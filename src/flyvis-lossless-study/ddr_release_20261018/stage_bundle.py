"""Stage a self-contained offline-only bundle; no board imports or operations."""
import argparse,hashlib,json,shutil
from pathlib import Path
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--tag',default='bundle_r1');a=ap.parse_args()
    assert a.tag.replace('_','').isalnum();out=P/a.tag;out.mkdir(exist_ok=False)
    bit=json.loads((P/'bit_r1/RESULT.json').read_text());assert bit['status']=='PASS_BITGEN_COMMANDS_LOCAL_ONLY'
    oracle=json.loads((P/'oracle_r1/RESULT.json').read_text());assert oracle['status']=='PASS_INDEPENDENT_SERIAL_FP32_REFERENCE_CPU_ONLY'
    for name,h in oracle['output_sha256'].items():assert sha(P/'oracle_r1'/name)==h
    for name,info in bit['outputs'].items():assert sha(P/'bit_r1'/name)==info['sha256']
    for f in (P/'runtime').iterdir():
        if f.suffix in ('.py','.c'):shutil.copyfile(f,out/f.name)
    copies=[(P/'README.md','README.md'),(P/'bit_r1/flyvis_ddr.bit','flyvis_ddr.bit'),(P/'bit_r1/flyvis_ddr.hwh','flyvis_ddr.hwh'),
        (P.parent/'ddr_soc_20261018/ddr_control.py','ddr_control.py'),(P.parent/'ddr_snapshot_20261018/snapshot_records.py','snapshot_records.py'),
        (P/'oracle_r1/inputs.bin','inputs.bin'),(P/'oracle_r1/expected_states.bin','expected_states.bin'),(P/'oracle_r1/initial_state.bin','initial_state.bin'),
        (P.parent/'ddr_soc_20261018/control_r1/ddr_records.bin','cpu_fixture_ddr.bin'),
        (P.parent/'preboard_20261018/bundle_r1/PROVENANCE.json','original_model_provenance.json'),
        (P/'oracle_r1/RESULT.json','REFERENCE_PROVENANCE.json')]
    for src,name in copies:shutil.copyfile(src,out/name)
    source=P.parent/'ddr_soc_20261018/soc_r9/release'
    for name in ('timing_routed.rpt','utilization_routed.rpt','drc.rpt','route_status.rpt','check_timing.rpt'):shutil.copyfile(source/name,out/name)
    audit=json.loads((P.parent/'ddr_soc_20261018/AUDIT.json').read_text())
    save(out/'release_info.json',dict(schema='line11-ddr-offline-release/v1',execution_authority='NONE',board_operations=0,
        source_routed_dcp_sha256='c693e828c6028d0d6c41462e10aa52dfe1faa4bfc2ecc3b1e7d7f4e2b6227506',
        candidate='ddr_soc_20261018/soc_r9',bitgen=bit,implementation=dict(device=audit['device'],tool_version=audit['tool_version'],resources=audit['resources'],timing=audit['timing'],DRC=audit['DRC']),
        nodes=45669,edges=1513231,strict_FP32=True,clock_MHz=100,default_acceptance_steps=3,stimulus_sequence='original frozen frame0,frame1,frame0',
        initial_state_readback='NOT_SUPPORTED_BY_CURRENT_ABI',physical_results='NOT_RUN',
        original_model_provenance_note='ORIGINAL_MODEL_PROVENANCE identifies the frozen model/reference and old release. New candidate BIT/HWH identity is in this file, not that historical record.',
        future_board_prerequisites=['separate human authorization and exclusive ownership','new exact BIT/HWH already loaded','fresh unused ABI','live nominal100MHz source/divider/lock check','live HP0 read/write64-bit settings','target ARM barrier compilation','actual cache/DDR visibility validation']))
    manifest={f.name:dict(bytes=f.stat().st_size,sha256=sha(f)) for f in sorted(out.iterdir()) if f.is_file()}
    save(out/'release_manifest.json',manifest)
    print(json.dumps(dict(bundle=a.tag,files=len(manifest),manifest_sha256=sha(out/'release_manifest.json')),indent=2))
if __name__=='__main__':main()
