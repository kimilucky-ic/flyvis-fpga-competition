// Ring records: release only after ARM has durably saved the contiguous prefix.
// One outstanding AXI4 INCR write, <=16 beats, 64-bit, no 4KiB crossing.
// Display/PC ACK never releases a slot. No overwrite of unreleased records.
// A record is published only after payload AND final header B responses OKAY.
module snapshot_axi_writer #(
    parameter integer N=45669, NE=1513231, INPUT_WORDS=721,
    parameter integer FIFO_DEPTH=64, BUS_TIMEOUT=65536
)(
    input logic clk, reset,
    input logic cfg_valid, output logic cfg_ready,
    input logic [31:0] cfg_base,cfg_end,cfg_first_frame,
    input logic [15:0] cfg_slots,
    input logic [31:0] cfg_cookie,release_sequence,release_cookie,
    input logic release_valid, output logic release_ready,
    output logic [31:0] released_count,
    input logic begin_valid, output logic begin_ready,
    output logic configured,active,capacity_exhausted,
    input logic input_valid, output logic input_ready, input logic [31:0] input_bits,
    input logic state_valid, output logic state_ready,
    input logic [15:0] state_id, input logic [31:0] state_bits, input logic state_last,
    input logic info_valid, input logic [31:0] info_cycles,info_edges,info_states,info_faults,
    output logic publish, output logic [31:0] published_base,published_frame,
    output logic [31:0] committed_count, output logic [7:0] error_flags,
    output logic [31:0] m_axi_awaddr, output logic [7:0] m_axi_awlen,
    output logic [2:0] m_axi_awsize, output logic [1:0] m_axi_awburst,
    output logic m_axi_awvalid, input logic m_axi_awready,
    output logic [63:0] m_axi_wdata, output logic [7:0] m_axi_wstrb,
    output logic m_axi_wlast,m_axi_wvalid, input logic m_axi_wready,
    input logic [1:0] m_axi_bresp, input logic m_axi_bvalid,output logic m_axi_bready
);
    localparam integer STATE_OFFSET=4096;
    localparam integer STRIDE=((STATE_OFFSET+4*N+4095)/4096)*4096;
    localparam integer IB=(INPUT_WORDS+1)/2, SB=(N+1)/2;
    localparam integer FW=$clog2(FIFO_DEPTH), TW=$clog2(BUS_TIMEOUT+1);
    localparam logic [2:0] IDLE=0,INPUTS=1,STATES=2,INFO=3,HEADER=4;
    localparam logic [1:0] AX_IDLE=0,AX_ADDR=1,AX_DATA=2,AX_RESP=3;
    logic [2:0] phase;
    logic [1:0] bus;
    logic [31:0] record_base,end_address,frame_id,acked_beats;
    logic [15:0] slots,write_slot;
    logic [31:0] ring_base,session_cookie;
    logic sequence_exhausted;
    logic [FW-1:0] wp,rp;
    logic [FW:0] count;
    (* ram_style="distributed" *) logic [63:0] fifo_data[0:FIFO_DEPTH-1];
    (* ram_style="distributed" *) logic [7:0] fifo_strb[0:FIFO_DEPTH-1];
    logic half;
    logic [31:0] low_word,input_count,state_count,input_hash,state_hash;
    logic [31:0] saved_cycles,saved_edges,saved_states,saved_faults;
    logic got_info;
    logic [4:0] burst_beats,beat;
    logic [TW-1:0] timeout_count;
    logic push,pop,accept_word,last_word;
    logic [31:0] word_bits;
    logic [63:0] push_data;
    logic [7:0] push_strb;
    logic capture_done;
    logic [32:0] next_end;

    assign next_end={1'b0,record_base}+STRIDE;
    assign cfg_ready=!configured&&!active&&(error_flags==0);
    assign capacity_exhausted=configured&&!active&&
        ((committed_count-released_count>=32'(slots))||sequence_exhausted||
         committed_count==32'hffffffff||next_end[32]||(next_end>{1'b0,end_address}));
    assign release_ready=configured&&(error_flags==0)&&release_cookie==session_cookie&&
        release_sequence>=released_count&&release_sequence<=committed_count;
    assign begin_ready=configured&&!active&&!capacity_exhausted&&(error_flags==0);
    assign input_ready=active&&phase==INPUTS&&input_count<INPUT_WORDS&&32'(count)<FIFO_DEPTH&&(error_flags==0);
    assign state_ready=active&&phase==STATES&&state_count<N&&32'(count)<FIFO_DEPTH&&(error_flags==0);
    assign accept_word=(input_valid&&input_ready)||(state_valid&&state_ready);
    assign word_bits=(phase==INPUTS)?input_bits:state_bits;
    assign last_word=(phase==INPUTS)?input_count==INPUT_WORDS-1:state_count==N-1;
    assign push=accept_word&&(half||last_word);
    assign push_data=half?{word_bits,low_word}:{32'b0,word_bits};
    assign push_strb=half?8'hff:8'h0f;
    assign pop=bus==AX_DATA&&m_axi_wready&&phase!=HEADER;
    assign capture_done=(phase==INPUTS)?input_count==INPUT_WORDS:state_count==N;

    // Header, little-endian 32-bit words: marker/version, frame/flags,
    // N/NE, input/state byte counts, cycles/edges, states/stride,
    // input/state rolling hashes, input/state offsets, then reserved words.
    function automatic logic [63:0] header_word(input logic [4:0] index);
        case(index)
            0:header_word={32'h00010000,32'h5331314c}; // "L11S", format1
            1:header_word={32'b0,frame_id};
            2:header_word={32'(NE),32'(N)};
            3:header_word={32'(4*N),32'(4*INPUT_WORDS)};
            4:header_word={saved_edges,saved_cycles};
            5:header_word={32'(STRIDE),saved_states};
            6:header_word={state_hash,input_hash};
            7:header_word={32'(STATE_OFFSET),32'd128};
            8:header_word={32'h3ba3d70a,32'h00110005}; // dt=.005, candidate ABI
            9:header_word={32'b0,saved_faults};
            10:header_word={session_cookie,committed_count+32'd1};
            default:header_word=0;
        endcase
    endfunction
    assign m_axi_awsize=3; assign m_axi_awburst=1;
    assign m_axi_awvalid=bus==AX_ADDR;
    assign m_axi_awlen=8'(burst_beats-1);
    assign m_axi_awaddr=record_base+((phase==INPUTS)?128:(phase==HEADER)?0:STATE_OFFSET)+8*acked_beats;
    assign m_axi_wvalid=bus==AX_DATA;
    assign m_axi_wdata=(phase==HEADER)?header_word(beat):fifo_data[rp];
    assign m_axi_wstrb=(phase==HEADER)?8'hff:fifo_strb[rp];
    assign m_axi_wlast=beat==burst_beats-1;
    assign m_axi_bready=bus==AX_RESP;

    always_ff @(posedge clk) begin
        if(reset) begin
            configured<=0;active<=0;phase<=IDLE;bus<=AX_IDLE;
            record_base<=0;end_address<=0;frame_id<=0;slots<=0;committed_count<=0;
            released_count<=0;write_slot<=0;ring_base<=0;session_cookie<=0;sequence_exhausted<=0;
            wp<=0;rp<=0;count<=0;half<=0;low_word<=0;acked_beats<=0;
            input_count<=0;state_count<=0;input_hash<=0;state_hash<=0;got_info<=0;
            saved_cycles<=0;saved_edges<=0;saved_states<=0;saved_faults<=0;
            error_flags<=0;publish<=0;published_base<=0;published_frame<=0;
            burst_beats<=0;beat<=0;timeout_count<=0;
        end else begin
            publish<=0;
            if(release_valid) begin
                if(release_ready) released_count<=release_sequence;
                else error_flags[5]<=1;
            end
            if(cfg_valid&&cfg_ready) begin
                if(cfg_base[11:0]!=0||cfg_end<=cfg_base||cfg_slots==0||
                   (64'(cfg_base)+64'(STRIDE)*64'(cfg_slots)>64'(cfg_end))||
                   ({1'b0,cfg_first_frame}+33'(cfg_slots)>33'h100000000)) error_flags[3]<=1;
                else begin
                    configured<=1;record_base<=cfg_base;end_address<=cfg_end;
                    ring_base<=cfg_base;session_cookie<=cfg_cookie;write_slot<=0;
                    frame_id<=cfg_first_frame;slots<=cfg_slots;
                end
            end
            if(begin_valid&&begin_ready) begin
                active<=1;phase<=INPUTS;input_count<=0;state_count<=0;
                half<=0;input_hash<=0;state_hash<=0;acked_beats<=0;got_info<=0;
            end
            if(accept_word) begin
                if(half||last_word) half<=0;
                else begin low_word<=word_bits;half<=1;end
                if(phase==INPUTS) begin
                    input_count<=input_count+1;
                    input_hash<={input_hash[30:0],input_hash[31]}^input_bits^input_count;
                end else begin
                    state_count<=state_count+1;
                    state_hash<={state_hash[30:0],state_hash[31]}^state_bits^state_count;
                    if(32'(state_id)!=state_count||state_last!=last_word) error_flags[0]<=1;
                end
            end
            if(push) begin fifo_data[wp]<=push_data;fifo_strb[wp]<=push_strb;wp<=wp+1'b1;end
            if(pop) rp<=rp+1'b1;
            case({push,pop})
                2'b10:count<=count+1'b1;
                2'b01:count<=count-1'b1;
                default:begin end
            endcase
            if(info_valid&&active) begin
                got_info<=1;saved_cycles<=info_cycles;saved_edges<=info_edges;
                saved_states<=info_states;saved_faults<=info_faults;
                if(info_edges!=NE||info_states!=N||info_faults!=0||got_info||
                   state_count!=N||input_count!=INPUT_WORDS) error_flags[4]<=1;
            end
            if(phase==INFO&&got_info&&error_flags==0) begin phase<=HEADER;acked_beats<=0;end

            // A timeout latches failure but does NOT withdraw an outstanding
            // AW/W VALID or truncate a burst. Drain the issued transaction,
            // publish nothing, accept no new input and require reconciliation.
            if(bus==AX_IDLE || (bus==AX_ADDR&&m_axi_awready) ||
               (bus==AX_DATA&&m_axi_wready) || (bus==AX_RESP&&m_axi_bvalid)) timeout_count<=0;
            else if(32'(timeout_count)<BUS_TIMEOUT) begin
                timeout_count<=timeout_count+1'b1;
                if(32'(timeout_count)==BUS_TIMEOUT-1) error_flags[2]<=1;
            end
            case(bus)
                AX_IDLE:if(active&&error_flags==0) begin
                    if(phase==HEADER) begin burst_beats<=16;beat<=0;bus<=AX_ADDR;end
                    else if((phase==INPUTS||phase==STATES)&&count!=0&&
                            (count>=16||capture_done)) begin
                        burst_beats<=(count>=16)?5'd16:5'(count);beat<=0;bus<=AX_ADDR;
                    end
                end
                AX_ADDR:if(m_axi_awready) bus<=AX_DATA;
                AX_DATA:if(m_axi_wready) begin
                    if(beat==burst_beats-1) bus<=AX_RESP;
                    else beat<=beat+1'b1;
                end
                AX_RESP:if(m_axi_bvalid) begin
                    bus<=AX_IDLE;
                    if(m_axi_bresp!=0) error_flags[1]<=1;
                    else if(error_flags==0) begin
                        if(phase==HEADER) begin
                            publish<=1;published_base<=record_base;published_frame<=frame_id;
                            committed_count<=committed_count+1'b1;
                            if(write_slot==slots-1) begin record_base<=ring_base;write_slot<=0;end
                            else begin record_base<=record_base+STRIDE;write_slot<=write_slot+1'b1;end
                            if(frame_id==32'hffffffff) sequence_exhausted<=1;
                            frame_id<=frame_id+1'b1;active<=0;phase<=IDLE;
                        end else if(acked_beats+32'(burst_beats)==((phase==INPUTS)?IB:SB)) begin
                            acked_beats<=0;half<=0;
                            phase<=(phase==INPUTS)?STATES:INFO;
                        end else acked_beats<=acked_beats+32'(burst_beats);
                    end
                end
            endcase
        end
    end
`ifndef SYNTHESIS
    initial begin
        if(FIFO_DEPTH<16||(FIFO_DEPTH&(FIFO_DEPTH-1))!=0) $fatal(1,"FIFO must be power of2 >=16");
        if(N>65535||INPUT_WORDS*4+128>STATE_OFFSET) $fatal(1,"Record shape unsupported");
    end
    always_ff @(posedge clk) if(!reset) begin
        if(released_count>committed_count||committed_count-released_count>32'(slots)) $fatal(1,"Ring ownership invariant");
        if(32'(count)>FIFO_DEPTH) $fatal(1,"FIFO overflow");
        if(pop&&count==0) $fatal(1,"FIFO underflow");
        if(m_axi_awvalid&&m_axi_awready&&(32'(m_axi_awaddr[11:0])+8*(32'(m_axi_awlen)+1)>4096)) $fatal(1,"AXI4KiB boundary");
    end
`endif
endmodule
