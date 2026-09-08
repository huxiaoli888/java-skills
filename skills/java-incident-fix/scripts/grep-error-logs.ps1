param(
    [Parameter(Mandatory = $true)]
    [string]$LogPath,

    [string]$Pattern = "ERROR|Exception|traceId|requestId|timeout|refused|denied|failed",
    [int]$Context = 2,
    [string]$OutputFile = ""
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path -LiteralPath $LogPath)) {
    Write-Error "Log path not found: $LogPath"
    exit 1
}

$files = Get-ChildItem -LiteralPath $LogPath -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch "\\.zip$|\\.gz$" }

$matches = foreach ($file in $files) {
    Select-String -LiteralPath $file.FullName -Pattern $Pattern -Context $Context -ErrorAction SilentlyContinue
}

if ($OutputFile) {
    $fullOut = [System.IO.Path]::GetFullPath($OutputFile)
    $parent = Split-Path -Parent $fullOut
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent | Out-Null
    }
    $matches | Out-String | Set-Content -LiteralPath $fullOut -Encoding UTF8
    Write-Host "Log grep result written to: $fullOut"
} else {
    $matches
}
