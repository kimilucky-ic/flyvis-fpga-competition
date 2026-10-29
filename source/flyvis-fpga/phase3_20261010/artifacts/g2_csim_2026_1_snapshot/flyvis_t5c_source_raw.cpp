#include <ap_int.h>

#include "flyvis_t5c_constants_q22.hpp"

namespace {
static const int STATE_W = 29;
static const int WEIGHT_W = 22;
static const int ACC_W = 48;
static const int INPUT_WORDS = FLYVIS_BOUNDARY_COUNT + 2 * FLYVIS_H_COUNT;

template <int IN_W, int SHIFT>
ap_int<IN_W + 1> round_shift_symmetric(ap_int<IN_W> value) {
#pragma HLS INLINE
    ap_int<IN_W + 1> extended = value;
    ap_uint<IN_W + 1> magnitude = 0;
    if (extended < 0) {
        magnitude = ap_uint<IN_W + 1>(-extended);
    } else {
        magnitude = ap_uint<IN_W + 1>(extended);
    }
    ap_uint<IN_W + 1> rounding = 0;
    rounding[SHIFT - 1] = 1;
    ap_uint<IN_W + 1> rounded_magnitude = (magnitude + rounding) >> SHIFT;
    ap_int<IN_W + 1> result = 0;
    if (extended < 0) {
        result = -ap_int<IN_W + 1>(rounded_magnitude);
    } else {
        result = ap_int<IN_W + 1>(rounded_magnitude);
    }
    return result;
}

template <int OUT_W, int IN_W>
bool fits_signed(ap_int<IN_W> value) {
#pragma HLS INLINE
    ap_int<OUT_W> narrowed = value;
    ap_int<IN_W> restored = narrowed;
    return restored == value;
}
}  // namespace

