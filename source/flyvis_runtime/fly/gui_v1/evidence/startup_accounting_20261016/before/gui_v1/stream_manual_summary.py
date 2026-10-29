"""Read-only final accounting of one manually selected stream, never an inference."""
import json
import numpy as np
from live_protocol import load,require,sha
from stream_clock import control_clock


def manual_summary(root,control):
    path=root/'result.json'
    if not path.exists():return dict(status='WAITING_FOR_GPU_AND_EVIDENCE_FINALIZATION',run_id=control['run_id'])
    result=load(path);require(result['run_id']==control['run_id'] and result['session_id']==control['session_id'],'SUMMARY_RUN')
    rows=[];read_error=None
    try:
        for line in (root/'step_commits.jsonl').read_text(encoding='utf-8').splitlines():rows.append(json.loads(line))
    except (OSError,ValueError) as error:read_error=str(error)
    journal=result.get('commit_journal',{});computed=result.get('computed_steps',result['committed_steps'])
    ordered=all(row['step_id']==i and row['state_token']==i+1 and row['run_id']==control['run_id'] for i,row in enumerate(rows))
    complete=bool(not read_error and result.get('evidence_complete') and ordered and len(rows)==computed==result['committed_steps']==journal.get('durable_steps') and not result.get('cleanup_errors'))
    receipts=root/'display_receipts.jsonl';draws=[json.loads(line) for line in receipts.read_text(encoding='utf-8').splitlines()] if receipts.exists() else []
    require(all(d['run_id']==control['run_id'] for d in draws),'SUMMARY_DRAW_RUN')
    span=(draws[-1]['draw_server_monotonic_ns']-draws[0]['draw_server_monotonic_ns'])/1e9 if len(draws)>1 else None
    def percentile(key,p):
        data=[d[key] for d in draws if key in d]
        return float(np.percentile(data,p)) if data else None
    browser_failure=load(root/'browser_failure.json') if (root/'browser_failure.json').exists() else None
    if browser_failure:require(browser_failure['run_id']==control['run_id'] and browser_failure['session_id']==control['session_id'],'SUMMARY_BROWSER_FAILURE_RUN')
    complete_run=bool(result['success'] and complete and not browser_failure)
    fps=(len(draws)-1)/span if span and span>0 else None
    p95=percentile('upper_ms',95)
    clock=control_clock(control)
    observed=complete_run and result['reason']=='STREAM_OBSERVATION_COMPLETE'
    paced=result['inference_steps_per_s'] is not None and abs(result['inference_steps_per_s']/clock['target_steps_per_s']-1)<=.01
    return dict(schema='flyvis-manual-desktop-summary/v1',status='COMPLETED' if complete_run else 'FAILED',
        run_id=result['run_id'],session_id=result['session_id'],reason=browser_failure['error'] if browser_failure else result['reason'],
        compute_reason=result['reason'],browser_failure=browser_failure,
        computed_steps=computed,durable_steps=result['committed_steps'],journal_rows=len(rows),journal_order_valid=ordered,journal_read_error=read_error,evidence_complete=complete,
        steps_per_s=result['inference_steps_per_s'],compute_wall_s=result['elapsed_s'],display_FPS=fps,draw_count=len(draws),draw_span_s=span,
        clock=clock,model_time_s=computed*.005,observation_completed=observed,selected_pacing_within_1_percent=paced,
        BOUNDED_SLOW_CAMERA_TEST='PASS' if (clock['mode']=='SLOW_MODEL_DEMO' and observed and paced and len(draws)>1) else 'NOT_MET_OR_NOT_APPLICABLE',
        receipt_to_draw_p95_upper_ms=p95,render_p50_ms=percentile('render_ms',50),raf_wait_p50_ms=percentile('raf_wait_ms',50),
        latest_slot_age_p50_ms=percentile('packet_slot_age_ms',50),hidden_draws=sum(d.get('document_visible') is False for d in draws),
        display_hosts=sorted({d.get('display_host','UNRECORDED') for d in draws}),
        browser_environment=draws[-1].get('browser_environment') if draws else None,
        nominal_200_step_pacing=(result['inference_steps_per_s']>=199) if result['inference_steps_per_s'] is not None else None,
        nominal_pacing_definition='Within 0.5 percent of 200 steps/s; descriptive only, does not issue realtime PASS',
        display_at_least_15_FPS=fps>=15 if fps is not None else None,latency_p95_below_200_ms=p95<200 if p95 is not None else None,
        REALTIME_STREAM_PASS='NOT_APPLICABLE_SLOW_MODEL_DEMO' if clock['mode']=='SLOW_MODEL_DEMO' else 'PENDING_USER_ACCEPTANCE' if (complete_run
            and result['inference_steps_per_s'] is not None and result['inference_steps_per_s']>=200
            and fps is not None and fps>=15 and p95 is not None and p95<200) else 'NOT_MET',
        physical_screen_scanout='NOT_MEASURED',full_asset_rehash='NOT_PERFORMED_BY_QUICK_SUMMARY',
        result_sha256=sha(path),journal_sha256=sha(root/'step_commits.jsonl'),evidence_folder=str(root),PL_execution=False,FPGA_status='NOT_CONNECTED')
