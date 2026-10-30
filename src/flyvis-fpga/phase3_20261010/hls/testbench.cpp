#include <ap_int.h>

#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>

#include "flyvis_t5c_constants_q22.hpp"

#ifndef FLYVIS_TEST_DATA_DIR
#define FLYVIS_TEST_DATA_DIR "testdata_q22"
#endif
#ifndef FLYVIS_TEST_LABEL
#define FLYVIS_TEST_LABEL "G2"
#endif

static const int INPUT_WORDS = FLYVIS_BOUNDARY_COUNT + 2 * FLYVIS_H_COUNT;
static const int REPLAY_REQUESTS = 800;
static const int TOTAL_REQUESTS = REPLAY_REQUESTS + 1;  // final request is a changed-boundary negative control

ap_uint<32> flyvis_t5c_source_raw(const ap_int<32> request[INPUT_WORDS],
                                 ap_int<32> result[FLYVIS_H_COUNT]);

static std::string data_path(const char *leaf) {
    std::string source = __FILE__;
    const std::string::size_type slash = source.find_last_of("/\\");
    const std::string directory = slash == std::string::npos ? "." : source.substr(0, slash);
    return directory + "/../" + FLYVIS_TEST_DATA_DIR + "/" + leaf;
}

int main() {
    std::ifstream request_file(data_path("requests_i32le.bin").c_str(), std::ios::binary);
    std::ifstream expected_file(data_path("expected_i32le.bin").c_str(), std::ios::binary);
    if (!request_file || !expected_file) {
        std::cerr << "FAIL: cannot open fixed-point vector files relative to testbench source\n";
        return 1;
    }

    ap_int<32> request[INPUT_WORDS];
    ap_int<32> result[FLYVIS_H_COUNT];
    int32_t raw_word = 0;
    int32_t expected_word = 0;
    int32_t baseline[FLYVIS_H_COUNT] = {};
    ap_int<32> baseline_request[INPUT_WORDS];
    int baseline_echo_mismatches = 0;
    int baseline_zero_mismatches = 0;
    int boundary_perturb_mismatches = 0;

    for (int request_id = 0; request_id < TOTAL_REQUESTS; ++request_id) {
        for (int i = 0; i < INPUT_WORDS; ++i) {
            if (!request_file.read(reinterpret_cast<char *>(&raw_word), sizeof(raw_word))) {
                std::cerr << "FAIL: truncated request vector at request " << request_id << " word " << i << "\n";
                return 2;
            }
            request[i] = raw_word;
            if (request_id == 0) baseline_request[i] = raw_word;
        }

        const ap_uint<32> status = flyvis_t5c_source_raw(request, result);
        if (status != 0) {
            std::cerr << "FAIL: nonzero hardware status at request " << request_id
                      << ": 0x" << std::hex << status.to_uint() << std::dec << "\n";
            return 3;
        }

        for (int h = 0; h < FLYVIS_H_COUNT; ++h) {
            if (!expected_file.read(reinterpret_cast<char *>(&expected_word), sizeof(expected_word))) {
                std::cerr << "FAIL: truncated expected vector at request " << request_id << " H " << h << "\n";
                return 4;
            }
            const int32_t actual = result[h].to_int();
            if (actual != expected_word) {
                std::cerr << "FAIL: bit-true mismatch request=" << request_id << " H=" << h
                          << " expected=" << expected_word << " actual=" << actual << "\n";
                return 5;
            }
            if (request_id == 0) {
                baseline[h] = actual;
                if (actual != request[FLYVIS_BOUNDARY_COUNT + h].to_int()) {
                    ++baseline_echo_mismatches;
                }
                if (actual != 0) {
                    ++baseline_zero_mismatches;
                }
            }
            if (request_id == REPLAY_REQUESTS && actual != baseline[h]) {
                ++boundary_perturb_mismatches;
            }
        }

        if (request_id == 0) {
            std::cout << "PASS: 1 " << FLYVIS_TEST_LABEL << " SOURCE_RAW stateless H request, exact Q6.22 oracle match\n";
        } else if (request_id == 31) {
            std::cout << "PASS: 32 " << FLYVIS_TEST_LABEL << " SOURCE_RAW stateless H requests, exact Q6.22 oracle match\n";
        } else if (request_id == REPLAY_REQUESTS - 1) {
            std::cout << "PASS: 800 " << FLYVIS_TEST_LABEL << " SOURCE_RAW stateless H requests, exact Q6.22 oracle match\n";
        }
    }

    char trailing = 0;
    if (request_file.read(&trailing, 1) || expected_file.read(&trailing, 1)) {
        std::cerr << "FAIL: fixture files have unexpected trailing data\n";
        return 6;
    }
    if (baseline_echo_mismatches == 0 || baseline_zero_mismatches == 0) {
        std::cerr << "FAIL: a fixed echo/zero-output negative control was not rejected\n";
        return 7;
    }
    if (boundary_perturb_mismatches == 0) {
        std::cerr << "FAIL: changing a real RH boundary input did not change the H output\n";
        return 8;
    }

    std::cout << "PASS: echo and fixed-zero negative controls rejected by vector comparison\n";
    std::cout << "PASS: +0.25 boundary perturbation changed " << boundary_perturb_mismatches
              << " of 67 H outputs\n";
    for (int mode = 1; mode <= 2; ++mode) {
        for (int i = 0; i < INPUT_WORDS; ++i) request[i] = baseline_request[i];
        if (mode == 1) request[0] = 0x40000000; // invalid Q29 sign extension
        else request[FLYVIS_BOUNDARY_COUNT + FLYVIS_H_COUNT] = 0x0fffffff;
        const ap_uint<32> status = flyvis_t5c_source_raw(request, result);
        const unsigned expected_status = mode == 1 ? 1 : 4;
        if (status.to_uint() != expected_status) {
            std::cerr << "FAIL: failure control status=" << status.to_uint() << " expected=" << expected_status << "\n";
            return 9;
        }
        for (int h = 0; h < FLYVIS_H_COUNT; ++h) {
            if (result[h] != 0) { std::cerr << "FAIL: failed request exposed a candidate\n"; return 10; }
        }
        std::cout << "PASS: fail-closed control mode=" << mode << " status=" << status.to_uint() << "\n";
    }
    std::cout << "PASS: total 801 valid requests (800 " << FLYVIS_TEST_LABEL << " replay + 1 boundary control), plus 2 failure controls\n";
    return 0;
}
