param(
    [string]$ProjectName = "chaken-ai-test",
    [string]$CmsModuleName = "",
    [string]$SdkModuleName = "",
    [int]$CmsPort = 18080,
    [int]$SdkPort = 18081,
    [ValidateSet("minimal", "standard")]
    [string]$Profile = "standard",
    [string]$CmsContextPath = "",
    [string]$SdkContextPath = "",
    [string]$CmsUsername = "admin",
    [string]$CmsPassword = "admin123",
    [string]$CmsSignSecret = "dev-cms-sign-secret",
    [string]$CmsUdid = "cms-udid-001",
    [string]$SdkApiKey = "dev-sdk-api-key",
    [string]$SdkSecret = "dev-sdk-secret",
    [string]$SdkUdid = "sdk-udid-001",
    [string]$MavenPath = "",
    [string]$JavaPath = "",
    [int]$StartupTimeoutSeconds = 180,
    [switch]$SkipBuild
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$script:StartedProcesses = New-Object System.Collections.Generic.List[System.Diagnostics.Process]
$RootDir = Split-Path -Parent $PSScriptRoot
Set-Location $RootDir
$IsMinimalProfile = $Profile -eq "minimal"

if ([string]::IsNullOrWhiteSpace($CmsModuleName)) {
    $CmsModuleName = "{0}-cms-api" -f $ProjectName
}
if ([string]::IsNullOrWhiteSpace($SdkModuleName)) {
    $SdkModuleName = "{0}-sdk-api" -f $ProjectName
}
if ([string]::IsNullOrWhiteSpace($CmsContextPath)) {
    $CmsContextPath = "/$CmsModuleName"
}
if ([string]::IsNullOrWhiteSpace($SdkContextPath)) {
    $SdkContextPath = "/$SdkModuleName"
}

function Resolve-Executable {
    param(
        [string]$PreferredPath,
        [string]$CommandName
    )
    if (-not [string]::IsNullOrWhiteSpace($PreferredPath) -and (Test-Path -LiteralPath $PreferredPath)) {
        return $PreferredPath
    }
    $command = Get-Command $CommandName -ErrorAction SilentlyContinue
    if ($null -ne $command) {
        return $command.Source
    }
    throw "Executable not found: $CommandName"
}

function Assert-PortAvailable {
    param([int]$Port)
    $listener = $null
    try {
        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Any, $Port)
        $listener.Start()
    } catch {
        throw "Port $Port is already in use. Stop the existing service or pass another port."
    } finally {
        if ($null -ne $listener) {
            $listener.Stop()
        }
    }
}

function Find-BootJar {
    param([string]$ModuleName)
    $targetDir = Join-Path $RootDir "$ModuleName\target"
    if (-not (Test-Path -LiteralPath $targetDir)) {
        throw "Target directory does not exist: $targetDir"
    }
    $jar = Get-ChildItem -LiteralPath $targetDir -Filter "$ModuleName-*.jar" |
        Where-Object { $_.Name -notlike "*.original" } |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if ($null -eq $jar) {
        throw "Executable jar not found for module: $ModuleName"
    }
    return $jar.FullName
}

