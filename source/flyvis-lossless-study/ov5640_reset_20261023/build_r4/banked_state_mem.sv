// Fixed-width banks, synchronous read-first, one cycle, common CE hold.
module banked_state_mem #(parameter INIT_FILE="")(
    input logic clk,reset,ce,re,we,input logic [15:0] ra,wa,
    input logic [31:0] wd,output logic [31:0] q,output logic qvalid
);
    function automatic string bank_file(input integer b);
        case(b)
            0: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_00.hex";
            1: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_01.hex";
            2: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_02.hex";
            3: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_03.hex";
            4: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_04.hex";
            5: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_05.hex";
            6: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_06.hex";
            7: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_07.hex";
            8: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_08.hex";
            9: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_09.hex";
            10: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_10.hex";
            11: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_11.hex";
            12: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_12.hex";
            13: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_13.hex";
            14: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_14.hex";
            15: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_15.hex";
            16: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_16.hex";
            17: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_17.hex";
            18: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_18.hex";
            19: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_19.hex";
            20: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_20.hex";
            21: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_21.hex";
            22: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_22.hex";
            23: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_23.hex";
            24: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_24.hex";
            25: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_25.hex";
            26: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_26.hex";
            27: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_27.hex";
            28: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_28.hex";
            29: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_29.hex";
            30: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_30.hex";
            31: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_31.hex";
            32: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_32.hex";
            33: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_33.hex";
            34: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_34.hex";
            35: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_35.hex";
            36: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_36.hex";
            37: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_37.hex";
            38: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_38.hex";
            39: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_39.hex";
            40: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_40.hex";
            41: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_41.hex";
            42: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_42.hex";
            43: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_43.hex";
            44: bank_file="C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_44.hex";
            default:bank_file="";
        endcase
    endfunction
    logic [5:0] selected;
    wire [31:0] bank_q[0:44];
    for(genvar b=0;b<45;b=b+1) begin: banks
        localparam IMAGE=(INIT_FILE=="")?"":bank_file(b);
        (* ram_style="block" *) logic [31:0] mem[0:1023];
        logic [31:0] data;
        initial if(IMAGE!="") $readmemh(IMAGE,mem);
        always_ff @(posedge clk) if(!reset&&ce) begin
            if(re&&ra[15:10]==b) data<=mem[ra[9:0]];
            if(we&&wa[15:10]==b) mem[wa[9:0]]<=wd;
        end
        assign bank_q[b]=data;
    end
    assign q=bank_q[selected];
    always_ff @(posedge clk) begin
        if(reset) qvalid<=0;
        else if(ce) begin qvalid<=re;if(re) selected<=ra[15:10];end
    end
endmodule
