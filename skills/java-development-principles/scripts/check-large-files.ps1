param(
    [string]$Path = ".",
    [int]$FileLineThreshold = 600,
    [int]$MethodLineThreshold = 100
)

$ErrorActionPreference = "Stop"
$root = [System.IO.Path]::GetFullPath($Path)
if (-not (Test-Path -LiteralPath $root)) {
    Write-Error "Path not found: $root"
    exit 1
}

$results = New-Object System.Collections.Generic.List[object]

Get-ChildItem -LiteralPath $root -Recurse -Filter "*.java" -File |
    Where-Object { $_.FullName -notmatch "\\target\\|\\build\\|\\.gradle\\" } |
    ForEach-Object {
        $file = $_
        $lines = Get-Content -LiteralPath $file.FullName -Encoding UTF8
        if ($lines.Count -gt $FileLineThreshold) {
            $results.Add([pscustomobject]@{
                Type = "LargeFile"
                File = $file.FullName
                Line = ""
                Detail = "File has $($lines.Count) lines, threshold $FileLineThreshold"
            })
        }

        $braceDepth = 0
        $methodStart = $null
        $methodName = $null
        for ($i = 0; $i -lt $lines.Count; $i++) {
            $line = $lines[$i]
            if ($null -eq $methodStart -and $line -match "^\s*(public|private|protected)\s+[\w<>\[\], ?]+\s+(\w+)\s*\([^;]*\)\s*(throws\s+[\w, ]+)?\s*\{") {
                $methodStart = $i + 1
                $methodName = $Matches[2]
                $braceDepth = 0
            }

            if ($null -ne $methodStart) {
                $braceDepth += ([regex]::Matches($line, "\{")).Count
                $braceDepth -= ([regex]::Matches($line, "\}")).Count
                if ($braceDepth -le 0) {
                    $methodLength = ($i + 1) - $methodStart + 1
                    if ($methodLength -gt $MethodLineThreshold) {
                        $results.Add([pscustomobject]@{
                            Type = "LongMethod"
                            File = $file.FullName
                            Line = $methodStart
                            Detail = "$methodName has $methodLength lines, threshold $MethodLineThreshold"
                        })
                    }
                    $methodStart = $null
                    $methodName = $null
                }
            }
        }
    }

if ($results.Count -eq 0) {
    Write-Host "No large-file or long-method risks found."
} else {
    $results | Format-Table -AutoSize
}
