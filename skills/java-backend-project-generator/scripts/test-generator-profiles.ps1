param(
    [string]$OutputDir = "",
    [string]$PythonCommand = "py",
    [string]$MavenCommand = "",
    [switch]$SkipCompile,
    [switch]$KeepOutput
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:PYTHONUTF8 = "1"

$scriptRoot = $PSScriptRoot
$skillRoot = Split-Path -Parent $scriptRoot
$skillsRoot = Split-Path -Parent $skillRoot
$scaffold = Join-Path $scriptRoot "scaffold-java-backend-project.ps1"
$checker = Join-Path $skillsRoot "java-backend-api-standard\scripts\check_java_api_standard.py"
$nettySkillChecker = Join-Path $skillsRoot "netty-handler-dispatcher\scripts\check_netty_handler_dispatcher_skill.py"

if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $OutputDir = Join-Path ([System.IO.Path]::GetTempPath()) "java-backend-project-generator-profile-tests"
}

if (-not (Test-Path -LiteralPath $scaffold)) {
    throw "生成器脚本不存在：$scaffold"
}
if (-not (Test-Path -LiteralPath $checker)) {
    throw "API 标准检查器不存在：$checker"
}
if (-not (Test-Path -LiteralPath $nettySkillChecker)) {
    throw "Netty skill 检查器不存在：$nettySkillChecker"
}

$runRoot = Join-Path $OutputDir ("run-" + [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds())
New-Item -ItemType Directory -Force -Path $runRoot | Out-Null
$succeeded = $false

function Resolve-MavenCommand {
    if (-not [string]::IsNullOrWhiteSpace($MavenCommand) -and (Test-Path -LiteralPath $MavenCommand)) {
        return $MavenCommand
    }
    $mvnCmd = Get-Command "mvn.cmd" -ErrorAction SilentlyContinue
    if ($null -ne $mvnCmd) {
        return $mvnCmd.Source
    }
    $mvn = Get-Command "mvn" -ErrorAction SilentlyContinue
    if ($null -ne $mvn) {
        return $mvn.Source
    }
    throw "未找到 Maven 命令，请通过 -MavenCommand 指定 mvn.cmd 路径"
}

function Invoke-Checker {
    param(
        [Parameter(Mandatory = $true)][string]$ProjectRoot,
        [Parameter(Mandatory = $true)][ValidateSet("minimal", "standard")][string]$Profile
    )
    $output = & $PythonCommand $checker $ProjectRoot --profile $Profile --json --fail-on-error
    $output | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "checker 失败：profile=$Profile project=$ProjectRoot"
    }
    $findings = @($output | ConvertFrom-Json)
    foreach ($finding in $findings) {
        if ($finding.rule -eq "business-exception-control-flow") {
            throw "checker 发现生成器产物仍存在禁止 warning：$($finding.rule) $($finding.file):$($finding.line)"
        }
    }
}

function Invoke-MavenCompile {
    param([Parameter(Mandatory = $true)][string]$ProjectRoot)
    if ($SkipCompile) {
        Write-Host "跳过 Maven compile：$ProjectRoot"
        return
    }
    $mavenExe = Resolve-MavenCommand
    Push-Location $ProjectRoot
    try {
        & $mavenExe -q -DskipTests compile
        if ($LASTEXITCODE -ne 0) {
            throw "Maven compile 失败：project=$ProjectRoot exit=$LASTEXITCODE"
        }
    } finally {
        Pop-Location
    }
}

function Invoke-NettySkillChecker {
    $output = & $PythonCommand $nettySkillChecker
    $output | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "Netty skill 检查器失败：$nettySkillChecker"
    }
}

function Assert-NoExpectedRejectionErrorStack {
    param([Parameter(Mandatory = $true)][string[]]$Roots)
    $forbidden = @(
        'log.error("sdk_signature_auth_failed',
        'log.error("netty_tcp_auth_failed',
        'log.error("netty_udp_auth_failed',
        'log.error("cms_signature_timestamp_invalid',
        'log.error("signature_timestamp_invalid'
    )
    foreach ($root in $Roots) {
        if (-not (Test-Path -LiteralPath $root)) {
            continue
        }
        $files = Get-ChildItem -LiteralPath $root -Recurse -File | Where-Object { $_.Extension -eq ".java" }
        foreach ($file in $files) {
            $text = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)
            foreach ($needle in $forbidden) {
                if ($text.Contains($needle)) {
                    throw "可预期鉴权/签名拒绝不应记录为 log.error 堆栈：$($file.FullName) needle=$needle"
                }
            }
        }
    }
}