function Start-ApiService {
    param(
        [string]$ModuleName,
        [string]$LogPrefix,
        [string]$JavaExe
    )
    $jarPath = Find-BootJar -ModuleName $ModuleName
    $logDir = Join-Path $RootDir "run-logs"
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
    $stdout = Join-Path $logDir "$LogPrefix.out.log"
    $stderr = Join-Path $logDir "$LogPrefix.err.log"
    $process = Start-Process `
        -FilePath $JavaExe `
        -ArgumentList @("-jar", $jarPath) `
        -WorkingDirectory $RootDir `
        -RedirectStandardOutput $stdout `
        -RedirectStandardError $stderr `
        -WindowStyle Hidden `
        -PassThru
    $script:StartedProcesses.Add($process)
    Write-Host "$ModuleName started, pid=$($process.Id), log=$stdout"
}

function Wait-Health {
    param(
        [string]$Name,
        [string]$Url,
        [int]$TimeoutSeconds
    )
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-RestMethod -Uri $Url -TimeoutSec 3
            if ($response.status -eq "UP") {
                Write-Host "$Name health UP"
                return
            }
        } catch {
            Start-Sleep -Seconds 2
        }
    }
    throw "$Name health check timed out: $Url"
}

function Invoke-JsonRequest {
    param(
        [string]$Method,
        [string]$Uri,
        [hashtable]$Headers,
        [AllowNull()][string]$Body
    )
    try {
        $verb = switch ($Method.ToUpperInvariant()) {
            "GET" { "Get" }
            "POST" { "Post" }
            "PUT" { "Put" }
            "PATCH" { "Patch" }
            "DELETE" { "Delete" }
            default { $Method }
        }
        $canSendBody = $Method.ToUpperInvariant() -in @("POST", "PUT", "PATCH")
        if ($canSendBody -and -not [string]::IsNullOrEmpty($Body)) {
            return Invoke-RestMethod -Method $verb -Uri $Uri -Headers $Headers -Body $Body -ContentType "application/json; charset=utf-8"
        }
        return Invoke-RestMethod -Method $verb -Uri $Uri -Headers $Headers
    } catch {
        $response = $_.Exception.Response
        if ($null -ne $response) {
            $reader = New-Object System.IO.StreamReader($response.GetResponseStream())
            $text = $reader.ReadToEnd()
            throw "HTTP $([int]$response.StatusCode) from ${Uri}: $text"
        }
        throw
    }
}

function Assert-ApiSuccess {
    param(
        [string]$Name,
        [object]$Response
    )
    if ($null -eq $Response) {
        throw "$Name 返回空响应"
    }
    if ($Response.code -ne "000000") {
        throw "$Name 失败，code=$($Response.code)，message=$($Response.message)"
    }
    Write-Host "$Name passed, reqid=$($Response.reqid)"
}

function Get-CanonicalUrlEncoded {
    param([AllowNull()][string]$Value)
    if ([string]::IsNullOrWhiteSpace($Value)) {
        return ""
    }
    $parts = $Value -split "&" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
    $ordered = $parts | Sort-Object `
        @{ Expression = { [System.Net.WebUtility]::UrlDecode(($_ -split "=", 2)[0]) } }, `
        @{ Expression = {
            $pair = $_ -split "=", 2
            if ($pair.Length -gt 1) {
                [System.Net.WebUtility]::UrlDecode($pair[1])
            } else {
                ""
            }
        } }
    return ($ordered -join "&")
}

function New-SdkSignedHeaders {
    param(
        [string]$Method,
        [string]$Path,
        [string]$Query,
        [string]$Body,
        [string]$Reqid
    )
    $signatureAlg = "HMAC-SHA256"
    $apiVersion = "v1"
    $timestamp = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds().ToString()
    $bodyValue = if ($null -eq $Body) { "" } else { $Body }
    $canonicalQuery = Get-CanonicalUrlEncoded -Value $Query
    $prefix = (($Method.ToUpperInvariant()), $Path, $canonicalQuery, $timestamp, $Reqid, $SdkApiKey, $SdkUdid, $signatureAlg, $apiVersion) -join "`n"
    $canonical = $prefix + "`n" + $bodyValue
    $keyBytes = [System.Text.Encoding]::UTF8.GetBytes($SdkSecret)
    $dataBytes = [System.Text.Encoding]::UTF8.GetBytes($canonical)
    $hmac = New-Object System.Security.Cryptography.HMACSHA256(, $keyBytes)
    $signature = [Convert]::ToBase64String($hmac.ComputeHash($dataBytes))
    return @{
        "accept-language" = "zh-CN"
        "x-api-key" = $SdkApiKey
        "x-timestamp" = $timestamp
        "x-reqid" = $Reqid
        "x-sign" = $signature
        "x-sign-alg" = $signatureAlg
        "x-api-version" = $apiVersion
        "x-udid" = $SdkUdid
    }
}

