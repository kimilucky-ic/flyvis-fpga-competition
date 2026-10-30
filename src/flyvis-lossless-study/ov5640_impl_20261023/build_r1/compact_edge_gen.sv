// Compact-template edge generator. No expanded edge list is visible to this module.
module compact_edge_gen #(
    parameter integer NR = 605,
    parameter integer NE = 1513231, parameter MAP_FILE="", ROWS_FILE=""
)(
    input logic clk, reset, start,
    output logic rom_en, output logic [12:0] rom_addr, input logic [31:0] rom_q,
    output logic valid, input logic ready,
    output logic [15:0] src, dst, output logic [31:0] weight,
    output logic [20:0] eid, output logic done,
    output logic map_read, output logic [10:0] map_address
);
    localparam integer IDLE=0,RQ=1,RG=2,SQ=3,SG=4,TQ=5,TG=6,
        OQ=7,OG=8,ROWQ=9,ROWG=10,MQ=11,MG=12,FIN=13,ROWC=14;
    logic [3:0] state;
    logic [9:0] rule_id,rank_first;
    logic [1:0] word_id,sv,tv,j_step,descriptor_step;
    logic [11:0] offset_id,offset_end;
    logic [4:0] u,u_last,j,row_count,query_j;
    logic [3:0] vfirst;
    logic sl,tl;
    logic [15:0] sbase,tbase;
    logic signed [3:0] du,dv;
    logic signed [6:0] ut;
    logic signed [7:0] vt;
    logic [20:0] next_eid;
    logic [31:0] offset_weight;
    logic advance;
    logic [31:0] r[0:3],sn[0:3],tn[0:3],geom;
    logic [31:0] row_q;
    logic [15:0] map_q;
    logic in_bounds, bounds_q;
    logic row_read,last_candidate,descriptor_query,descriptor_valid;
    logic [4:0] descriptor_u,first_j,end_j;
    logic [5:0] lower_j,upper_j,rows_addr,target_rows_addr,prefetch_u;
    logic signed [7:0] base_v,lower_delta,upper_delta,target_read_u;
    logic [7:0] target_last_v;
    logic [31:0] target_row_q;
    logic row_pending,desc_ready,desc_nonempty;
    logic [4:0] row_tag,desc_tag,desc_first,desc_end;
    logic [1:0] desc_step;
    logic [3:0] desc_vfirst;
    logic [9:0] desc_rank;
    sync_mem #(.WIDTH(16),.DEPTH(1922),.AW(11),.INIT_FILE(MAP_FILE),.SIM_KEY("MAP")) maps(
        .clk,.reset,.ce(advance),.re(map_read),.ra(map_address),.we(1'b0),.wa(11'b0),.wd(16'b0),.q(map_q),.qvalid());
    sync_mem #(.DEPTH(62),.AW(6),.INIT_FILE(ROWS_FILE),.SIM_KEY("ROWS")) rows(
        .clk,.reset,.ce(advance),.re(row_read),.ra(rows_addr),.we(1'b0),.wa(6'b0),.wd(32'b0),.q(row_q),.qvalid());
    // Parallel descriptor read from the SAME immutable 62-word image. This
    // duplicates a tiny row ROM, not the expanded graph or neural arithmetic.
    sync_mem #(.DEPTH(62),.AW(6),.INIT_FILE(ROWS_FILE),.SIM_KEY("ROWS")) target_rows(
        .clk,.reset,.ce(advance),.re(row_read),.ra(target_rows_addr),.we(1'b0),.wa(6'b0),.wd(32'b0),.q(target_row_q),.qvalid());
    always_comb begin
        rom_en=0;rom_addr=0;
        case(state)
            RQ: begin rom_en=1;rom_addr=13'(292+4*rule_id+word_id);end
            SQ: begin rom_en=1;rom_addr=13'(32+4*int'(r[0][7:0])+word_id);end
            TQ: begin rom_en=1;rom_addr=13'(32+4*int'(r[0][15:8])+word_id);end
            OQ: begin rom_en=1;rom_addr=13'(2712+2*offset_id+word_id);end
            default: begin end
        endcase
        advance=!valid||ready;
        last_candidate=({1'b0,j}+{4'b0,j_step}>={1'b0,row_count});
        // The row RAM holds the following row throughout an active row. Read
        // the row after that while issuing the following row's first lookup.
        // All requests and their tags freeze with the elastic output slot.
        row_read=advance&&((state==ROWQ)||(state==ROWG&&u<u_last)||
            (state==MG&&last_candidate&&desc_ready&&u+1<u_last));
        prefetch_u={1'b0,u};
        if(state==ROWG)prefetch_u={1'b0,u}+6'd1;
        if(state==MG)prefetch_u={1'b0,u}+6'd2;
        rows_addr=6'(sl*31+prefetch_u);
        target_read_u={2'b0,prefetch_u}+{{4{du[3]}},du};
        target_rows_addr=6'(tl*31+target_read_u);
        descriptor_u=desc_tag;
        // Intersect the translated source row with the occupied target row.
        // Each image row is one arithmetic progression, proved independently
        // against all 1,922 map cells. Current profile v strides are 1 or 2.
        base_v={4'b0,row_q[3:0]}+{{4{dv[3]}},dv};
        target_last_v={4'b0,target_row_q[3:0]};
        if(target_row_q[12:8]!=0)
            target_last_v=target_last_v+(({3'b0,target_row_q[12:8]}-8'd1)*{6'b0,tv});
        lower_delta={4'b0,target_row_q[3:0]}-base_v;
        upper_delta=target_last_v-base_v;
        lower_j=0;
        if(lower_delta>0)begin
            if(sv==2)lower_j=6'((8'(lower_delta)+8'd1)>>1);
            else lower_j=6'(lower_delta);
        end
        // An odd source stride visits alternating target parity when tv=2.
        // Align the first candidate, then jump j by two without reordering.
        descriptor_step=(tv==2&&sv==1)?2'd2:2'd1;
        if(tv==2&&sv==1&&(base_v[0]^lower_j[0]^target_row_q[0]))lower_j=lower_j+6'd1;
        upper_j=0;
        if(upper_delta>=0)upper_j=(sv==2)?6'((8'(upper_delta)>>1)+8'd1):6'(8'(upper_delta)+8'd1);
        first_j=5'(lower_j);
        end_j=(upper_j<{1'b0,row_q[12:8]})?5'(upper_j):row_q[12:8];
        descriptor_valid=(target_row_q[12:8]!=0)&&(first_j<end_j)&&
            !(tv==2&&sv==2&&(base_v[0]^target_row_q[0]));
        descriptor_query=(state==ROWG)||(state==MG&&last_candidate&&u<u_last&&desc_ready);
        // Prime directly from a descriptor, or overlap the next column with
        // the current response. Row boundaries need no separate MQ cycle.
        query_j=j+{3'b0,j_step};
        ut={2'b0,u}+{{3{du[3]}},du};
        if(descriptor_query)begin query_j=desc_first;ut={2'b0,descriptor_u}+{{3{du[3]}},du};end
        // Explicit 8-bit two's-complement addition. The checked range is
        // [-8,115], so no overflow occurs; unsigned query/stride stay positive.
        vt={4'b0,vfirst}+({3'b0,query_j}*{6'b0,sv})+{{4{dv[3]}},dv};
        if(descriptor_query)vt={4'b0,desc_vfirst}+({3'b0,query_j}*{6'b0,sv})+{{4{dv[3]}},dv};
        in_bounds=ut>=0 && ut<31 && vt>=0 && vt<31 && (!descriptor_query||desc_nonempty);
        rom_en=rom_en&&advance;
        map_read=(descriptor_query||(state==MG&&!last_candidate))&&in_bounds&&advance;
        map_address=(tl?11'd961:11'd0)+11'($signed(ut)*31)+11'($signed(vt));
        done=(state==FIN)&&!valid;
    end
    always_ff @(posedge clk) begin
        // synthesis translate_off
        if(!reset&&row_read&&(rows_addr>=62||target_rows_addr>=62||target_read_u<0||target_read_u>30))
            $fatal(1,"prefetched source/target row address out of range");
        // synthesis translate_on
        if(reset) begin state<=IDLE;eid<=0;next_eid<=0;valid<=0;rule_id<=0;word_id<=0;weight<=0;row_pending<=0;desc_ready<=0;end
        else if(advance) begin
        valid<=0;
        // Register clipping/parity before the map-address path. The following
        // row is normally ready during the current row. One-candidate rows
        // use ROWG as a bounded fallback rather than consuming a stale tag.
        row_pending<=row_read;
        if(row_read)row_tag<=prefetch_u[4:0];
        if(row_pending)begin
            desc_first<=first_j;desc_end<=end_j;desc_step<=descriptor_step;
            desc_vfirst<=row_q[3:0];desc_rank<=row_q[25:16];
            desc_nonempty<=descriptor_valid;desc_tag<=row_tag;desc_ready<=1;
        end
        if(descriptor_query)desc_ready<=0;
        // synthesis translate_off
        if(descriptor_query&&(!desc_ready||desc_tag!=((state==MG)?u+5'd1:u)))
            $fatal(1,"clipped row descriptor tag/not-ready mismatch");
        // synthesis translate_on
        case(state)
            IDLE,FIN: if(start) begin state<=RQ;rule_id<=0;word_id<=0;next_eid<=0;row_pending<=0;desc_ready<=0;end
            RQ: state<=RG;
            RG: begin
                r[word_id]<=rom_q;
                if(word_id==3) begin word_id<=0;state<=SQ;end
                else begin word_id<=word_id+1;state<=RQ;end
            end
            SQ:state<=SG;
            SG: begin
                sn[word_id]<=rom_q;
                if(word_id==3) begin word_id<=0;state<=TQ;end
                else begin word_id<=word_id+1;state<=SQ;end
            end
            TQ:state<=TG;
            TG: begin
                tn[word_id]<=rom_q;
                if(word_id==3) begin
                    word_id<=0;state<=OQ;offset_id<=12'(r[1]);
                    offset_end<=12'(r[1]+{16'b0,r[0][31:16]});
                    sbase<=sn[0][15:0];tbase<=tn[0][15:0];
                    sl<=sn[1][16];tl<=tn[1][16];sv<=sn[1][9:8];tv<=tn[1][9:8];
                    // synthesis translate_off
                    if(next_eid!=r[2][20:0]) $fatal(1,"rule first eid mismatch");
                    if(r[1]+{16'b0,r[0][31:16]}>4095||sn[1][23:16]>1||tn[1][23:16]>1||
                        (sn[1][15:8]<1||sn[1][15:8]>2)||(tn[1][15:8]<1||tn[1][15:8]>2))
                        $fatal(1,"template exceeds checked address widths");
                    // synthesis translate_on
                end else begin word_id<=word_id+1;state<=TQ;end
            end
            OQ:state<=OG;
            OG:begin
                if(word_id==0) begin geom<=rom_q;word_id<=1;state<=OQ;end
                else begin
                    offset_weight<=rom_q;du<=geom[3:0];dv<=geom[11:8];
                    // synthesis translate_off
                    if($signed(geom[7:0]) < -8 || $signed(geom[7:0]) > 7 ||
                       $signed(geom[15:8]) < -8 || $signed(geom[15:8]) > 7)
                        $fatal(1,"offset exceeds checked signed width");
                    // synthesis translate_on
                    // Skip entire u rows which cannot address the target map.
                    u<=geom[3]?5'(7'd0-{{3{geom[3]}},geom[3:0]}):5'd0;
                    u_last<=geom[3]?5'd30:(5'd30-{1'b0,geom[3:0]});
                    word_id<=0;state<=ROWQ;
                end
            end
            ROWQ:state<=ROWC;
            ROWC:state<=ROWG;
            ROWG:begin
                vfirst<=desc_vfirst;row_count<=desc_end;rank_first<=desc_rank;j<=desc_first;j_step<=desc_step;
                bounds_q<=in_bounds;
                // synthesis translate_off
                if(row_q[7:0]>15||row_q[15:8]>31||row_q[31:16]>1023)
                    $fatal(1,"row descriptor exceeds checked widths");
                // synthesis translate_on
                if(desc_nonempty) state<=MG;
                else if(u<u_last) begin u<=u+1;state<=ROWC;end
                else if(offset_id+1<offset_end) begin offset_id<=offset_id+1;state<=OQ;end
                else if(rule_id+1<NR) begin rule_id<=rule_id+1;state<=RQ;end
                else begin state<=FIN;
                    // synthesis translate_off
                    if(int'(next_eid)!=NE) $fatal(1,"edge total mismatch");
                    // synthesis translate_on
                end
            end
            MG:begin
                // One registered output slot. If downstream stalls, advance=0
                // freezes this slot, generator state and synchronous RAMs.
                // With ready asserted, lookup of the next candidate overlaps
                // consumption of this slot: no added steady-state issue gap.
                if(bounds_q&&(map_q!=16'hffff)) begin
                    valid<=1;src<=16'(sbase+{6'b0,rank_first}+{11'b0,j});
                    dst<=tbase+map_q;weight<=offset_weight;eid<=next_eid;
                    next_eid<=next_eid+1;
                end
                // synthesis translate_off
                if(!bounds_q||map_q==16'hffff)$fatal(1,"hole survived occupied-row intersection");
                // synthesis translate_on
                if(!last_candidate) begin j<=j+{3'b0,j_step};bounds_q<=in_bounds;state<=MG;end
                else if(u<u_last) begin
                    // row_q already contains u+1. Its first map read occurs
                    // in this same clock, before the final old response retires.
                    // synthesis translate_off
                    if(row_q[7:0]>15||row_q[15:8]>31||row_q[31:16]>1023)
                        $fatal(1,"prefetched row descriptor exceeds checked widths");
                    // synthesis translate_on
                    if(!desc_ready)begin u<=u+1;state<=ROWG;end
                    else if(desc_nonempty)begin
                        u<=u+1;vfirst<=desc_vfirst;row_count<=desc_end;
                        rank_first<=desc_rank;j<=desc_first;j_step<=desc_step;bounds_q<=in_bounds;state<=MG;
                    end else if(u+1<u_last)begin u<=u+2;state<=ROWC;end
                    else if(offset_id+1<offset_end)begin offset_id<=offset_id+1;state<=OQ;end
                    else if(rule_id+1<NR)begin rule_id<=rule_id+1;state<=RQ;end
                    else begin state<=FIN;
                        // synthesis translate_off
                        if(int'(next_eid)+int'(bounds_q&&(map_q!=16'hffff))!=NE) $fatal(1,"edge total mismatch");
                        // synthesis translate_on
                    end
                end
                else if(offset_id+1<offset_end) begin offset_id<=offset_id+1;state<=OQ;end
                else if(rule_id+1<NR) begin rule_id<=rule_id+1;state<=RQ;end
                else begin state<=FIN;
                    // synthesis translate_off
                    if(int'(next_eid)+int'(bounds_q&&(map_q!=16'hffff))!=NE) $fatal(1,"edge total mismatch");
                    // synthesis translate_on
                end
            end
            default:begin
                // synthesis translate_off
                $fatal(1,"generator state");
                // synthesis translate_on
            end
        endcase
        end
    end
endmodule
