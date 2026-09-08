# Profile-specific generator helpers. Dot-source from scaffold-java-backend-project.ps1.

function Remove-EmptyParentDirectories {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$StopAt
    )
    $current = Split-Path -Parent $Path
    while ($current -and $current.StartsWith($StopAt) -and $current -ne $StopAt) {
        if ((Get-ChildItem -LiteralPath $current -Force | Select-Object -First 1) -ne $null) {
            break
        }
        Remove-Item -LiteralPath $current
        $current = Split-Path -Parent $current
    }
}


function Remove-DirectoryInsideRoot {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$Path
    )
    $rootFullPath = [System.IO.Path]::GetFullPath($Root)
    $pathFullPath = [System.IO.Path]::GetFullPath($Path)
    if (-not $pathFullPath.StartsWith($rootFullPath)) {
        throw "拒绝删除目标目录外的路径：$pathFullPath"
    }
    if (Test-Path -LiteralPath $pathFullPath) {
        Remove-Item -LiteralPath $pathFullPath -Recurse -Force
    }
}

function Remove-LineContaining {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string[]]$Needles
    )
    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }
    $lines = [System.IO.File]::ReadAllLines($Path, [System.Text.Encoding]::UTF8)
    $kept = New-Object System.Collections.Generic.List[string]
    foreach ($line in $lines) {
        $matched = $false
        foreach ($needle in $Needles) {
            if ($line.Contains($needle)) {
                $matched = $true
                break
            }
        }
        if (-not $matched) {
            $kept.Add($line)
        }
    }
    [System.IO.File]::WriteAllLines($Path, $kept, $Utf8NoBom)
}

function Write-MinimalApiInventory {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$CmsModule
    )
    $content = @"
# API 清单

> Profile: minimal

## 1. 模块边界

| 模块 | 使用方 | 职责 | 不负责 |
| --- | --- | --- | --- |
| ``$CmsModule`` | 后台管理端 | CMS controller、CMS request/response DTO、开发级登录/token、后台认证鉴权适配、操作日志/登录日志查询、后台操作审计落库、CMS 业务 service、CMS mapper/entity/repository | 开放平台对外契约、客户端签名验签入口 |

## 2. 通用请求头

``````text
authorization
accept-language
x-trace-id
x-reqid
x-timestamp
x-sign
x-sign-alg
x-api-version
x-udid
``````

登录、验证码、探活等公开接口通过 ``auth-exclude-paths`` 跳过认证链，不要求 token、签名或 ``x-udid``。受保护 CMS 接口使用 ``authorization: Bearer <token>`` 表达登录态，使用 ``x-udid`` 表达设备或用户唯一标识；``x-timestamp`` 做时间窗口校验，``x-sign`` 做防篡改签名，防重放 replay key 使用 token 指纹 + ``x-udid`` + ``x-reqid``，``x-sign-alg`` 和 ``x-api-version`` 参与签名 canonical。

## 3. CMS 接口清单