function New-CmsSignedHeaders {
    param(
        [string]$Method,
        [string]$Path,
        [string]$Query,
        [string]$Body,
        [string]$Reqid,
        [string]$ContentType = "application/json; charset=utf-8"
    )
    $signatureAlg = "HMAC-SHA256"
    $apiVersion = "v1"
    $timestamp = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds().ToString()
    $authorization = "Bearer $CmsToken"
    $bodyValue = if ($null -eq $Body) { "" } else { $Body }
    $canonicalQuery = Get-CanonicalUrlEncoded -Value $Query
    $prefix = (($Method.ToUpperInvariant()), $Path, $canonicalQuery, $timestamp, $Reqid, $authorization, $CmsUdid, $signatureAlg, $apiVersion) -join "`n"
    $canonical = $prefix + "`n" + $bodyValue
    $keyBytes = [System.Text.Encoding]::UTF8.GetBytes($CmsSignSecret)
    $dataBytes = [System.Text.Encoding]::UTF8.GetBytes($canonical)
    $hmac = New-Object System.Security.Cryptography.HMACSHA256(, $keyBytes)
    $signature = [Convert]::ToBase64String($hmac.ComputeHash($dataBytes))
    return @{
        "authorization" = $authorization
        "accept-language" = "zh-CN"
        "x-timestamp" = $timestamp
        "x-reqid" = $Reqid
        "x-sign" = $signature
        "x-sign-alg" = $signatureAlg
        "x-api-version" = $apiVersion
        "x-udid" = $CmsUdid
    }
}

function Invoke-CmsLogin {
    param(
        [string]$BaseUrl,
        [string]$Username,
        [string]$Password
    )
    $body = (New-Object psobject -Property ([ordered]@{
        username = $Username
        password = $Password
    }) | ConvertTo-Json -Compress)
    $response = Invoke-JsonRequest -Method "POST" -Uri "$BaseUrl/api/v1/cms/auth/login" -Headers @{
        "accept-language" = "zh-CN"
        "content-type" = "application/json; charset=utf-8"
    } -Body $body
    Assert-ApiSuccess -Name "CMS login" -Response $response
    if ([string]::IsNullOrWhiteSpace($response.data.token)) {
        throw "CMS 登录未返回 token"
    }
    return $response.data.token
}

