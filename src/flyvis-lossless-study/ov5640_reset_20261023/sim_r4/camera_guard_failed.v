// Candidate camera control only. Neural RTL is unchanged.
// run=0 resets capture/FIFO; run=1 releases each domain synchronously.
module camera_guard(
 (* X_INTERFACE_PARAMETER="XIL_INTERFACENAME aclk, FREQ_HZ 100000000" *) input aclk,
 input aresetn, run,
 (* X_INTERFACE_PARAMETER="XIL_INTERFACENAME pclk, FREQ_HZ 72000000" *) input pclk,
 input overflow,
 output stream_aresetn, capture_resetn,
 (* X_INTERFACE_INFO="xilinx.com:signal:reset:1.0 video_reset RST", X_INTERFACE_PARAMETER="XIL_INTERFACENAME video_reset, POLARITY ACTIVE_HIGH" *) output video_reset,
 output [2:0] status
);
 (* ASYNC_REG="TRUE" *) reg [1:0] ar=0, pr=0, global_pr=0;
 wire request_n = aresetn && run;
 always @(posedge aclk or negedge request_n)
   if (!request_n) ar<=0; else ar<={ar[0],1'b1};
 always @(posedge pclk or negedge request_n)
   if (!request_n) pr<=0; else pr<={pr[0],1'b1};
 always @(posedge pclk or negedge aresetn)
   if (!aresetn) global_pr<=0; else global_pr<={global_pr[0],1'b1};
 reg fault=0;
 // Only synchronous functional reset: no async control of video RAM enables.
 always @(posedge pclk)
   if (!global_pr[1]) fault<=0; else if (pr[1] && overflow) fault<=1;
 (* ASYNC_REG="TRUE" *) reg [1:0] fault_sync=0, ready_sync=0;
 always @(posedge aclk) begin
   if (!aresetn) begin fault_sync<=0;ready_sync<=0;end
   else begin fault_sync<={fault_sync[0],fault};ready_sync<={ready_sync[0],~video_reset_sync};end
 end
 assign stream_aresetn=ar[1];
 reg video_reset_sync=1;
 always @(posedge pclk) video_reset_sync<=~pr[1];
 assign video_reset=video_reset_sync;
 assign capture_resetn=pr[1];
 // Bit0 sticky overflow, bit1 video domain released, bit2 AXIS released.
 assign status={ar[1],ready_sync[1],fault_sync[1]};
endmodule
