"""Preserve failed/blocked attempts without reusing an unfinished trajectory."""
from pathlib import Path
from datetime import datetime,timezone
import json,traceback,uuid
HERE=Path(__file__).resolve().parent
def record(context,exc):
    out=HERE/'attempt_failures'/str(uuid.uuid4());out.mkdir(parents=True)
    d=dict(status='BLOCKED_OR_FAILED_ATTEMPT_NOT_ACCEPTED',created_utc=datetime.now(timezone.utc).isoformat(),
        exception_type=type(exc).__name__,exception=str(exc),traceback=traceback.format_exc(),
        mode=context.get('mode'),reference_repeat=context.get('reference_repeat'),condition=context.get('condition'),
        native_H_update_evidence='unknown until result/audit exists',fallback_performed=False,FPGA_execution=False,
        incomplete_arrays_must_not_be_consumed=True)
    co=context.get('coordinator')
    if co is not None:
        import numpy as np
        from h_step import array_hash
        state=co.state
        np.save(out/'last_committed_full.npy',state)
        d.update(last_committed_next_step_id=co.next_step_id,last_committed_digest=array_hash(state),
            pending_step_id=None if co.pending is None else co.pending.tag.step_id,coordinator_status=co.status,
            co_logs=co.logs)
    with (out/'failure.json').open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
