"""Prepare an isolated build; never invokes EDA or hardware operations."""
from pathlib import Path
import argparse,hashlib,json,shutil

HERE=Path(__file__).resolve().parent
NEURAL=HERE.parent.parent/'src/neural'
STAGES=('migrate3','combine','synth','route','bitgen')

def prepare(vendor,output):
    vendor=Path(vendor).resolve();output=Path(output).resolve()
    if output.exists():raise FileExistsError('Fresh output directory required; nothing overwritten')
    if output==vendor or vendor in output.parents:raise ValueError('Output must be separate from vendor source')
    expected=json.loads((HERE/'vendor_requirements.json').read_text('utf8'))
    for relative,digest in expected.items():
        p=vendor/relative
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
            raise ValueError('Missing or different vendor dependency: '+relative)
    for row in json.loads((HERE/'relocation_manifest.json').read_text('utf8')):
        if hashlib.sha256((NEURAL/Path(row['path']).relative_to('neural')).read_bytes()).hexdigest()!=row['sha256']:
            raise ValueError('Exported RTL/image identity mismatch: '+row['path'])
    output.mkdir(parents=True)
    shutil.copytree(NEURAL,output/'neural')
    for relative in expected:
        q=output/'vendor'/relative;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(vendor/relative,q)
    for name in ['base_2026.bd','camera_budget.xdc','audit_routed.tcl',*[s+'.tcl' for s in STAGES]]:
        shutil.copyfile(HERE/name,output/name)
    (output/'launch.ps1').write_text('''param([Parameter(Mandatory=$true)][string]$Vivado,[ValidateSet('migrate3','combine','synth','route','bitgen')][string]$Stage)
$ErrorActionPreference='Stop'
Set-Location -LiteralPath $PSScriptRoot
if (!(Test-Path -LiteralPath $Vivado -PathType Leaf)) { throw 'Vivado executable missing' }
$env:TEMP=Join-Path $PSScriptRoot 'tmp'
$env:TMP=$env:TEMP
New-Item -ItemType Directory -Force -Path $env:TEMP | Out-Null
$env:OMP_NUM_THREADS='1'
& $Vivado -mode batch -notrace -source ($Stage+'.tcl') -log ($Stage+'.log') -journal ($Stage+'.jou')
if ($LASTEXITCODE -ne 0) { throw 'Vivado stage failed; preserve logs and stop' }
''',encoding='utf8')
    result=dict(status='PREPARED_FILES_ONLY_NOT_SYNTHESIZED',vendor_files=len(expected),stages=STAGES,
                device_operations=0,eda_started=False)
    (output/'preparation.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vendor-dir',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();print(json.dumps(prepare(args.vendor_dir,args.output)))
