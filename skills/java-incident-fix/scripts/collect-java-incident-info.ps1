param(
    [int]$Pid = 0,
    [string]$OutputDir = ".incident"
)

$ErrorActionPreference = "Continue"
$out = [System.IO.Path]::GetFullPath($OutputDir)
if (-not (Test-Path -LiteralPath $out)) {
    New-Item -ItemType Directory -Path $out | Out-Null
}

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$report = Join-Path $out "java-incident-info-$timestamp.txt"

function Append-Section {
    param([string]$Title, [scriptblock]$Command)
    Add-Content -LiteralPath $report -Encoding UTF8 -Value ""
    Add-Content -LiteralPath $report -Encoding UTF8 -Value "===== $Title ====="
    try {
        & $Command 2>&1 | Out-String | Add-Content -LiteralPath $report -Encoding UTF8
    } catch {
        Add-Content -LiteralPath $report -Encoding UTF8 -Value $_.Exception.Message
    }
}

Add-Content -LiteralPath $report -Encoding UTF8 -Value "Java incident collection time: $(Get-Date -Format o)"
Add-Content -LiteralPath $report -Encoding UTF8 -Value "Computer: $env:COMPUTERNAME"
Add-Content -LiteralPath $report -Encoding UTF8 -Value "User: $env:USERNAME"

Append-Section "Java Processes" { jps -lv }
Append-Section "Java Version" { java -version }

if ($Pid -gt 0) {
    Append-Section "VM Version for PID $Pid" { jcmd $Pid VM.version }
    Append-Section "VM Command Line for PID $Pid" { jcmd $Pid VM.command_line }
    Append-Section "GC Heap Info for PID $Pid" { jcmd $Pid GC.heap_info }
    Append-Section "Thread Print for PID $Pid" { jcmd $Pid Thread.print }
    Append-Section "Class Histogram for PID $Pid" { jcmd $Pid GC.class_histogram }
}

Write-Host "Incident info written to: $report"