| ID | 接口名称 | Method | URL | 使用主体 | 认证 | 签名 | 防重放 | 幂等 | Request DTO | Response DTO | Service 方法 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CMS-HEALTH-001 | CMS 服务探活 | GET | ``/actuator/health`` | 监控/探针 | 否 | 否 | 否 | 否 | 无 | Actuator | Actuator | 只返回服务可用性，不返回内部配置 |
| CMS-SYS-001 | 查询当前后台用户 | GET | ``/api/v1/cms/sys/current-user`` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 否 | 无 | ``SysCurrentUserResponse`` | ``SysUserService.currentUser`` | 返回当前用户、角色、权限和菜单 |
| CMS-SYS-002 | 分页查询后台用户 | GET | ``/api/v1/cms/sys/users`` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 否 | ``SysUserPageQuery`` | ``PageResult<SysUserResponse>`` | ``SysUserService.page`` | 开发级用户查询骨架 |
| CMS-SYS-003 | 查询后台角色 | GET | ``/api/v1/cms/sys/roles`` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 否 | 无 | ``List<SysRoleResponse>`` | ``SysRoleService.listActiveRoles`` | 开发级角色查询骨架 |
| CMS-SYS-004 | 查询后台菜单 | GET | ``/api/v1/cms/sys/menus`` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 否 | 无 | ``List<SysMenuResponse>`` | ``SysMenuService.listActiveMenus`` | 开发级菜单和权限查询骨架 |
| CMS-SYS-005 | 分页查询后台字典 | GET | ``/api/v1/cms/sys/dicts`` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 否 | ``SysDictPageQuery`` | ``PageResult<SysDictResponse>`` | ``SysDictService.page`` | 开发级字典查询骨架 |
| CMS-SYS-006 | 查询字典项 | GET | ``/api/v1/cms/sys/dicts/{dictCode}/items`` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 否 | 无 | ``List<SysDictItemResponse>`` | ``SysDictService.listItems`` | 开发级字典项查询骨架 |
| CMS-SYS-007 | 分页查询后台参数 | GET | ``/api/v1/cms/sys/params`` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 否 | ``SysParamPageQuery`` | ``PageResult<SysParamResponse>`` | ``SysParamService.page`` | 开发级参数查询骨架，不保存密钥类配置 |
| CMS-TASK-001 | 分页查询测试任务 | GET | ``/api/v1/cms/test-tasks`` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 否 | ``TestTaskPageQuery`` | ``PageResult<TestTaskResponse>`` | ``TestTaskQueryService.pageTasks`` | P0 查询样例 |
| CMS-TASK-002 | 查询测试任务详情 | GET | ``/api/v1/cms/test-tasks/{taskNo}`` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 否 | 无 | ``TestTaskDetailResponse`` | ``TestTaskQueryService.getTaskDetail`` | P0 详情样例 |
| CMS-SAMPLE-001 | 创建样例条目 | POST | ``/api/v1/cms/sample-items`` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 业务可选 | ``SampleItemCreateRequest`` | ``SampleItemDetailResponse`` | ``SampleItemService.createItem`` | 简单 CRUD 样例，记录操作审计 |
| CMS-SAMPLE-002 | 分页查询样例条目 | GET | ``/api/v1/cms/sample-items`` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 否 | ``SampleItemPageQuery`` | ``PageResult<SampleItemResponse>`` | ``SampleItemService.pageItems`` | 简单 CRUD 样例 |
| CMS-SAMPLE-003 | 查询样例条目详情 | GET | ``/api/v1/cms/sample-items/{itemId}`` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 否 | 无 | ``SampleItemDetailResponse`` | ``SampleItemService.getItem`` | 简单 CRUD 样例 |
| CMS-SAMPLE-004 | 修改样例条目 | PUT | ``/api/v1/cms/sample-items/{itemId}`` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 业务可选 | ``SampleItemUpdateRequest`` | ``SampleItemDetailResponse`` | ``SampleItemService.updateItem`` | 简单 CRUD 样例，记录操作审计 |
| CMS-SAMPLE-005 | 删除样例条目 | DELETE | ``/api/v1/cms/sample-items/{itemId}`` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 业务可选 | 无 | ``Void`` | ``SampleItemService.deleteItem`` | 简单 CRUD 样例，记录操作审计 |

## 4. DTO 和实现边界

- CMS request DTO、response DTO、entity 分开定义。
- Controller 只处理 HTTP 入参、参数校验、鉴权注解和统一响应。
- Service 处理业务规则和事务边界。
- Mapper/Repository 只处理数据库访问；复杂 SQL 放入 ``src/main/resources/mapper/**/*.xml``。

## 5. 待生产替换

- 默认开发管理员、固定签名密钥、内存 replay request store、内存幂等和日志型兜底操作审计仅用于本地开发。
- 生产环境应按 ``docs/development/production_stack.md`` 和 ``docs/development/production_replacement.md`` 替换。
"@
    [System.IO.File]::WriteAllText($Path, $content, $Utf8NoBom)
}

