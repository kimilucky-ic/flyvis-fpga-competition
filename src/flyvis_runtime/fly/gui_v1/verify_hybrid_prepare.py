"""Bounded CPU protocol + existing-evidence readback. No GUI/device launches."""
import ast
import csv
import io
import json
import subprocess
import sys
import unittest
from unittest.mock import patch
import numpy as np
from hybrid_a3 import A3Contract
from live_protocol import HERE,load,require,sha,utc,write
from prepare_hybrid_partition import prepare

OUT=HERE/'evidence/hybrid_prepare_20261012'


def main():
    OUT.mkdir(exist_ok=True)
    from test_live_protocol import Protocol
    from test_camera_stream import CameraProtocol
    from test_realtime_prepare import Realtime
    from test_stream import StreamTests
    from test_stream_efficiency import Efficiency
    from test_checked_full import CheckedFullProtocol
    from test_hybrid_a3 import HybridProtocol
    cases=(Protocol,CameraProtocol,Realtime,StreamTests,Efficiency,CheckedFullProtocol,HybridProtocol)
    suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(c) for c in cases)
    log=io.StringIO();result=unittest.TextTestRunner(stream=log).run(suite)
    (OUT/'cpu_tests.log').write_text(log.getvalue(),encoding='utf-8');require(result.wasSuccessful(),'CPU_TEST_FAILURE '+log.getvalue())
    import verify_live_interfaces
    with patch.object(verify_live_interfaces,'write'):preserved=verify_live_interfaces.verify()
    write(OUT/'preservation.json',preserved)
    js={}
    for file in ('test_spatial_view.cjs','test_spatial_geometry.cjs'):
        run=subprocess.run([r'C:\Program Files\nodejs\node.exe',str(HERE/file)],cwd=HERE,capture_output=True,text=True,check=True)
        js[file]=json.loads(run.stdout)
    write(OUT/'javascript.json',js)
    contract=A3Contract();write(OUT/'interface_status.json',contract.status())
    partition=prepare(OUT/'R5768_candidate_manifest.json')
    expected=np.asarray([int(v,16) for v in contract.paths['a3_expected'].read_text().split()],dtype='<u4').view('<i4')
    rows=list(csv.DictReader(contract.paths['a3_system_outputs'].open()))
    require(len(rows)==17304 and all(int(r['case'])==i//5768 and int(r['h_index'])==i%5768 and int(r['raw_q24'])==int(expected[i]) for i,r in enumerate(rows)),'A3_SYSTEM_SIM_REPLAY')
    archive=contract.paths['board67_verification'];board=load(archive);file=archive.parent/'results_2144.csv'
    rows67=list(csv.DictReader(file.open()));codes=[]
    require(len(rows67)==2144,'H67_COUNT')
    for i,r in enumerate(rows67):
        require(int(r['row'])==i//67 and int(r['neuron_index'])==i%67 and int(r['pl_q22_i32'])==int(r['oracle_q22_i32']) and r['match']=='true','H67_REPLAY')
        codes.append(int(r['pl_q22_i32']))
    import hashlib
    require(hashlib.sha256(np.asarray(codes,dtype='<i4').tobytes()).hexdigest()==board['pl_output_sha256'],'H67_OUTPUT_IDENTITY')
    old=load(HERE/'evidence/sync_optimization_20261012/verification.json')
    stream=HERE/'runtime/live/b872bc4816bc4004ab9bfef9eead9008/stream'
    require(sha(stream/'manifest.json')==old['manifest_sha256'],'PREVIOUS_STREAM_MANIFEST')
    for name,digest in load(stream/'manifest.json').items():require(sha(stream/name)==digest,'PREVIOUS_STREAM_CHANGED '+name)
    names=['hybrid_a3.py','hybrid_registry.json','prepare_hybrid_partition.py','test_hybrid_a3.py','verify_hybrid_prepare.py',
           'stream_transport.py','stream_bridge.py','stream_runtime.py','server.py','test_spatial_geometry.cjs']
    for n in names:
        if n.endswith('.py'):ast.parse((HERE/n).read_text(encoding='utf-8'))
    require(not any(m in sys.modules for m in ('torch','flyvis','cv2','pynq')),'DEVICE_MODULE_IMPORTED')
    report=dict(status='PASS_CPU_INTERFACE_AND_RECORDED_EVIDENCE_ONLY',utc=utc(),CPU_tests=result.testsRun,JS_tests=js,
        reused_original_coordinator=True,source_pins=contract.registry['pins'],original_39_pins=preserved['source_pins_verified'],
        source_replay=dict(A3R1=dict(evidence='SYSTEM_SIMULATION',states=17304,max_code_error=0),
            H67=dict(evidence='ACTUAL_BOARD_OFFLINE_REPLAY',requests=32,states=2144,true_closed_loop=False,csv_sha256=sha(file)),
            previous_GUI=dict(steps=2457,snapshots=224,manifest_sha256=old['manifest_sha256'],new_compute=False)),
        partition=partition,files_sha256={str(HERE/n):sha(HERE/n) for n in names},spatial_view_sha256=sha(HERE.parent/'viewer/spatial_view.js'),
        new_GPU_runs=0,new_neural_steps=0,new_decoder_calls=0,GUI_launches=0,camera_operations=0,board_operations=0,
        live_PL_backend='NOT_CONNECTED',PL_proven_global_ids=[],new_performance_measurement='NOT_RUN',FPGA_closed_loop='NOT_RUN',REALTIME_STREAM_PASS='NOT_MET_PREVIOUS_MEASUREMENT')
    write(OUT/'verification.json',report)
    print(json.dumps({k:report[k] for k in ('status','CPU_tests','JS_tests','source_replay','new_GPU_runs','board_operations','live_PL_backend')},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
