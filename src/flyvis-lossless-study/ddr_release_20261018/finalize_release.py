"""Package the CPU-tested offline candidate and verify a fresh extraction."""
import hashlib,importlib.util,json,shutil,subprocess,sys,zipfile
from pathlib import Path
from build_bit import verify_seals
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def main():
    b=P/'bundle_r2';test=json.loads((P/'CPU_RESULT_cpu_tests_r1.json').read_text(encoding='utf-8'))
    assert test['status']=='PASS_OFFLINE_RELEASE_CPU_CONTRACT_ONLY' and test['tests']==18
    assert test['bundle_manifest_sha256']==sha(b/'release_manifest.json') and test['test_sha256']==sha(P/'test_release.py')
    for f in (P/'runtime').iterdir():
        if f.suffix in ('.py','.c'):assert sha(f)==sha(b/f.name),f.name
    baseline=verify_seals();assert baseline==json.loads((P/'BASELINE_BEFORE.json').read_text())
    save(P/'BASELINE_AFTER.json',baseline)
    sys.path.insert(0,str(b));from offline_check import verify
    check=verify(b)
    source=P.parent/'ddr_soc_20261018'
    spec=importlib.util.spec_from_file_location('frozen_audit',source/'audit_soc.py');audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
    timing=audit.timing(P/'bit_r1/timing.rpt');prior=json.loads((source/'AUDIT.json').read_text())['timing']
    assert timing==prior,(timing,prior)
    assert not any(timing[k] for k in ('setup_failing','hold_failing','pulse_failing'))
    for n,h in json.loads((P/'bit_r1/INPUT_SNAPSHOT.json').read_text()).items():assert sha(P/'bit_r1'/n)==h,n
    archive=P/'flyvis_line11_ddr_100mhz_offline_r2.zip'
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for f in sorted(b.iterdir()):
            if f.is_file():z.write(f,f.name)
    extracted=P/'extracted_r1';extracted.mkdir(exist_ok=False)
    with zipfile.ZipFile(archive) as z:
        expected={f.name for f in b.iterdir() if f.is_file()}
        assert len(z.namelist())==len(expected) and set(z.namelist())==expected
        assert z.testzip() is None
        for info in z.infolist():
            assert Path(info.filename).name==info.filename and info.file_size==(b/info.filename).stat().st_size
            data=z.read(info);assert hashlib.sha256(data).hexdigest()==sha(b/info.filename)
            with (extracted/info.filename).open('xb') as f:f.write(data)
    commands=[]
    for name,args in [('offline_check',[str(extracted/'offline_check.py')]),
                      ('cpu_replay',[str(extracted/'cpu_replay.py'),str(P/'extracted_cpu_r1')])]:
        command=[sys.executable,'-B',*args]
        r=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30)
        (P/('EXTRACTED_'+name+'.log')).write_bytes(r.stdout);commands.append(dict(command=command,returncode=r.returncode));r.check_returncode()
    replay=json.loads((P/'extracted_cpu_r1/RESULT.json').read_text())
    assert replay['evidence']=='CPU_MOCK_ONLY' and not replay['board_result'] and replay['states_compared']==137007
    assert replay['completed_steps']==3 and replay['input_words_compared']==2163 and replay['mismatch_words']==0
    for i in range(3):assert sha(P/'extracted_cpu_r1'/('record_%06d.bin'%i))==hashlib.sha256((b/'cpu_fixture_ddr.bin').read_bytes()[i*188416:(i+1)*188416]).hexdigest()
    result=dict(status='PASS_BIT_HWH_OFFLINE_RELEASE_AND_CPU_ACCEPTANCE_ONLY',date='2026-10-18',bundle='bundle_r2',archive=archive.name,
        zip_bytes=archive.stat().st_size,zip_sha256=sha(archive),package_manifest_sha256=sha(b/'release_manifest.json'),files=len(expected),
        nodes=45669,edges=1513231,strict_FP32_unchanged=True,clock_MHz=100,timing=timing,
        bit_sha256=check['bit_sha256'],hwh_sha256=check['hwh_sha256'],bit_header=check['bit_header'],
        cpu_tests=test,fresh_extraction_replay=replay,commands=commands,baseline_seals_unchanged=baseline,
        board_operations=0,GPU_operations=0,new_synthesis_or_route=False,
        boundaries=['No physical BIT load, DDR allocation/cache visibility or native ARM barrier compilation/execution',
            'Initial full-state readback is unavailable in current ABI; all post-step states are compared',
            'Future real binding needs separate operator authorization, fresh image/ownership/nominal clock/HP0-width checks',
            'No real-time/FPS/power or physical continuous-feedback result',
            'Uncertain sessions retain DDR and prohibit retry/reset/automatic free'])
    save(P/'FINAL_RESULT.json',result)
    (P/(archive.name+'.sha256')).write_text(sha(archive)+'  '+archive.name+'\n',encoding='ascii')
    print(json.dumps({k:v for k,v in result.items() if k in ('status','archive','zip_bytes','zip_sha256','files','bit_sha256','hwh_sha256','package_manifest_sha256')},indent=2))
if __name__=='__main__':main()