// One stateless SOURCE_RAW H.step. The request contains 1364 source activities,
// followed by old_H[67] and x_H[67], all signed Q6.22 in 32-bit host words.
// The PL computes every HH/RH edge in global edge-ID order and returns only
// an uncommitted new_H candidate. The host/coordinator owns COMMIT.
ap_uint<32> flyvis_t5c_source_raw(const ap_int<32> request[INPUT_WORDS],
                                 ap_int<32> result[FLYVIS_H_COUNT]) {
#pragma HLS INTERFACE m_axi port=request offset=slave bundle=gmem0 depth=INPUT_WORDS max_read_burst_length=64
#pragma HLS INTERFACE m_axi port=result offset=slave bundle=gmem0 depth=FLYVIS_H_COUNT max_write_burst_length=64
#pragma HLS INTERFACE s_axilite port=request bundle=control
#pragma HLS INTERFACE s_axilite port=result bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control

    ap_uint<32> status = 0;
    ap_int<29> boundary[FLYVIS_BOUNDARY_COUNT];
    ap_int<29> old_h[FLYVIS_H_COUNT];
    ap_int<29> x_h[FLYVIS_H_COUNT];
    ap_int<48> chemical[FLYVIS_H_COUNT];
    ap_int<29> candidate[FLYVIS_H_COUNT];
#pragma HLS BIND_STORAGE variable=boundary type=ram_1p impl=bram
#pragma HLS ARRAY_PARTITION variable=old_h complete
#pragma HLS ARRAY_PARTITION variable=x_h complete
#pragma HLS ARRAY_PARTITION variable=chemical complete
#pragma HLS ARRAY_PARTITION variable=candidate complete

    // Reject non-sign-extended host words before any result can be committed.
    for (int i = 0; i < INPUT_WORDS; ++i) {
#pragma HLS PIPELINE II=1
        ap_int<32> raw = request[i];
        ap_uint<3> upper = raw.range(31, 29);
        ap_uint<3> expected_upper = raw[28] ? ap_uint<3>(7) : ap_uint<3>(0);
        if (upper != expected_upper) {
            status[0] = 1;
        }
        ap_int<29> q = raw.range(28, 0);
        if (i < FLYVIS_BOUNDARY_COUNT) {
            boundary[i] = q;
        } else if (i < FLYVIS_BOUNDARY_COUNT + FLYVIS_H_COUNT) {
            old_h[i - FLYVIS_BOUNDARY_COUNT] = q;
        } else {
            x_h[i - FLYVIS_BOUNDARY_COUNT - FLYVIS_H_COUNT] = q;
        }
    }

    for (int h = 0; h < FLYVIS_H_COUNT; ++h) {
#pragma HLS PIPELINE II=1
        chemical[h] = 0;
        candidate[h] = 0;
    }

    if (status == 0) {
        // Static edge ROMs are traversed in strict ascending original edge ID.
        for (int e = 0; e < FLYVIS_EDGE_COUNT; ++e) {
#pragma HLS PIPELINE II=1
            ap_uint<12> src_code = FLYVIS_EDGE_SRC[e];
            ap_uint<11> src_index = src_code.range(10, 0);
            ap_int<29> source_activity = 0;
            if (src_code[11]) {
                source_activity = old_h[src_index];
            } else {
                source_activity = boundary[src_index];
            }
            if (source_activity < 0) {
                source_activity = 0;
            }

            ap_int<22> weight = FLYVIS_EDGE_WEIGHT_Q20[e];
            ap_int<51> product = source_activity * weight;
            ap_int<52> term_wide = round_shift_symmetric<51, FLYVIS_WEIGHT_FRAC>(product);
            ap_int<29> term = term_wide;
            if (!fits_signed<29>(term_wide)) {
                status[2] = 1;
            }

            ap_uint<7> target = FLYVIS_EDGE_DST[e];
            ap_int<49> sum = ap_int<49>(chemical[target]) + ap_int<49>(term);
            if (!fits_signed<48>(sum)) {
                status[1] = 1;
            }
            chemical[target] = sum.range(47, 0);
        }

        if (status == 0) {
            for (int h = 0; h < FLYVIS_H_COUNT; ++h) {
#pragma HLS PIPELINE II=1
                ap_int<29> chemical_q = chemical[h];
                if (!fits_signed<29>(chemical[h])) {
                    status[2] = 1;
                }

                // Preserve the software operation grouping:
                // inv_tau * (((-old_H + bias) + chemical) + x_H).
                ap_int<31> drive = -ap_int<31>(old_h[h])
                                  + ap_int<31>(FLYVIS_BIAS_Q22[h])
                                  + ap_int<31>(chemical_q)
                                  + ap_int<31>(x_h[h]);
                ap_int<60> velocity_product = ap_int<29>(FLYVIS_INVTau_Q22[h]) * drive;
                ap_int<61> velocity_wide = round_shift_symmetric<60, FLYVIS_STATE_FRAC>(velocity_product);
                ap_int<29> velocity = velocity_wide;
                if (!fits_signed<29>(velocity_wide)) {
                    status[2] = 1;
                }

                ap_int<58> delta_product = velocity * ap_int<29>(FLYVIS_DT_Q22);
                ap_int<59> delta_wide = round_shift_symmetric<58, FLYVIS_STATE_FRAC>(delta_product);
                ap_int<29> delta = delta_wide;
                if (!fits_signed<29>(delta_wide)) {
                    status[2] = 1;
                }

                ap_int<30> new_wide = ap_int<30>(old_h[h]) + ap_int<30>(delta);
                if (!fits_signed<29>(new_wide)) {
                    status[2] = 1;
                }
                candidate[h] = new_wide.range(28, 0);
            }
        }
    }

    // Fail closed: any malformed word or arithmetic overflow discards all H.
    for (int h = 0; h < FLYVIS_H_COUNT; ++h) {
#pragma HLS PIPELINE II=1
        if (status == 0) {
            result[h] = ap_int<32>(candidate[h]);
        } else {
            result[h] = 0;
        }
    }
    return status;
}
