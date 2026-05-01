$ErrorActionPreference = 'Continue'
$logDir = 'C:\Users\bjusm\operaite\scripts\logs'
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$logFile = Join-Path $logDir ("blog-" + (Get-Date -Format 'yyyy-MM-dd-HHmm') + ".log")

Set-Location 'C:\Users\bjusm\operaite'

$prompt = Get-Content -Raw 'C:\Users\bjusm\operaite\scripts\blog-prompt.md'

"=== Run started: $(Get-Date) ===" | Out-File -FilePath $logFile -Encoding utf8

& claude --print --dangerously-skip-permissions $prompt 2>&1 | Tee-Object -FilePath $logFile -Append

"=== Run finished: $(Get-Date) ===" | Out-File -FilePath $logFile -Append -Encoding utf8