function Write-MinimalSmokeTest {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$ProjectName,
        [Parameter(Mandatory = $true)][string]$CmsModule
    )
    $content = @'
param(
    [string]$ProjectName = "__PROJECT_NAME__",
    [string]$CmsModuleName = "__CMS_MODULE__",
    [int]$CmsPort = 18080,
    [ValidateSet("minimal")]
    [string]$Profile = "minimal",
    [string]$CmsContextPath = "",
    [string]$CmsUsername = "admin",
    [string]$CmsPassword = "admin123",
    [string]$CmsSignSecret = "dev-cms-sign-secret",
    [string]$CmsUdid = "cms-udid-001",
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

if ([string]::IsNullOrWhiteSpace($CmsContextPath)) {
    $CmsContextPath = "/$CmsModuleName"
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
        Where-Object { $_.Name -notlike "*sources*" -and $_.Name -notlike "*javadoc*" } |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if ($null -eq $jar) {
        throw "Boot jar not found in $targetDir"
    }
    return $jar.FullName
}

function Start-ApiService {
    param(
        [string]$ModuleName,
        [string]$LogPrefix,
        [string]$JavaExe
    )
    $jar = Find-BootJar -ModuleName $ModuleName
    $logDir = Join-Path $RootDir "target\smoke-logs"
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    $stdout = Join-Path $logDir "$LogPrefix.out.log"
    $stderr = Join-Path $logDir "$LogPrefix.err.log"
    $process = Start-Process -FilePath $JavaExe -ArgumentList @("-jar", $jar) -WorkingDirectory $RootDir -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru -WindowStyle Hidden
    $script:StartedProcesses.Add($process)
    Write-Host "Started $ModuleName pid=$($process.Id)"
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
            $response = Invoke-RestMethod -Method GET -Uri $Url -TimeoutSec 3
            if ($response.status -eq "UP") {
                Write-Host "$Name health is UP"
                return
            }
        } catch {
            Start-Sleep -Seconds 2
        }
    }
    throw "$Name health check timed out: $Url"
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

