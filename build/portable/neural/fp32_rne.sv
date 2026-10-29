// Exact binary32 RNE. True internal pipelines, II=1, common CE and reset.
// No FMA, FTZ, host arithmetic, or change to the accepted NaN/flag contract.
// Add uses exact integer units of 2^-149; mul uses the exact 48-bit product.
module fp32_add_pipeline(
    input logic clk,reset,ce,valid_in,input logic [31:0] a,b,
    output logic valid_out,output logic [31:0] result,output logic [4:0] flags);
    typedef struct packed {
        logic special; logic [36:0] special_result;
        logic sa,sb,sign,sub;
        logic [7:0] ash,bsh;
        logic [279:0] ma,mb,hi,lo;
        logic [3:0] gt,eq;
        logic [283:0] sums;
        logic [287:0] mag;
        logic [17:0] groups;
        logic [71:0] positions;
        logic [8:0] k;
        logic zero;
        logic [7:0] shift;
        logic [8:0] exponent;
        logic [290:0] shifted;
        logic [24:0] rounded;
        logic nx;
    } context_t;
    context_t d[0:11];
    logic [12:0] v;
    logic [36:0] packed_result;
    function automatic logic [3:0] msb16(input logic [15:0] x);
        logic [15:0] q; logic [3:0] n;
        begin q=x;n=0;
            if(|q[15:8]) begin q=q>>8;n=n+8;end
            if(|q[7:4]) begin q=q>>4;n=n+4;end
            if(|q[3:2]) begin q=q>>2;n=n+2;end
            if(q[1]) n=n+1;
            return n;
        end
    endfunction
    function automatic logic [4:0] msb18(input logic [17:0] x);
        logic [17:0] q;logic [4:0] n;
        begin q=x;n=0;
            if(|q[17:16]) begin q=q>>16;n=n+16;end
            if(|q[15:8]) begin q=q>>8;n=n+8;end
            if(|q[7:4]) begin q=q>>4;n=n+4;end
            if(|q[3:2]) begin q=q>>2;n=n+2;end
            if(q[1]) n=n+1;
            return n;
        end
    endfunction
    function automatic logic [290:0] jam(input logic [290:0] x,input integer n);
        logic [290:0] q;
        begin q=x>>n;q[0]=q[0]|(|(x<<(291-n)));return q;end
    endfunction
    logic an,bn,ai,bi;
    logic a_ge_b;
    logic [4:0] carry,group_index;
    logic [7:0] amount;
    logic [290:0] shift_low,shift_high;
    logic [8:0] final_exp;
    always_comb begin
        an=(&a[30:23])&&(|a[22:0]);bn=(&b[30:23])&&(|b[22:0]);
        ai=(&a[30:23])&&!(|a[22:0]);bi=(&b[30:23])&&!(|b[22:0]);
        a_ge_b=d[3].gt[3]|(d[3].eq[3]&d[3].gt[2])|
            (&d[3].eq[3:2]&d[3].gt[1])|(&d[3].eq[3:1]&d[3].gt[0])|(&d[3].eq);
        carry=0;carry[0]=d[5].sub;
        for(integer j=0;j<4;j=j+1)
            carry[j+1]=d[5].sums[71*j+70]|((&d[5].sums[71*j+:70])&carry[j]);
        group_index=msb18(d[7].groups);
        amount=(d[8].k>23)?8'(d[8].k-23):8'b0;
        shift_low={d[8].mag,3'b0};
        for(integer j=0;j<4;j=j+1) if(amount[j]) shift_low=jam(shift_low,1<<j);
        shift_high=d[9].shifted;
        for(integer j=4;j<8;j=j+1) if(d[9].shift[j]) shift_high=jam(shift_high,1<<j);
        final_exp=d[11].exponent+9'(d[11].rounded[24]);
        packed_result=0;
        if(d[11].zero) packed_result={5'b0,d[11].sign,31'b0};
        else if(final_exp>=255) packed_result={5'b00101,d[11].sign,8'hff,23'b0};
        else packed_result={4'b0,d[11].nx,d[11].sign,final_exp[7:0],
            (d[11].rounded[24]?d[11].rounded[23:1]:d[11].rounded[22:0])};
        if(d[11].special) packed_result=d[11].special_result;
    end
    always_ff @(posedge clk) begin
        if(reset) v<='0;
        else if(ce) begin
            v<={v[11:0],valid_in};
            for(integer i=1;i<12;i=i+1) d[i]<=d[i-1];
            // 0: classify and decode exact finite significands.
            d[0]<='0;d[0].sa<=a[31];d[0].sb<=b[31];
            d[0].ma<={{256{1'b0}},(|a[30:23]),a[22:0]};
            d[0].mb<={{256{1'b0}},(|b[30:23]),b[22:0]};
            d[0].ash<=(a[30:23]==0)?0:a[30:23]-8'd1;
            d[0].bsh<=(b[30:23]==0)?0:b[30:23]-8'd1;
            d[0].special<=an|bn|ai|bi;
            if(an|bn) d[0].special_result<={((an&&!a[22])||(bn&&!b[22])),4'b0,32'h7fc00000};
            else if(ai&&bi&&(a[31]!=b[31])) d[0].special_result<={5'b10000,32'h7fc00000};
            else d[0].special_result<={5'b0,(ai?a[31]:b[31]),8'hff,23'b0};
            // 1-2: split the exact alignment barrel shifters.
            d[1].ma<=d[0].ma<<d[0].ash[3:0];d[1].mb<=d[0].mb<<d[0].bsh[3:0];
            d[2].ma<=d[1].ma<<{d[1].ash[7:4],4'b0};
            d[2].mb<=d[1].mb<<{d[1].bsh[7:4],4'b0};
            // 3-4: four bounded comparators, followed by magnitude selection.
            for(integer j=0;j<4;j=j+1) begin
                d[3].gt[j]<=d[2].ma[70*j+:70]>d[2].mb[70*j+:70];
                d[3].eq[j]<=d[2].ma[70*j+:70]==d[2].mb[70*j+:70];
            end
            d[4].hi<=a_ge_b?d[3].ma:d[3].mb;
            d[4].lo<=a_ge_b?d[3].mb:d[3].ma;
            d[4].sub<=d[3].sa^d[3].sb;
            d[4].sign<=(d[3].sa==d[3].sb)?d[3].sa:((&d[3].eq)?1'b0:(a_ge_b?d[3].sa:d[3].sb));
            // 5-6: four 70-bit carry-select slices. No 278-bit ripple chain.
            for(integer j=0;j<4;j=j+1)
                d[5].sums[71*j+:71]<={1'b0,d[4].hi[70*j+:70]}+
                    {1'b0,(d[4].lo[70*j+:70]^{70{d[4].sub}})};
            d[6].mag<='0;
            for(integer j=0;j<4;j=j+1)
                d[6].mag[70*j+:70]<=d[5].sums[71*j+:70]+70'(carry[j]);
            // 7-8: local leading-one detection then global selection.
            for(integer j=0;j<18;j=j+1) begin
                d[7].groups[j]<=|d[6].mag[16*j+:16];
                d[7].positions[4*j+:4]<=msb16(d[6].mag[16*j+:16]);
            end
            d[7].zero<=d[6].mag==0;
            d[8].k<={group_index,4'b0}+9'(d[7].positions[4*group_index+:4]);
            // 9-10: jammed normalization preserves guard/round/sticky exactly.
            d[9].shift<=amount;d[9].shifted<=shift_low;
            d[9].exponent<=(d[8].k>=23)?d[8].k-9'd22:9'b0;
            d[10].shifted<=shift_high;
            // 11: one rounding, restricted to the necessary 25-bit result.
            d[11].rounded<={1'b0,d[10].shifted[26:3]}+
                25'(d[10].shifted[2]&&((|d[10].shifted[1:0])||d[10].shifted[3]));
            d[11].nx<=|d[10].shifted[2:0];
            // 12: final exponent, flags, signed zero and special-value bypass.
            {flags,result}<=packed_result;
        end
    end
    assign valid_out=v[12];
endmodule

module fp32_mul_pipeline(
    input logic clk,reset,ce,valid_in,input logic [31:0] a,b,
    output logic valid_out,output logic [31:0] result,output logic [4:0] flags);
    typedef struct packed {
        logic special;logic [36:0] special_result;logic sign,zero,tiny,nx;
        logic [31:0] raw_a,raw_b;
        logic [23:0] ma,mb;logic [47:0] mag;
        logic signed [10:0] power,exponent,shift;
        logic [5:0] k;
        logic [50:0] shifted;
        logic [24:0] rounded;
    } context_t;
    context_t d[0:6];logic [7:0] v;
    wire [31:0] operand_a=d[0].raw_a,operand_b=d[0].raw_b;
    logic an,bn,ai,bi,az,bz;
    logic signed [10:0] exponent,amount,final_exp;
    logic [50:0] shift_low,shift_high;
    logic [36:0] packed_result;
    function automatic logic [5:0] msb48(input logic [47:0] x);
        logic [47:0] q;logic [5:0] n;
        begin q=x;n=0;
            if(|q[47:32]) begin q=q>>32;n=n+32;end
            if(|q[31:16]) begin q=q>>16;n=n+16;end
            if(|q[15:8]) begin q=q>>8;n=n+8;end
            if(|q[7:4]) begin q=q>>4;n=n+4;end
            if(|q[3:2]) begin q=q>>2;n=n+2;end
            if(q[1]) n=n+1;
            return n;
        end
    endfunction
    function automatic logic [50:0] jam(input logic [50:0] x,input integer n);
        logic [50:0] q;
        begin
            if(n>=51) q={50'b0,(|x)};
            else begin q=x>>n;q[0]=q[0]|(|(x<<(51-n)));end
            return q;
        end
    endfunction
    always_comb begin
        an=(&operand_a[30:23])&&(|operand_a[22:0]);bn=(&operand_b[30:23])&&(|operand_b[22:0]);
        ai=(&operand_a[30:23])&&!(|operand_a[22:0]);bi=(&operand_b[30:23])&&!(|operand_b[22:0]);
        az=operand_a[30:0]==0;bz=operand_b[30:0]==0;
        exponent=$signed({5'b0,d[2].k})+d[2].power;
        amount=(exponent < -126)?(-11'sd149-d[2].power):($signed({5'b0,d[2].k})-11'sd23);
        shift_low={d[3].mag,3'b0};
        if(d[3].shift<0) shift_low=shift_low<<(-d[3].shift);
        else for(integer j=0;j<4;j=j+1) if(d[3].shift[j]) shift_low=jam(shift_low,1<<j);
        shift_high=d[4].shifted;
        if(d[4].shift>=0)
            for(integer j=4;j<8;j=j+1) if(d[4].shift[j]) shift_high=jam(shift_high,1<<j);
        final_exp=d[6].exponent+11'(d[6].rounded[24]);
        packed_result=0;
        if(d[6].zero) packed_result={5'b0,d[6].sign,31'b0};
        else if(d[6].exponent < -126)
            packed_result={3'b0,(d[6].tiny&&d[6].nx),d[6].nx,d[6].sign,7'b0,d[6].rounded[23:0]};
        else if(final_exp>127) packed_result={5'b00101,d[6].sign,8'hff,23'b0};
        else packed_result={4'b0,d[6].nx,d[6].sign,8'(final_exp+127),
            (d[6].rounded[24]?d[6].rounded[23:1]:d[6].rounded[22:0])};
        if(d[6].special) packed_result=d[6].special_result;
    end
    always_ff @(posedge clk) begin
        if(reset) v<='0;
        else if(ce) begin
            v<={v[6:0],valid_in};
            for(integer i=1;i<7;i=i+1)d[i]<=d[i-1];
            d[0]<='0;d[0].sign<=a[31]^b[31];
            d[0].raw_a<=a;d[0].raw_b<=b;
            d[0].ma<={(|a[30:23]),a[22:0]};d[0].mb<={(|b[30:23]),b[22:0]};
            // Stage 0 terminates the bank-mux/operand-select path. Decode the
            // exponent and special values from registered inputs in stage 1,
            // alongside (not in series with) the exact product.
            d[1].power<=((operand_a[30:23]==0)?-11'sd149:($signed({3'b0,operand_a[30:23]})-11'sd150))+
                ((operand_b[30:23]==0)?-11'sd149:($signed({3'b0,operand_b[30:23]})-11'sd150));
            d[1].special<=an|bn|ai|bi;
            if(an|bn) d[1].special_result<={((an&&!operand_a[22])||(bn&&!operand_b[22])),4'b0,32'h7fc00000};
            else if((ai&&bz)||(bi&&az)) d[1].special_result<={5'b10000,32'h7fc00000};
            else d[1].special_result<={5'b0,d[0].sign,8'hff,23'b0};
            d[1].mag<=d[0].ma*d[0].mb;
            d[2].k<=msb48(d[1].mag);d[2].zero<=d[1].mag==0;
            d[3].exponent<=exponent;d[3].shift<=amount;
            // Same after-rounding tininess test as the accepted exact oracle.
            d[3].tiny<=!(exponent==-127&&d[2].k>=24&&
                ((d[2].mag>>(d[2].k-24))==48'h1ffffff));
            d[4].shifted<=shift_low;
            d[5].shifted<=shift_high;
            d[6].rounded<={1'b0,d[5].shifted[26:3]}+
                25'(d[5].shifted[2]&&((|d[5].shifted[1:0])||d[5].shifted[3]));
            d[6].nx<=|d[5].shifted[2:0];
            {flags,result}<=packed_result;
        end
    end
    assign valid_out=v[7];
endmodule

module fp32_pipe #(parameter integer LATENCY=13,parameter bit MULTIPLY=0)(
    input logic clk,reset,ce,valid_in,input logic [31:0] a,b,
    output logic valid_out,output logic [31:0] result,output logic [4:0] flags);
    initial begin
        if((MULTIPLY&&LATENCY!=8)||(!MULTIPLY&&LATENCY!=13))
            $fatal(1,"True FP32 pipeline requires add=13 / multiply=8 enabled clocks");
    end
    if(MULTIPLY) fp32_mul_pipeline impl(.*);
    else fp32_add_pipeline impl(.*);
endmodule
