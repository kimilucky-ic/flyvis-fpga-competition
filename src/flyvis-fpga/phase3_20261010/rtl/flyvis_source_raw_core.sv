`timescale 1ns/1ps
// Stateless FlyVis SOURCE_RAW arithmetic. The PL consumes raw boundary/old_H/x_H
// and computes all ordered HH/RH edges plus Euler updates. No host chemical input.
module flyvis_source_raw_core #(
    parameter integer H_COUNT = 67,
    parameter integer B_COUNT = 1364,
    parameter integer EDGE_COUNT = 6537,
    parameter EDGE_FILE = "rom/edges_q22.mem",
    parameter NEURON_FILE = "rom/neurons_q22.mem"
) (
    input wire clk, input wire rst_n,
    input wire req_begin,
    input wire in_we,
    input wire [$clog2(B_COUNT+2*H_COUNT)-1:0] in_addr,
    input wire signed [31:0] in_data,
    input wire start,
    output wire busy,
    output reg done,
    output reg out_valid,
    output reg [31:0] status,
    output reg [31:0] compute_cycles,
    input wire [$clog2(H_COUNT)-1:0] out_addr,
    output wire signed [31:0] out_data
);
    localparam integer INPUT_WORDS = B_COUNT + 2*H_COUNT;
    localparam integer INPUT_AW = $clog2(INPUT_WORDS);
    localparam integer H_AW = $clog2(H_COUNT);
    localparam integer E_AW = $clog2(EDGE_COUNT);
    localparam integer SRC_INDEX_W = $clog2((B_COUNT > H_COUNT) ? B_COUNT : H_COUNT);
    localparam integer SRC_W = SRC_INDEX_W + 1;
    localparam integer META_W = SRC_W + H_AW + 22;
    localparam [3:0] IDLE=0, LOAD=1, CLEAR=2, E_META=3, E_SOURCE=4,
        E_MUL=5, E_ACC=6, N_READ=7, N_DRIVE=8, N_VMUL=9,
        N_VROUND=10, N_DMUL=11, N_NEW=12, FINISH=13, ERROR=14;
    reg [3:0] state;
    reg [INPUT_AW:0] loaded;
    reg [H_AW-1:0] h_index;
    reg [E_AW-1:0] e_index;
    (* ram_style="block" *) reg signed [28:0] request_mem [0:INPUT_WORDS-1];
    (* rom_style="block" *) reg [META_W-1:0] edge_rom [0:EDGE_COUNT-1];
    (* rom_style="block" *) reg [57:0] neuron_rom [0:H_COUNT-1];
    reg signed [47:0] chemical [0:H_COUNT-1];
    reg signed [28:0] candidate [0:H_COUNT-1];
    reg [META_W-1:0] meta;
    wire [SRC_W-1:0] source_code = meta[META_W-1:22+H_AW];
    wire [SRC_INDEX_W-1:0] source_index = source_code[SRC_INDEX_W-1:0];
    wire [H_AW-1:0] target = meta[22+H_AW-1:22];
    wire signed [21:0] weight = meta[21:0];
    reg signed [28:0] source_activity, old_h, x_h, bias, inv_tau, velocity;
    reg signed [47:0] chemical_read;
    reg signed [30:0] drive;
    reg signed [59:0] product;
    reg signed [30:0] mul_a;
    reg signed [28:0] mul_b;

    initial begin
        $readmemh(EDGE_FILE, edge_rom);
        $readmemh(NEURON_FILE, neuron_rom);
    end

    function automatic signed [63:0] round_nearest_away;
        input signed [63:0] value;
        input integer shift;
        reg signed [63:0] half;
        begin
            half = 64'sd1 <<< (shift-1);
            if (value < 0) round_nearest_away = -(((-value)+half) >>> shift);
            else round_nearest_away = (value+half) >>> shift;
        end
    endfunction
    function automatic fits29;
        input signed [63:0] value;
        begin fits29 = (value[63:29] == {35{value[28]}}); end
    endfunction
    wire signed [63:0] rounded_edge = round_nearest_away({{4{product[59]}},product},20);
    wire signed [63:0] rounded_state = round_nearest_away({{4{product[59]}},product},22);
    wire signed [48:0] edge_sum = $signed({chemical[target][47],chemical[target]})
        + $signed({{20{rounded_edge[28]}},rounded_edge[28:0]});
    wire signed [29:0] new_sum = $signed({old_h[28],old_h})
        + $signed({rounded_state[28],rounded_state[28:0]});

    // One explicitly shared 31x29 multiplier, independent of edge/neuron count.
    always @* begin
        mul_a = 0; mul_b = 0;
        case (state)
            E_MUL: begin
                mul_a = source_activity[28] ? 31'sd0 : $signed({{2{source_activity[28]}},source_activity});
                mul_b = $signed({{7{weight[21]}},weight});
            end
            N_VMUL: begin mul_a = drive; mul_b = inv_tau; end
            N_DMUL: begin mul_a = $signed({{2{velocity[28]}},velocity}); mul_b = 29'sd20972; end
            default: begin end
        endcase
    end
    assign busy = (state != IDLE);
    assign out_data = (out_valid && status == 0 && out_addr < H_COUNT)
        ? $signed({{3{candidate[out_addr][28]}},candidate[out_addr]}) : 32'sd0;

    always @(posedge clk) begin
        if (!rst_n) begin
            state <= IDLE; loaded <= 0; h_index <= 0; e_index <= 0;
            done <= 0; out_valid <= 0; status <= 0; compute_cycles <= 0;
        end else begin
            done <= 0;
            if (state != IDLE && state != LOAD) compute_cycles <= compute_cycles + 1;
            if (req_begin) begin
                if (state == IDLE) begin
                    state <= LOAD; loaded <= 0; status <= 0;
                    out_valid <= 0; compute_cycles <= 0;
                end else begin status[3] <= 1; out_valid <= 0; state <= ERROR; end
            end else if ((in_we && state != LOAD) || (start && state != LOAD)) begin
                status[3] <= 1; out_valid <= 0; state <= ERROR;
            end else case (state)
                IDLE: begin end
                LOAD: begin
                    if (in_we) begin
                        if (loaded >= INPUT_WORDS || in_addr != loaded) status[3] <= 1;
                        else begin
                            request_mem[in_addr] <= in_data[28:0];
                            loaded <= loaded + 1;
                            if (in_data[31:29] != {3{in_data[28]}}) status[0] <= 1;
                        end
                    end
                    if (start) begin
                        if (loaded == INPUT_WORDS && status == 0 && !in_we) begin
                            h_index <= 0; e_index <= 0; compute_cycles <= 0; state <= CLEAR;
                        end else begin
                            if (loaded != INPUT_WORDS || in_we) status[3] <= 1;
                            state <= ERROR;
                        end
                    end
                end
                CLEAR: begin
                    chemical[h_index] <= 0;
                    if (h_index == H_COUNT-1) begin h_index <= 0; state <= E_META; end
                    else h_index <= h_index + 1;
                end
                E_META: begin meta <= edge_rom[e_index]; state <= E_SOURCE; end
                E_SOURCE: begin
                    source_activity <= request_mem[source_code[SRC_INDEX_W] ? B_COUNT+source_index : source_index];
                    state <= E_MUL;
                end
                E_MUL: begin product <= mul_a * mul_b; state <= E_ACC; end
                E_ACC: begin
                    if (!fits29(rounded_edge)) begin status[2] <= 1; state <= ERROR; end
                    else if (edge_sum[48] != edge_sum[47]) begin status[1] <= 1; state <= ERROR; end
                    else begin
                        chemical[target] <= edge_sum[47:0];
                        if (e_index == EDGE_COUNT-1) begin h_index <= 0; state <= N_READ; end
                        else begin e_index <= e_index+1; state <= E_META; end
                    end
                end
                N_READ: begin
                    old_h <= request_mem[B_COUNT+h_index];
                    x_h <= request_mem[B_COUNT+H_COUNT+h_index];
                    bias <= neuron_rom[h_index][28:0]; inv_tau <= neuron_rom[h_index][57:29];
                    chemical_read <= chemical[h_index]; state <= N_DRIVE;
                end
                N_DRIVE: begin
                    if (chemical_read[47:29] != {19{chemical_read[28]}}) begin status[2] <= 1; state <= ERROR; end
                    else begin
                        drive <= -$signed({{2{old_h[28]}},old_h}) + $signed({{2{bias[28]}},bias})
                            + $signed({{2{chemical_read[28]}},chemical_read[28:0]}) + $signed({{2{x_h[28]}},x_h});
                        state <= N_VMUL;
                    end
                end
                N_VMUL: begin product <= mul_a*mul_b; state <= N_VROUND; end
                N_VROUND: begin
                    if (!fits29(rounded_state)) begin status[2] <= 1; state <= ERROR; end
                    else begin velocity <= rounded_state[28:0]; state <= N_DMUL; end
                end
                N_DMUL: begin product <= mul_a*mul_b; state <= N_NEW; end
                N_NEW: begin
                    if (!fits29(rounded_state) || new_sum[29] != new_sum[28]) begin status[2] <= 1; state <= ERROR; end
                    else begin
                        candidate[h_index] <= new_sum[28:0];
                        if (h_index == H_COUNT-1) state <= FINISH;
                        else begin h_index <= h_index+1; state <= N_READ; end
                    end
                end
                FINISH: begin done <= 1; out_valid <= 1; state <= IDLE; end
                ERROR: begin done <= 1; out_valid <= 0; state <= IDLE; end
                default: begin status[3] <= 1; out_valid <= 0; state <= ERROR; end
            endcase
        end
    end
endmodule
