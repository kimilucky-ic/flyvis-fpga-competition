"""Reproduce a build-local PS7 VIP scheduler repair; never used by synthesis."""
from pathlib import Path
import hashlib,json,difflib,sys

def prepare(build,vivado):
    native=Path(vivado)/'data/ip/xilinx/processing_system7_vip_v1_0/hdl/processing_system7_vip_v1_0_vl_rfs.sv'
    original=native.read_bytes()
    assert hashlib.sha256(original).hexdigest()=='1f212066d193e8ca618cc4a6ba6b1c77112caeffdf2e9b27ed6a3a60bc5325a0', 'Different native model; review patch again'
    source=native.read_text();start=source.index('module processing_system7_vip_v1_0_25_ddrc(');end=source.index('endmodule',start)+len('endmodule')
    part=source[start:end];old='end else begin\n case(state) \n 0:begin';assert part.count(old)==1
    part=part.replace(old,'end else begin\n // Local simulation-only race correction: upstream blocking #0 payload settles first.\n #1ps;\n case(state) \n 0:begin')
    part=part.replace('`include "processing_system7_vip_v1_0_25_local_params.v"','`include "processing_system7_vip_v1_0_25_local_params.v"\ninitial $display("B_PSVIP_DDRC_SCHEDULING_PATCH_1PS active; native VIP protocol checks retained");',1)
    patched=source[:start]+part+source[end:]
    d=Path(build)/'simulation_model';d.mkdir(exist_ok=True);f=d/native.name;f.write_text(patched)
    (d/'scheduling.patch').write_text(''.join(difflib.unified_diff(source.splitlines(True),patched.splitlines(True),fromfile=str(native),tofile=str(f))))
    identity=dict(original=str(native),original_sha256=hashlib.sha256(original).hexdigest(),patched_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),scope='SIMULATION_ONLY: native PS7 DDRC sample delayed 1ps for upstream #0 scheduling; no synthesis or DUT changes',unmodified_failure='stages/diagnose_4/simulate.log',unmodified_full_failure='stages/simulate_2/simulate.log')
    (d/'MODEL_IDENTITY.json').write_text(json.dumps(identity,indent=2)+'\n')
    return identity
if __name__=='__main__':print(json.dumps(prepare(sys.argv[1],sys.argv[2])))