function Assert-NettyProtocolErrorsSeparated {
    param([Parameter(Mandatory = $true)][string[]]$Roots)
    $required = @(
        "JsonProcessingException",
        "protocol_invalid",
        'responseWriter.fail(reqid, "AC0001", "协议格式错误")'
    )
    $forbidden = @(
        'catch (Exception ex) {
            context.writeAndFlush(responseWriter.fail(reqid, "AC0001", "协议格式错误")',
        'catch (Exception ex) {
            writeError(context, packet, responseWriter.fail(reqid, "AC0001", "协议格式错误"))'
    )
    foreach ($root in $Roots) {
        if (-not (Test-Path -LiteralPath $root)) {
            continue
        }
        $files = Get-ChildItem -LiteralPath $root -Recurse -File | Where-Object { $_.Name -in @("NettyTcpMessageHandler.java", "NettyUdpMessageHandler.java") }
        foreach ($file in $files) {
            $text = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)
            $normalizedText = $text -replace "`r`n", "`n"
            foreach ($needle in $required) {
                if (-not $text.Contains($needle)) {
                    throw "Netty 协议格式错误应单独捕获并用 info 记录：$($file.FullName) missing=$needle"
                }
            }
            foreach ($needle in $forbidden) {
                if ($normalizedText.Contains($needle)) {
                    throw "Netty 可预期协议格式错误不应混入 catch-all error 堆栈：$($file.FullName) needle=$needle"
                }
            }
        }
    }
}

function Assert-TextOrder {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Before,
        [Parameter(Mandatory = $true)][string]$After,
        [Parameter(Mandatory = $true)][string]$Message
    )
    $text = [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
    $beforeIndex = $text.IndexOf($Before, [StringComparison]::Ordinal)
    $afterIndex = $text.IndexOf($After, [StringComparison]::Ordinal)
    if ($beforeIndex -lt 0 -or $afterIndex -lt 0 -or $beforeIndex -gt $afterIndex) {
        throw "$Message：$Path"
    }
}

function Assert-NettyUnexpectedExceptionLoggedBeforeResponse {
    param([Parameter(Mandatory = $true)][string]$ProjectRoot)
    $nettyModule = Get-ChildItem -LiteralPath $ProjectRoot -Directory | Where-Object { $_.Name -like "*-netty" } | Select-Object -First 1
    if ($null -eq $nettyModule) {
        throw "未找到 Netty 模块：$ProjectRoot"
    }
    $tcpHandler = Get-ChildItem -LiteralPath $nettyModule.FullName -Recurse -File -Filter "NettyTcpMessageHandler.java" | Select-Object -First 1
    $udpHandler = Get-ChildItem -LiteralPath $nettyModule.FullName -Recurse -File -Filter "NettyUdpMessageHandler.java" | Select-Object -First 1
    if ($null -eq $tcpHandler -or $null -eq $udpHandler) {
        throw "Netty handler 文件缺失：$ProjectRoot"
    }
    Assert-TextOrder `
        -Path $tcpHandler.FullName `
        -Before 'log.error("netty_tcp_message_failed' `
        -After 'context.writeAndFlush(responseWriter.fail(reqid, "AC9999", "系统异常")' `
        -Message "TCP catch-all 程序异常应先 log.error 记录原始异常，再尝试写兜底响应"
    Assert-TextOrder `
        -Path $udpHandler.FullName `
        -Before 'log.error("netty_udp_message_failed' `
        -After 'writeError(context, packet, responseWriter.fail(reqid, "AC9999", "系统异常"))' `
        -Message "UDP catch-all 程序异常应先 log.error 记录原始异常，再尝试写兜底响应"
}