function New-CmsSignedHeaders {
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
    $authorization = "Bearer $CmsToken"
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

function Invoke-JsonRequest {
    param(
        [string]$Method,
        [string]$Uri,
        [hashtable]$Headers,
        [AllowNull()][string]$Body
    )
    $verb = switch ($Method.ToUpperInvariant()) {
        "GET" { "Get" }
        "POST" { "Post" }
        "PUT" { "Put" }
        "PATCH" { "Patch" }
        "DELETE" { "Delete" }
        default { $Method }
    }
    $canSendBody = $Method.ToUpperInvariant() -in @("POST", "PUT", "PATCH")
    if (-not $canSendBody -or [string]::IsNullOrEmpty($Body)) {
        return Invoke-RestMethod -Method $verb -Uri $Uri -Headers $Headers -TimeoutSec 10
    }
    return Invoke-RestMethod -Method $verb -Uri $Uri -Headers $Headers -Body $Body -ContentType "application/json" -TimeoutSec 10
}

function Assert-ApiSuccess {
    param(
        [string]$Name,
        [object]$Response
    )
    if ($null -eq $Response -or $Response.code -ne "000000") {
        $payload = $Response | ConvertTo-Json -Depth 10 -Compress
        throw "$Name failed: $payload"
    }
}

try {
    Assert-PortAvailable -Port $CmsPort
    $mavenExe = Resolve-Executable -PreferredPath $MavenPath -CommandName "mvn"
    $javaExe = Resolve-Executable -PreferredPath $JavaPath -CommandName "java"

    if (-not $SkipBuild) {
        Write-Host "Building minimal project with clean install..."
        & $mavenExe -q clean install
        if ($LASTEXITCODE -ne 0) {
            throw "Maven build failed with exit code $LASTEXITCODE"
        }
    }

    Start-ApiService -ModuleName $CmsModuleName -LogPrefix "cms-smoke" -JavaExe $javaExe
    $cmsBaseUrl = "http://localhost:$CmsPort$CmsContextPath"
    Wait-Health -Name "CMS" -Url "$cmsBaseUrl/actuator/health" -TimeoutSeconds $StartupTimeoutSeconds

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

    $itemId = $crudCreate.data.itemId
    if ([string]::IsNullOrWhiteSpace($itemId)) {
        $itemId = $crudCreate.data.id
    }
    if ([string]::IsNullOrWhiteSpace($itemId)) {
        throw "CMS 创建 sample item 未返回 data.itemId"
    }
    $crudDetailPath = "$CmsContextPath/api/v1/cms/sample-items/$itemId"
    $crudDetail = Invoke-JsonRequest -Method "GET" -Uri "$cmsBaseUrl/api/v1/cms/sample-items/$itemId" -Headers (New-CmsSignedHeaders -Method "GET" -Path $crudDetailPath -Query "" -Body "" -Reqid "cms-detail-sample-$crudSuffix") -Body $null
    Assert-ApiSuccess -Name "CMS get sample item" -Response $crudDetail

    $crudUpdateBody = (New-Object psobject -Property ([ordered]@{
        name = "smoke item updated $crudSuffix"
        code = "SMOKE$crudSuffix"
        description = "updated by smoke test"
        enabled = $true
    }) | ConvertTo-Json -Compress)
    $crudUpdate = Invoke-JsonRequest -Method "PUT" -Uri "$cmsBaseUrl/api/v1/cms/sample-items/$itemId" -Headers (New-CmsSignedHeaders -Method "PUT" -Path $crudDetailPath -Query "" -Body $crudUpdateBody -Reqid "cms-update-sample-$crudSuffix") -Body $crudUpdateBody
    Assert-ApiSuccess -Name "CMS update sample item" -Response $crudUpdate

    $crudDelete = Invoke-JsonRequest -Method "DELETE" -Uri "$cmsBaseUrl/api/v1/cms/sample-items/$itemId" -Headers (New-CmsSignedHeaders -Method "DELETE" -Path $crudDetailPath -Query "" -Body "" -Reqid "cms-delete-sample-$crudSuffix") -Body $null
    Assert-ApiSuccess -Name "CMS delete sample item" -Response $crudDelete

    $crudPage = Invoke-JsonRequest -Method "GET" -Uri "$cmsBaseUrl/api/v1/cms/sample-items?page=1&pageSize=10" -Headers (New-CmsSignedHeaders -Method "GET" -Path $cmsSampleItemsPath -Query "page=1&pageSize=10" -Body "" -Reqid "cms-page-sample-$crudSuffix") -Body $null
    Assert-ApiSuccess -Name "CMS page sample items" -Response $crudPage

    Write-Host "SMOKE_TEST_PASSED profile=$Profile"
} finally {
    foreach ($process in $script:StartedProcesses) {
        if ($null -ne $process -and -not $process.HasExited) {
            Stop-Process -Id $process.Id -Force
            Write-Host "Stopped pid=$($process.Id)"
        }
    }
}
'@
    $content = $content.Replace("__PROJECT_NAME__", $ProjectName).Replace("__CMS_MODULE__", $CmsModule)
    [System.IO.File]::WriteAllText($Path, $content, $Utf8Bom)
}

