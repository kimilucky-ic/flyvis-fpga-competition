'use strict';
const assert=require('node:assert/strict');
const d=require('../viewer/stream_display_diagnostics.js');
const run={run_id:'test-only',session_id:'session-only'};
const status={...run,result_valid:false,compute:{error:'STREAM_OBSERVATION_COMPLETE'}};
for(const reason of ['STREAM_RESULT_REVOKED','RAW_REVOKED_DURING_RENDER','DRAW_RESULT_REVOKED','STREAM_STOP_REQUESTED']){
  assert.equal(d.terminalReason(reason,status,run),'STREAM_OBSERVATION_COMPLETE');
  for(const bad of [{...status,run_id:'other'},{...status,session_id:'other'},{...status,result_valid:true},{...status,compute:{error:'MODEL_LAG_LIMIT_NO_STEP_SKIP'}},null])
    assert.equal(d.terminalReason(reason,bad,run),reason);
}
for(const error of ['Failed to fetch','RAW_RECEIPT_IDENTITY','CLOCK_IDENTITY','BAD_SHA'])assert.equal(d.terminalReason(error,status,run),error);
console.log('PASS: terminal race classifications; identity, network and compute errors remain failures');