function Assert-ReqidNullSafety {
    param([Parameter(Mandatory = $true)][string]$ProjectRoot)
    $apiResult = Get-ChildItem -LiteralPath $ProjectRoot -Recurse -File -Filter "ApiResult.java" | Select-Object -First 1
    if ($null -eq $apiResult) {
        throw "ApiResult.java 缺失：$ProjectRoot"
    }
    Assert-FileContains `
        -Path $apiResult.FullName `
        -Needles @("reqidOrEmpty", "this.reqid = reqidOrEmpty(reqid)", "setReqid(String reqid)")

    $nettyWriter = Get-ChildItem -LiteralPath $ProjectRoot -Recurse -File -Filter "NettyResponseWriter.java" | Select-Object -First 1
    if ($null -ne $nettyWriter) {
        Assert-FileContains `
            -Path $nettyWriter.FullName `
            -Needles @("java.util.UUID", "reqidOrGenerated", "server-", "UUID.randomUUID().toString()")
    }
}

function Assert-PathMissing {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (Test-Path -LiteralPath $Path) {
        throw "不应存在路径：$Path"
    }
}

function Assert-PathExists {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "路径应存在但不存在：$Path"
    }
}

function Assert-FileContains {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string[]]$Needles
    )
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "文件应存在但不存在：$Path"
    }
    $text = [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
    foreach ($needle in $Needles) {
        if (-not $text.Contains($needle)) {
            throw "文件缺少预期内容：$Path needle=$needle"
        }
    }
}

function Assert-TextDoesNotContain {
    param(
        [Parameter(Mandatory = $true)][string[]]$Roots,
        [Parameter(Mandatory = $true)][string[]]$Needles
    )
    foreach ($root in $Roots) {
        if (-not (Test-Path -LiteralPath $root)) {
            continue
        }
        $files = Get-ChildItem -LiteralPath $root -Recurse -File
        foreach ($file in $files) {
            $text = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)
            foreach ($needle in $Needles) {
                if ($text.Contains($needle)) {
                    throw "文件仍包含不应出现的内容：$($file.FullName) needle=$needle"
                }
            }
        }
    }
}

