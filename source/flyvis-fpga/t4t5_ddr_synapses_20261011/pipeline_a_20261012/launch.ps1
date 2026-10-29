param([Parameter(Mandatory=$true)][string]$RunDir)
$ErrorActionPreference='Stop'
$pRun=[System.IO.Path]::GetFullPath($RunDir)
$pRoot=[System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot 'build'))+[System.IO.Path]::DirectorySeparatorChar
if(!$pRun.StartsWith($pRoot,[System.StringComparison]::OrdinalIgnoreCase)){throw 'Outside pipeline isolated build root'}
$pIdentity=Get-Content -LiteralPath (Join-Path $pRun 'RUN_IDENTITY.json') | ConvertFrom-Json
. (Join-Path $PSScriptRoot '..\..\phase3_20261010\amd2026_environment.ps1') -App Vivado
$env:TEMP=Join-Path $pRun 'tmp';$env:TMP=$env:TEMP
$pBin=Join-Path $env:XILINX_VIVADO 'bin'
Push-Location $pRun
try {
    if($pIdentity.kind -eq 'ooc') {
        & (Join-Path $pBin 'vivado.bat') -mode batch -source synth_pipeline.tcl -log vivado.log -journal vivado.jou
        if($LASTEXITCODE -ne 0){throw 'Pipeline OOC failed'}
        if(!(Select-String -LiteralPath vivado.log -Pattern 'B433880_OOC_SYNTHESIS_COMPLETE_NO_IMPLEMENTATION')){throw 'OOC marker absent'}
    } else {
        $pTop=$pIdentity.tb_top
        & (Join-Path $pBin 'xvlog.bat') --sv -i . edge_fifo.sv axi_edge_reader.sv ddr_synapse_core.sv ddr_synapse_top.sv ($pTop+'.sv') --log xvlog.log
        if($LASTEXITCODE -ne 0){throw 'Pipeline compile failed'}
        & (Join-Path $pBin 'xelab.bat') ('work.'+$pTop) -s pipeline_sim -debug typical --mt off -log xelab.log
        if($LASTEXITCODE -ne 0){throw 'Pipeline elaboration failed'}
        if($pIdentity.kind -eq 'fullstress') {
            # Keep '=' inside the response file; Windows batch argument parsing
            # otherwise splits an unquoted STRESS=1 into STRESS and 1.
            Set-Content -LiteralPath xsim_args.txt -Value '-testplusarg STRESS=1' -Encoding ascii
            & (Join-Path $pBin 'xsim.bat') pipeline_sim -runall -f xsim_args.txt -log xsim.log
        } else {
            & (Join-Path $pBin 'xsim.bat') pipeline_sim -runall -log xsim.log
        }
        if($LASTEXITCODE -ne 0){throw 'Pipeline simulation failed'}
        if(!(Select-String -LiteralPath xsim.log -Pattern 'ALL_PASS') -or (Select-String -LiteralPath xsim.log -Pattern 'Fatal:|FATAL|Error:')){throw 'Clean PASS marker absent'}
    }
} finally {Pop-Location}
