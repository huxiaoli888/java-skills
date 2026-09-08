param(
    [string]$Path = "."
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
        $content = Get-Content -LiteralPath $file.FullName -Raw -Encoding UTF8
        $isController = $content -match "@(RestController|Controller)\b" -or $file.FullName -match "\\controller\\"

        if ($isController -and $content -match "@Transactional\b") {
            $results.Add([pscustomobject]@{
                Type = "ControllerTransactional"
                File = $file.FullName
                Detail = "Controller contains @Transactional; transaction should usually live in service/use-case layer."
            })
        }

        if ($isController -and $content -match "import\s+.*\.(mapper|repository|dao)\.") {
            $results.Add([pscustomobject]@{
                Type = "ControllerDataAccessImport"
                File = $file.FullName
                Detail = "Controller imports mapper/repository/dao; route through service layer instead."
            })
        }

        if ($file.FullName -match "\\utils?\\|\\util\\" -and $content -match "(RedisTemplate|JdbcTemplate|Mapper|Repository|RocketMQ|Kafka|FeignClient|RestTemplate|WebClient)") {
            $results.Add([pscustomobject]@{
                Type = "BusinessUtility"
                File = $file.FullName
                Detail = "Utility package references infrastructure; verify this is not hidden business logic."
            })
        }
    }

if ($results.Count -eq 0) {
    Write-Host "No common layering risks found."
} else {
    $results | Format-Table -AutoSize
}
