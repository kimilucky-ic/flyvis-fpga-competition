// Single-clock, synchronous one-read/one-write port. Read-first collision
// semantics; the lane forbids same-address collisions. No array reset.
module sync_mem #(parameter integer WIDTH=32,DEPTH=45669,AW=16,
    parameter INIT_FILE="", parameter SIM_KEY="")(
    input logic clk,reset,ce,re,we,input logic [AW-1:0] ra,wa,
    input logic [WIDTH-1:0] wd,output logic [WIDTH-1:0] q,
    output logic qvalid
);
    generate if(WIDTH==32&&DEPTH==45669&&AW==16) begin: wide_banked
        banked_state_mem #(.INIT_FILE(INIT_FILE)) storage(.clk,.reset,.ce,.re,.we,.ra,.wa,.wd,.q,.qvalid);
`ifndef SYNTHESIS
        always_ff @(posedge clk) if(!reset&&ce) begin
            if(re&&int'(ra)>=DEPTH) $fatal(1,"banked read bounds");
            if(we&&int'(wa)>=DEPTH) $fatal(1,"banked write bounds");
        end
`endif
    end else begin: ordinary
    (* ram_style="block" *) logic [WIDTH-1:0] mem[0:DEPTH-1];
    // Constant file is FPGA-ROM/RAM initialization coding style; mapping unproven.
    initial if(INIT_FILE!="") $readmemh(INIT_FILE,mem);
`ifndef SYNTHESIS
    string path;
    initial if(SIM_KEY!="") begin
        if(!$value$plusargs({SIM_KEY,"=%s"},path)) $fatal(1,"missing memory image %s",SIM_KEY);
        $readmemh(path,mem);
    end
    always_ff @(posedge clk) if(!reset&&ce) begin
        if(re&&int'(ra)>=DEPTH) $fatal(1,"sync read bounds");
        if(we&&int'(wa)>=DEPTH) $fatal(1,"sync write bounds");
    end
`endif
    always_ff @(posedge clk) begin
        if(reset) qvalid<=0;
        else if(ce) begin
            qvalid<=re;
            if(re) q<=mem[ra];
            if(we) mem[wa]<=wd;
        end
    end
    end endgenerate
endmodule
