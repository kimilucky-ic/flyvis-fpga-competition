"""CPU pure validation and native-filesystem log-admission microbenchmarks."""
import hashlib,json,shutil,statistics,sys,tempfile,time,uuid
from pathlib import Path
P=Path(__file__).resolve().parent;G=P.parents[1];sys.path.insert(0,str(G))
import test_ps_commit_evidence
from test_ps_hotpath import PSHotPathTests
PSHotPathTests.setUpClass();case=PSHotPathTests('test_range_validation_all_saved_requests_and_candidates_and_edges')
rows=[];io_rows=[]
with tempfile.TemporaryDirectory(prefix='flyvis-ps-hotpath-') as folder:
    native=Path(folder);assert not str(native).startswith('/mnt/')
    test_ps_commit_evidence.OUT=native
    f,c=case.fixture(n=1);helper=c.e.driver_helpers
    payloads=[r[256:] for r in f.requests]+f.candidates
    for payload in payloads:
        assert helper.original_validate(payload) is None and helper.validate_words(payload) is None
    for repeat in range(6):
        for optimized in ((False,True) if repeat%2==0 else (True,False)):
            fn=helper.validate_words if optimized else helper.original_validate;start=time.perf_counter_ns()
            for payload in payloads:fn(payload)
            rows.append(dict(repeat=repeat,optimized=optimized,ms=(time.perf_counter_ns()-start)/1e6))
    for repeat in range(4):
        for optimized in ((False,True) if repeat%2==0 else (True,False)):
            f,c=case.fixture(n=1,optimized=optimized)
            fn=c.e.driver_helpers.save_bytes if optimized else c.d.run.__func__.__globals__['save_bytes']
            start=time.perf_counter_ns()
            for k,payload in enumerate(payloads):fn(c.base.directory/('CPU_%03d.bin'%k),payload)
            elapsed=(time.perf_counter_ns()-start)/1e6
            c.e.journal.checkpoint('CPU_LOG_COMPARE_NOT_NEURAL_RUN');c.base.close()
            reader=f.reader_module.JournalReader(c.e.journal.path)
            assert all(reader.read('CPU_%03d.bin'%k)==payload for k,payload in enumerate(payloads))
            copy=P/'native_closed_comparison'/('%s.fvej'%uuid.uuid4().hex)
            copy.parent.mkdir(exist_ok=True);shutil.copyfile(c.e.journal.path,copy)
            io_rows.append(dict(repeat=repeat,optimized=optimized,admission_ms=elapsed,
                files=len(payloads),bytes=sum(map(len,payloads)),closed_logical_files_verified=True,
                captured_file=copy.relative_to(P).as_posix(),capture_sha256=hashlib.sha256(copy.read_bytes()).hexdigest()))
    case.doCleanups()
def med(rows,key):return {str(flag):statistics.median(r[key] for r in rows if r['optimized']==flag) for flag in (False,True)}
validation=med(rows,'ms');io=med(io_rows,'admission_ms')
v=dict(evidence='CPU_MICROBENCHMARK_NOT_ARM_OR_NEW_GPU_FPGA_RUN',validation_rows=rows,log_admission_rows=io_rows,
    validation_64_saved_arrays_median_ms=validation,validation_speedup=validation['False']/validation['True'],
    native_log_64_files_median_ms=io,log_admission_speedup=io['False']/io['True'],
    validation_bytes=sum(map(len,payloads)),all_original_validation_results_and_saved_file_bytes_equal=True,
    note='Log timer includes Path construction, directory lookup/bound dispatch and original RAM add/SHA/bounds. Checkpoint/fsync is outside the timer but is actually performed and closed files verified; production checkpoint order unchanged.',
    GPU_runs=0,camera_starts=0,GUI_starts=0,board_connections=0,real_MMIO=0,new_scopes=0,actual_PS_ms='NOT_MEASURED')
(P/'CPU_COMPARISON.json').write_text(json.dumps(v,indent=2),encoding='utf8')
print(json.dumps({k:v[k] for k in ('evidence','validation_64_saved_arrays_median_ms','validation_speedup',
    'native_log_64_files_median_ms','log_admission_speedup','all_original_validation_results_and_saved_file_bytes_equal')},indent=2))
