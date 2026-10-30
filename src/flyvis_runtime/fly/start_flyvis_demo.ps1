param([switch]$EnableGPU,[switch]$Desktop,[switch]$Stream,[switch]$Skeleton,[switch]$Camera,[switch]$Stop,[switch]$Status,[switch]$NoOpen,[switch]$Benchmark,[ValidateRange(10,300)][int]$StreamSeconds=300,[ValidateSet('quiet','balanced','performance','current_unconfirmed')][string]$PowerMode='current_unconfirmed',[ValidateSet('baseline','sampled','combined_checks','owned_checks')][string]$Variant='sampled')
$ErrorActionPreference='Stop'
if ($Skeleton) { $Stream=$true }
if ($Desktop -and ($Stop -or $Status -or $NoOpen -or $Benchmark)) { throw 'Desktop applies only to a visible manual start.' }
if ($Stop -and $Status) { throw 'Choose Stop or Status.' }
if ($EnableGPU -and ($Stop -or $Status)) { throw 'EnableGPU applies only to a new manual start.' }
if ($Camera -and ($Stop -or $Status)) { throw 'Camera applies only to a new manual start.' }
if ($Stream -and ($Stop -or $Status)) { throw 'Stream applies only to a new manual start.' }
$demoPython=Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $demoPython)) { throw 'Existing fly Python environment is required; this launcher does not install dependencies.' }
if ($Benchmark) {
    if ($Stream -or $Camera -or $Stop -or $Status -or $NoOpen) { throw 'Benchmark is a separate single manual measurement, without GUI/camera.' }
    $benchmarkArguments=@('-B',(Join-Path $PSScriptRoot 'gui_v1\realtime_benchmark.py'),'--power-mode',$PowerMode,'--variant',$Variant)
    if ($EnableGPU) { $benchmarkArguments+='--enable-gpu' }
    & $demoPython @benchmarkArguments
    if ($LASTEXITCODE -ne 0) { throw 'Benchmark failed; preserve its logs. No automatic retry.' }
    exit
}
$demoAction=if ($Stop) {'stop'} elseif ($Status) {'status'} else {'start'}
$demoArguments=@('-B',(Join-Path $PSScriptRoot 'gui_v1\demo_launcher.py'),$demoAction)
if ($demoAction -eq 'start') {$demoArguments+=@('--power-mode',$PowerMode,'--stream-seconds',$StreamSeconds)}
if ($EnableGPU) {$demoArguments+='--enable-gpu'}
if ($Camera) {$demoArguments+='--camera'}
if ($Stream) {$demoArguments+='--stream'}
if ($Skeleton) {$demoArguments+='--skeleton'}
if ($NoOpen) {$demoArguments+='--no-open'}
if ($Desktop) {$demoArguments+='--desktop'}
& $demoPython @demoArguments
if ($LASTEXITCODE -ne 0) { throw "FlyVis demo command failed ($LASTEXITCODE). Inspect the managed session log; no replay is used as a new result." }