try {
    $mavenExe = Resolve-Executable -PreferredPath $MavenPath -CommandName "mvn.cmd"
    $javaExe = Resolve-Executable -PreferredPath $JavaPath -CommandName "java.exe"
    Assert-PortAvailable -Port $CmsPort
    if (-not $IsMinimalProfile) {
        Assert-PortAvailable -Port $SdkPort
    }

    if (-not $SkipBuild) {
        Write-Host "Building project with clean install..."
        & $mavenExe -q clean install
        if ($LASTEXITCODE -ne 0) {
            throw "Maven build failed with exit code $LASTEXITCODE"
        }
    }

    Start-ApiService -ModuleName $CmsModuleName -LogPrefix "cms-smoke" -JavaExe $javaExe
    if (-not $IsMinimalProfile) {
        Start-ApiService -ModuleName $SdkModuleName -LogPrefix "sdk-smoke" -JavaExe $javaExe
    }

    $cmsBaseUrl = "http://localhost:$CmsPort$CmsContextPath"
    $sdkBaseUrl = "http://localhost:$SdkPort$SdkContextPath"
    Wait-Health -Name "CMS" -Url "$cmsBaseUrl/actuator/health" -TimeoutSeconds $StartupTimeoutSeconds
    if (-not $IsMinimalProfile) {
        Wait-Health -Name "SDK" -Url "$sdkBaseUrl/actuator/health" -TimeoutSeconds $StartupTimeoutSeconds
    }

    $CmsToken = Invoke-CmsLogin -BaseUrl $cmsBaseUrl -Username $CmsUsername -Password $CmsPassword

    $cmsCurrentUserPath = "$CmsContextPath/api/v1/cms/sys/current-user"
    $cmsCurrentUser = Invoke-JsonRequest -Method "GET" -Uri "$cmsBaseUrl/api/v1/cms/sys/current-user" -Headers (New-CmsSignedHeaders -Method "GET" -Path $cmsCurrentUserPath -Query "" -Body "" -Reqid "cms-current-user-$([DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds())") -Body $null
    Assert-ApiSuccess -Name "CMS current user" -Response $cmsCurrentUser

    $cmsSysUsersPath = "$CmsContextPath/api/v1/cms/sys/users"
    $cmsSysUsers = Invoke-JsonRequest -Method "GET" -Uri "$cmsBaseUrl/api/v1/cms/sys/users?page=1&pageSize=10" -Headers (New-CmsSignedHeaders -Method "GET" -Path $cmsSysUsersPath -Query "page=1&pageSize=10" -Body "" -Reqid "cms-page-sys-users-$([DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds())") -Body $null
    Assert-ApiSuccess -Name "CMS page sys users" -Response $cmsSysUsers

    $cmsSysDictsPath = "$CmsContextPath/api/v1/cms/sys/dicts"
    $cmsSysDicts = Invoke-JsonRequest -Method "GET" -Uri "$cmsBaseUrl/api/v1/cms/sys/dicts?page=1&pageSize=10" -Headers (New-CmsSignedHeaders -Method "GET" -Path $cmsSysDictsPath -Query "page=1&pageSize=10" -Body "" -Reqid "cms-page-sys-dicts-$([DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds())") -Body $null
    Assert-ApiSuccess -Name "CMS page sys dicts" -Response $cmsSysDicts

    $cmsSysDictItemsPath = "$CmsContextPath/api/v1/cms/sys/dicts/sys_status/items"
    $cmsSysDictItems = Invoke-JsonRequest -Method "GET" -Uri "$cmsBaseUrl/api/v1/cms/sys/dicts/sys_status/items" -Headers (New-CmsSignedHeaders -Method "GET" -Path $cmsSysDictItemsPath -Query "" -Body "" -Reqid "cms-list-sys-dict-items-$([DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds())") -Body $null
    Assert-ApiSuccess -Name "CMS list sys dict items" -Response $cmsSysDictItems

    $cmsSysParamsPath = "$CmsContextPath/api/v1/cms/sys/params"
    $cmsSysParams = Invoke-JsonRequest -Method "GET" -Uri "$cmsBaseUrl/api/v1/cms/sys/params?page=1&pageSize=10" -Headers (New-CmsSignedHeaders -Method "GET" -Path $cmsSysParamsPath -Query "page=1&pageSize=10" -Body "" -Reqid "cms-page-sys-params-$([DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds())") -Body $null
    Assert-ApiSuccess -Name "CMS page sys params" -Response $cmsSysParams

    $cmsTestTasksPath = "$CmsContextPath/api/v1/cms/test-tasks"
    $cmsPage = Invoke-JsonRequest -Method "GET" -Uri "$cmsBaseUrl/api/v1/cms/test-tasks?page=1&pageSize=10" -Headers (New-CmsSignedHeaders -Method "GET" -Path $cmsTestTasksPath -Query "page=1&pageSize=10" -Body "" -Reqid "cms-page-test-tasks-$([DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds())") -Body $null
    Assert-ApiSuccess -Name "CMS page test tasks" -Response $cmsPage

    $crudSuffix = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds().ToString()
    $crudCreateBody = (New-Object psobject -Property ([ordered]@{
        name = "smoke item $crudSuffix"
        code = "SMOKE$crudSuffix"
        description = "created by smoke test"
        enabled = $true
    }) | ConvertTo-Json -Compress)
    $cmsSampleItemsPath = "$CmsContextPath/api/v1/cms/sample-items"
    $crudCreate = Invoke-JsonRequest -Method "POST" -Uri "$cmsBaseUrl/api/v1/cms/sample-items" -Headers (New-CmsSignedHeaders -Method "POST" -Path $cmsSampleItemsPath -Query "" -Body $crudCreateBody -Reqid "cms-create-sample-$crudSuffix") -Body $crudCreateBody
    Assert-ApiSuccess -Name "CMS create sample item" -Response $crudCreate

    $itemId = $null
    if ($crudCreate.data.PSObject.Properties.Name -contains "itemId") {
        $itemId = $crudCreate.data.itemId
    }
    if ([string]::IsNullOrWhiteSpace($itemId) -and $crudCreate.data.PSObject.Properties.Name -contains "id") {
        $itemId = $crudCreate.data.id
    }
    if ([string]::IsNullOrWhiteSpace($itemId)) {
        throw "CMS 创建 sample item 未返回 data.id"
    }
    $crudDetailPath = "$CmsContextPath/api/v1/cms/sample-items/$itemId"
    $crudDetail = Invoke-JsonRequest -Method "GET" -Uri "$cmsBaseUrl/api/v1/cms/sample-items/$itemId" -Headers (New-CmsSignedHeaders -Method "GET" -Path $crudDetailPath -Query "" -Body "" -Reqid "cms-detail-sample-$crudSuffix") -Body $null
    Assert-ApiSuccess -Name "CMS get sample item" -Response $crudDetail

    $crudUpdateBody = (New-Object psobject -Property ([ordered]@{
        name = "smoke item updated $crudSuffix"
        remark = "updated by smoke test"
        version = $crudDetail.data.version
    }) | ConvertTo-Json -Compress)
    $crudUpdate = Invoke-JsonRequest -Method "PUT" -Uri "$cmsBaseUrl/api/v1/cms/sample-items/$itemId" -Headers (New-CmsSignedHeaders -Method "PUT" -Path $crudDetailPath -Query "" -Body $crudUpdateBody -Reqid "cms-update-sample-$crudSuffix") -Body $crudUpdateBody
    Assert-ApiSuccess -Name "CMS update sample item" -Response $crudUpdate

    $crudDelete = Invoke-JsonRequest -Method "DELETE" -Uri "$cmsBaseUrl/api/v1/cms/sample-items/$itemId" -Headers (New-CmsSignedHeaders -Method "DELETE" -Path $crudDetailPath -Query "" -Body "" -Reqid "cms-delete-sample-$crudSuffix") -Body $null
    Assert-ApiSuccess -Name "CMS delete sample item" -Response $crudDelete

    $crudPage = Invoke-JsonRequest -Method "GET" -Uri "$cmsBaseUrl/api/v1/cms/sample-items?page=1&pageSize=10" -Headers (New-CmsSignedHeaders -Method "GET" -Path $cmsSampleItemsPath -Query "page=1&pageSize=10" -Body "" -Reqid "cms-page-sample-$crudSuffix") -Body $null
    Assert-ApiSuccess -Name "CMS page sample items" -Response $crudPage

    if (-not $IsMinimalProfile) {
        $suffix = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds().ToString()
        $createBody = (New-Object psobject -Property ([ordered]@{
            requestNo = "REQ-SMOKE-$suffix"
            businessNo = "BIZ-SMOKE-$suffix"
            taskName = "smoke test task $suffix"
            modelCode = "demo-model"
            callbackUrl = "https://example.com/callback"
        }) | ConvertTo-Json -Compress)
        $createPath = "$SdkContextPath/api/v1/sdk/test-tasks"
        $createHeaders = New-SdkSignedHeaders -Method "POST" -Path $createPath -Query "" -Body $createBody -Reqid "sdk-create-$suffix"
        $createResponse = Invoke-JsonRequest -Method "POST" -Uri "$sdkBaseUrl/api/v1/sdk/test-tasks" -Headers $createHeaders -Body $createBody
        Assert-ApiSuccess -Name "SDK create test task" -Response $createResponse

        $taskNo = $createResponse.data.taskNo
        if ([string]::IsNullOrWhiteSpace($taskNo)) {
            throw "SDK 创建测试任务未返回 data.taskNo"
        }
        $statusPath = "$SdkContextPath/api/v1/sdk/test-tasks/$taskNo"
        $statusHeaders = New-SdkSignedHeaders -Method "GET" -Path $statusPath -Query "" -Body "" -Reqid "sdk-status-$suffix"
        $statusResponse = Invoke-JsonRequest -Method "GET" -Uri "$sdkBaseUrl/api/v1/sdk/test-tasks/$taskNo" -Headers $statusHeaders -Body $null
        Assert-ApiSuccess -Name "SDK query task status" -Response $statusResponse

        Write-Host "SMOKE_TEST_PASSED profile=$Profile taskNo=$taskNo"
    } else {
        Write-Host "SMOKE_TEST_PASSED profile=$Profile"
    }
} finally {
    foreach ($process in $script:StartedProcesses) {
        if ($null -ne $process -and -not $process.HasExited) {
            Stop-Process -Id $process.Id -Force
            Write-Host "Stopped pid=$($process.Id)"
        }
    }
}
