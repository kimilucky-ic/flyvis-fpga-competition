`timescale 1ns / 1ps
module ps7_clock_reset_helper (
    input wire clk,
    input wire ext_resetn,
    output wire peripheral_resetn
);
    reg [3:0] reset_pipe = 4'b0000;
    always @(posedge clk or negedge ext_resetn) begin
        if (!ext_resetn)
            reset_pipe <= 4'b0000;
        else
            reset_pipe <= {reset_pipe[2:0], 1'b1};
    end
    assign peripheral_resetn = reset_pipe[3];
endmodule