function Assert-ProductionReadyRejected {
    $rejected = $false
    try {
        & $scaffold `
            -ProjectName "eval-production" `
            -GroupId "com.example.evalproduction" `
            -BasePackage "com.example.evalproduction" `
            -OutputDir $runRoot `
            -Profile production-ready | Out-Null
    } catch {
        $message = $_.Exception.Message
        if ($message -match "ValidateSet" -or $message -match "无法对参数.*Profile" -or $message -match "Cannot validate argument") {
            $rejected = $true
        } else {
            throw
        }
    }
    if (-not $rejected) {
        throw "production-ready 不应作为生成器运行 profile 被接受"
    }
}

try {
    $minimalRoot = Join-Path $runRoot "eval-minimal"
    $defaultRoot = Join-Path $runRoot "eval-default"
    $standardRoot = Join-Path $runRoot "eval-standard"
    $boot3CrudRoot = Join-Path $runRoot "eval-boot3-crud"
    $nettyRoot = Join-Path $runRoot "eval-netty"

    & $scaffold `
        -ProjectName "eval-minimal" `
        -GroupId "com.example.evalminimal" `
        -BasePackage "com.example.evalminimal" `
        -OutputDir $runRoot `
        -Profile minimal | Out-Host

    Assert-PathMissing -Path (Join-Path $minimalRoot "eval-minimal-sdk-api")
    Assert-PathMissing -Path (Join-Path $minimalRoot "eval-minimal-netty")
    Assert-TextDoesNotContain `
        -Roots @((Join-Path $minimalRoot "docs"), (Join-Path $minimalRoot "scripts")) `
        -Needles @("sdk-api", "dev-sdk-", "test-sdk-", "SdkModuleName", "x-api-key")
    Invoke-Checker -ProjectRoot $minimalRoot -Profile minimal
    Assert-ReqidNullSafety -ProjectRoot $minimalRoot
    Invoke-MavenCompile -ProjectRoot $minimalRoot

    & $scaffold `
        -ProjectName "eval-default" `
        -GroupId "com.example.evaldefault" `
        -BasePackage "com.example.evaldefault" `
        -OutputDir $runRoot | Out-Host

    Assert-PathExists -Path (Join-Path $defaultRoot "eval-default-common")
    Assert-PathExists -Path (Join-Path $defaultRoot "eval-default-cms-api")
    Assert-PathMissing -Path (Join-Path $defaultRoot "eval-default-sdk-api")
    Assert-PathMissing -Path (Join-Path $defaultRoot "eval-default-netty")
    Invoke-Checker -ProjectRoot $defaultRoot -Profile minimal
    Assert-ReqidNullSafety -ProjectRoot $defaultRoot
    Invoke-MavenCompile -ProjectRoot $defaultRoot

    & $scaffold `
        -ProjectName "eval-standard" `
        -GroupId "com.example.evalstandard" `
        -BasePackage "com.example.evalstandard" `
        -OutputDir $runRoot `
        -Profile standard | Out-Host

    foreach ($module in @("eval-standard-common", "eval-standard-cms-api", "eval-standard-sdk-api")) {
        $path = Join-Path $standardRoot $module
        if (-not (Test-Path -LiteralPath $path)) {
            throw "standard profile 缺少模块：$module"
        }
    }
    Assert-PathMissing -Path (Join-Path $standardRoot "eval-standard-netty")
    Invoke-Checker -ProjectRoot $standardRoot -Profile standard
    Assert-ReqidNullSafety -ProjectRoot $standardRoot
    Invoke-MavenCompile -ProjectRoot $standardRoot

    & $scaffold `
        -ProjectName "eval-boot3-crud" `
        -GroupId "com.example.evalboot3crud" `
        -BasePackage "com.example.evalboot3crud" `
        -OutputDir $runRoot `
        -SpringBootVersion 3.3.7 `
        -JavaVersion 17 `
        -Profile standard `
        -IncludeDbCrudExample | Out-Host

    $boot3CrudCmsPom = Join-Path $boot3CrudRoot "eval-boot3-crud-cms-api\pom.xml"
    Assert-FileContains `
        -Path $boot3CrudCmsPom `
        -Needles @("mybatis-plus-spring-boot3-starter", "mybatis-plus-spring-boot3-starter-test", "springdoc-openapi-starter-webmvc-api", "<version>2.8.14</version>")
    Assert-TextDoesNotContain `
        -Roots @($boot3CrudRoot) `
        -Needles @("mybatis-plus-spring-boot4-starter", "mybatis-plus-spring-boot4-starter-test", "spring-boot-flyway", "<version>3.0.2</version>")
    Invoke-Checker -ProjectRoot $boot3CrudRoot -Profile standard
    Assert-ReqidNullSafety -ProjectRoot $boot3CrudRoot
    Invoke-MavenCompile -ProjectRoot $boot3CrudRoot

    & $scaffold `
        -ProjectName "eval-netty" `
        -GroupId "com.example.evalnetty" `
        -BasePackage "com.example.evalnetty" `
        -OutputDir $runRoot `
        -Profile standard `
        -IncludeNetty | Out-Host

    foreach ($module in @("eval-netty-common", "eval-netty-cms-api", "eval-netty-sdk-api", "eval-netty-netty")) {
        Assert-PathExists -Path (Join-Path $nettyRoot $module)
    }
    Invoke-NettySkillChecker
    Assert-NoExpectedRejectionErrorStack -Roots @($nettyRoot)
    Assert-NettyProtocolErrorsSeparated -Roots @($nettyRoot)
    Assert-NettyUnexpectedExceptionLoggedBeforeResponse -ProjectRoot $nettyRoot
    Invoke-Checker -ProjectRoot $nettyRoot -Profile standard
    Assert-ReqidNullSafety -ProjectRoot $nettyRoot
    Invoke-MavenCompile -ProjectRoot $nettyRoot
    Assert-ProductionReadyRejected

    $succeeded = $true
    Write-Host "通过：生成器 profile 回归验证完成，输出目录：$runRoot"
} finally {
    if ($succeeded -and -not $KeepOutput) {
        Remove-Item -LiteralPath $runRoot -Recurse -Force
        Write-Host "已清理生成器 profile 回归输出目录：$runRoot"
    } elseif (-not $succeeded) {
        Write-Host "生成器 profile 回归失败，已保留输出目录便于排查：$runRoot"
    } else {
        Write-Host "已按 -KeepOutput 保留生成器 profile 回归输出目录：$runRoot"
    }
}