function Apply-MinimalProfile {
    param(
        [Parameter(Mandatory = $true)][string]$ProjectRoot,
        [Parameter(Mandatory = $true)][string]$SdkModule,
        [Parameter(Mandatory = $true)][string]$CmsModule,
        [Parameter(Mandatory = $true)][string]$CommonModule
    )
    Remove-DirectoryInsideRoot -Root $ProjectRoot -Path (Join-Path $ProjectRoot $SdkModule)

    $pomPath = Join-Path $ProjectRoot "pom.xml"
    $pomContent = [System.IO.File]::ReadAllText($pomPath, [System.Text.Encoding]::UTF8)
    $pomContent = $pomContent.Replace("    <module>$SdkModule</module>`r`n", "")
    $pomContent = $pomContent.Replace("    <module>$SdkModule</module>`n", "")
    [System.IO.File]::WriteAllText($pomPath, $pomContent, $Utf8NoBom)

    Remove-LineContaining -Path (Join-Path $ProjectRoot "README.md") -Needles @($SdkModule, "CMS 和 SDK")
    Remove-LineContaining -Path (Join-Path $ProjectRoot "AGENTS.md") -Needles @($SdkModule, "SDK/open-platform")
    Remove-LineContaining -Path (Join-Path $ProjectRoot "$CmsModule\AGENTS.md") -Needles @($SdkModule)
    Remove-LineContaining -Path (Join-Path $ProjectRoot "docs\architecture\module_map.md") -Needles @($SdkModule, "SDK", "sdk --> common")
    Remove-LineContaining -Path (Join-Path $ProjectRoot "docs\architecture\system_architecture.md") -Needles @("SDK", "sdk-api", "x-api-key")
    Write-MinimalApiInventory -Path (Join-Path $ProjectRoot "docs\api\api_inventory.md") -CmsModule $CmsModule
    Write-MinimalSmokeTest -Path (Join-Path $ProjectRoot "scripts\smoke-test.ps1") -ProjectName (Split-Path -Leaf $ProjectRoot) -CmsModule $CmsModule

    $smokeDoc = Join-Path $ProjectRoot "docs\development\smoke_test.md"
    if (Test-Path -LiteralPath $smokeDoc) {
        Replace-InTextFile -Path $smokeDoc -Replacements @(
            @{ Old = "CMS API 和 SDK API"; New = "CMS API" },
            @{ Old = "CMS/SDK"; New = "CMS" }
        )
        Remove-LineContaining -Path $smokeDoc -Needles @("SDK", "sdk")
    }

    $configurationGuide = Join-Path $ProjectRoot "docs\development\configuration_guide.md"
    if (Test-Path -LiteralPath $configurationGuide) {
        Remove-LineContaining -Path $configurationGuide -Needles @("## SDK 安全配置", "chaken.sdk.security", "SDK 默认", "SDK 签名", "apiKey", "x-api-key")
    }

    Remove-LineContaining -Path (Join-Path $ProjectRoot "docs\development\permission_standard.md") -Needles @("SDK", "x-api-key")
    Replace-InTextFile -Path (Join-Path $ProjectRoot "docs\development\observability_standard.md") -Replacements @(
        @{ Old = '`x-udid` 和 `x-api-key`'; New = '`x-udid`' },
        @{ Old = "x-udid 和 x-api-key"; New = "x-udid" }
    )

    Replace-InTextFile -Path (Join-Path $ProjectRoot "docs\development\version_compatibility.md") -Replacements @(
        @{ Old = "common/cms-api/sdk-api"; New = "common/cms-api" },
        @{ Old = "CMS 与 SDK 模块 package。"; New = "CMS 模块 package。" },
        @{ Old = "CMS API、SDK API"; New = "CMS API" }
    )
    Remove-LineContaining -Path (Join-Path $ProjectRoot "docs\development\module_development_guide.md") -Needles @("新增 SDK 接口", "sdk-api", "CMS 和 SDK", "CMS/SDK")
    Remove-LineContaining -Path (Join-Path $ProjectRoot "docs\development\production_stack.md") -Needles @("sdk-api.yml")
    Replace-InTextFile -Path (Join-Path $ProjectRoot "docs\development\persistence_template.md") -Replacements @(
        @{ Old = "CMS/SDK Filter"; New = "CMS Filter" },
        @{ Old = ' 或 ``x-api-key``'; New = "" },
        @{ Old = ' 或 `x-api-key`'; New = "" }
    )
}
