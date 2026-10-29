param([Parameter(ValueFromRemainingArguments = $true)][string[]]$RunnerArguments)
& python -B (Join-Path $PSScriptRoot 'runner.py') @RunnerArguments
exit $LASTEXITCODE
