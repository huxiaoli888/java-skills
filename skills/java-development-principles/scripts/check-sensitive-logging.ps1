param(
    [string]$Path = "."
)

$ErrorActionPreference = "Stop"
$root = [System.IO.Path]::GetFullPath($Path)
if (-not (Test-Path -LiteralPath $root)) {
    Write-Error "Path not found: $root"
    exit 1
}

$patterns = @(
    "password",
    "passwd",
    "pwd",
    "token",
    "secret",
    "privateKey",
    "accessKey",
    "authorization",
    "credential",
    "idCard",
    "phone",
    "mobile",
    "signature",
    "key"
)

$results = New-Object System.Collections.Generic.List[object]

Get-ChildItem -LiteralPath $root -Recurse -Filter "*.java" -File |
    Where-Object { $_.FullName -notmatch "\\target\\|\\build\\|\\.gradle\\" } |
    ForEach-Object {
        $file = $_
        $lines = Get-Content -LiteralPath $file.FullName -Encoding UTF8
        for ($i = 0; $i -lt $lines.Count; $i++) {
            $line = $lines[$i]
            if ($line -match "\b(log|logger)\.(trace|debug|info|warn|error)\s*\(") {
                foreach ($pattern in $patterns) {
                    if ($line -match $pattern) {
                        $results.Add([pscustomobject]@{
                            File = $file.FullName
                            Line = $i + 1
                            Pattern = $pattern
                            Detail = $line.Trim()
                        })
                        break
                    }
                }
            }
        }
    }

if ($results.Count -eq 0) {
    Write-Host "No obvious sensitive logging risks found."
} else {
    $results | Format-Table -AutoSize
}
