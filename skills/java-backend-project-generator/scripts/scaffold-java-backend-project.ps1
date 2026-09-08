param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectName,

    [Parameter(Mandatory = $true)]
    [string]$GroupId,

    [Parameter(Mandatory = $true)]
    [string]$BasePackage,

    [string]$OutputDir = ".",
    [string]$Version = "1.0.0-SNAPSHOT",
    [string]$JavaVersion = "17",
    [string]$SpringBootVersion = "4.0.5",
    [int]$CmsPort = 18080,
    [int]$SdkPort = 18081,
    [int]$NettyHttpPort = 18082,
    [int]$NettyTcpPort = 19090,
    [int]$NettyUdpPort = 19091,
    [string]$CommonModuleName = "",
    [string]$CmsModuleName = "",
    [string]$SdkModuleName = "",
    [string]$NettyModuleName = "",
    [ValidateSet("minimal", "standard")]
    [string]$Profile = "minimal",
    [switch]$IncludeNetty,
    [switch]$IncludeDbCrudExample
)

$ErrorActionPreference = "Stop"
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$Utf8Bom = New-Object System.Text.UTF8Encoding($true)
$SkillRoot = Split-Path -Parent $PSScriptRoot
$SkillsRoot = Split-Path -Parent $SkillRoot
$ApiStandardChecker = Join-Path $SkillsRoot "java-backend-api-standard\scripts\check_java_api_standard.py"
$ApiStandardContract = Join-Path $SkillsRoot "java-backend-api-standard\references\api-standard-contract.json"

function Assert-SupportedRuntimeVersion {
    param(
        [Parameter(Mandatory = $true)][string]$JavaVersion,
        [Parameter(Mandatory = $true)][string]$SpringBootVersion
    )

    $javaMajorMatch = [regex]::Match($JavaVersion, "^(\d+)")
    if (-not $javaMajorMatch.Success) {
        throw "无法识别 JavaVersion 主版本号。当前 base-template 只支持 Java 17+。收到 JavaVersion=$JavaVersion"
    }
    if ([int]$javaMajorMatch.Groups[1].Value -lt 17) {
        throw "当前 base-template 使用 record、String.isBlank 和 Jakarta API，只支持 Java 17+；不支持 JDK8/11 生成。收到 JavaVersion=$JavaVersion"
    }
    $script:EffectiveJavaVersion = $javaMajorMatch.Groups[1].Value

    $springBootMajorMatch = [regex]::Match($SpringBootVersion, "^(3|4)\.")
    if (-not $springBootMajorMatch.Success) {
        throw "当前 base-template 使用 jakarta.* 包，只支持 Spring Boot 3.x/4.x；不支持 Spring Boot 2.x 生成。收到 SpringBootVersion=$SpringBootVersion"
    }
    $script:EffectiveSpringBootMajor = $springBootMajorMatch.Groups[1].Value
}

Assert-SupportedRuntimeVersion -JavaVersion $JavaVersion -SpringBootVersion $SpringBootVersion

if ($EffectiveSpringBootMajor -eq "3") {
    $script:MyBatisPlusStarterArtifact = "mybatis-plus-spring-boot3-starter"
    $script:MyBatisPlusTestStarterArtifact = "mybatis-plus-spring-boot3-starter-test"
    $script:SpringdocOpenApiVersion = "2.8.14"
    $script:SpringBootFlywayPomDependencyXml = ""
    $script:SpringBootFlywayDocDependencyXml = ""
} else {
    $script:MyBatisPlusStarterArtifact = "mybatis-plus-spring-boot4-starter"
    $script:MyBatisPlusTestStarterArtifact = "mybatis-plus-spring-boot4-starter-test"
    $script:SpringdocOpenApiVersion = "3.0.2"
    $script:SpringBootFlywayPomDependencyXml = @"
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-flyway</artifactId>
    </dependency>
"@
    $script:SpringBootFlywayDocDependencyXml = @"
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-flyway</artifactId>
  </dependency>
"@
}

function To-ClassName {
    param([Parameter(Mandatory = $true)][string]$Name)
    $parts = $Name -split "[-_]"
    return ($parts | ForEach-Object {
        if ($_.Length -eq 0) {
            ""
        } else {
            $_.Substring(0, 1).ToUpperInvariant() + $_.Substring(1)
        }
    }) -join ""
}

function To-PackagePath {
    param([Parameter(Mandatory = $true)][string]$PackageName)
    return $PackageName.Replace(".", [System.IO.Path]::DirectorySeparatorChar)
}

function Replace-InTextFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][array]$Replacements
    )
    $content = [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
    foreach ($item in $Replacements) {
        $content = $content.Replace($item.Old, $item.New)
    }
    $encoding = if ([System.IO.Path]::GetExtension($Path) -eq ".ps1") { $Utf8Bom } else { $Utf8NoBom }
    [System.IO.File]::WriteAllText($Path, $content, $encoding)
}

function Move-DirectoryIfExists {
    param(
        [Parameter(Mandatory = $true)][string]$From,
        [Parameter(Mandatory = $true)][string]$To
    )
    if ($From -eq $To -or -not (Test-Path -LiteralPath $From)) {
        return
    }
    if (Test-Path -LiteralPath $To) {
        throw "移动目录失败，目标路径已存在：$To"
    }
    $parent = Split-Path -Parent $To
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent | Out-Null
    }
    Move-Item -LiteralPath $From -Destination $To
}

. (Join-Path $PSScriptRoot "generator-profile-helpers.ps1")

function Copy-TemplateTree {
    param(
        [Parameter(Mandatory = $true)][string]$From,
        [Parameter(Mandatory = $true)][string]$To,
        [Parameter(Mandatory = $true)][array]$Replacements
    )
    if (-not (Test-Path -LiteralPath $From)) {
        throw "模板路径不存在：$From"
    }
    Get-ChildItem -LiteralPath $From -Recurse -File | Where-Object {
        $_.FullName -notmatch "[\\/](target|dist|node_modules)[\\/]"
    } | ForEach-Object {
        $relative = $_.FullName.Substring($From.Length).TrimStart([System.IO.Path]::DirectorySeparatorChar)
        $destFile = Join-Path $To $relative
        $parent = Split-Path -Parent $destFile
        if (-not (Test-Path -LiteralPath $parent)) {
            New-Item -ItemType Directory -Path $parent | Out-Null
        }
        Copy-Item -LiteralPath $_.FullName -Destination $destFile -Force
        Replace-InTextFile -Path $destFile -Replacements $Replacements
    }
}

function Assert-ApiStandardContract {
    param(
        [Parameter(Mandatory = $true)][string]$ProjectRoot,
        [Parameter(Mandatory = $true)][string]$CommonModule,
        [Parameter(Mandatory = $true)][string]$PackagePath
    )
    if (-not (Test-Path -LiteralPath $ApiStandardContract)) {
        return
    }
    $contract = Get-Content -LiteralPath $ApiStandardContract -Encoding UTF8 -Raw | ConvertFrom-Json
    $signatureHeadersPath = Join-Path (Join-Path (Join-Path (Join-Path $ProjectRoot $CommonModule) "src\main\java") $PackagePath) "security\signature\SignatureHeaders.java"
    if (-not (Test-Path -LiteralPath $signatureHeadersPath)) {
        throw "共享契约校验失败，缺少签名头常量文件：$signatureHeadersPath"
    }
    $text = [System.IO.File]::ReadAllText($signatureHeadersPath, [System.Text.Encoding]::UTF8)
    foreach ($fragment in $contract.signatureHeaders.requiredConstantFragments) {
        if (-not $text.Contains($fragment)) {
            throw "共享契约校验失败，SignatureHeaders 缺少常量片段：$fragment"
        }
    }
    foreach ($header in $contract.requestHeaders.obsolete) {
        if ($text.Contains($header)) {
            throw "共享契约校验失败，SignatureHeaders 包含废弃请求头：$header"
        }
    }
}

function Insert-BeforeClosingDependencies {
    param(
        [Parameter(Mandatory = $true)][string]$PomPath,
        [Parameter(Mandatory = $true)][string]$DependencyXml
    )
    $content = [System.IO.File]::ReadAllText($PomPath, [System.Text.Encoding]::UTF8)
    $content = $content.Replace("  </dependencies>", "$DependencyXml`r`n  </dependencies>")
    [System.IO.File]::WriteAllText($PomPath, $content, $Utf8NoBom)
}

if ([string]::IsNullOrWhiteSpace($CommonModuleName)) {
    $CommonModuleName = "$ProjectName-common"
}
if ([string]::IsNullOrWhiteSpace($CmsModuleName)) {
    $CmsModuleName = "$ProjectName-cms-api"
}
if ([string]::IsNullOrWhiteSpace($SdkModuleName)) {
    $SdkModuleName = "$ProjectName-sdk-api"
}
if ([string]::IsNullOrWhiteSpace($NettyModuleName)) {
    $NettyModuleName = "$ProjectName-netty"
}

$skillRoot = Split-Path -Parent $PSScriptRoot
$templateRoot = Join-Path $skillRoot "assets\base-template"
if (-not (Test-Path -LiteralPath $templateRoot)) {
    throw "模板根目录不存在：$templateRoot"
}

$targetRoot = Join-Path $OutputDir $ProjectName
$targetFullPath = [System.IO.Path]::GetFullPath($targetRoot)
if (Test-Path -LiteralPath $targetFullPath) {
    throw "目标目录已存在，已拒绝覆盖：$targetFullPath"
}

New-Item -ItemType Directory -Path $targetFullPath | Out-Null
Get-ChildItem -LiteralPath $templateRoot -Recurse -File | Where-Object {
    $_.FullName -notmatch "[\\/](target|dist|node_modules)[\\/]"
} | ForEach-Object {
    $relative = $_.FullName.Substring($templateRoot.Length).TrimStart([System.IO.Path]::DirectorySeparatorChar)
    $destFile = Join-Path $targetFullPath $relative
    $parent = Split-Path -Parent $destFile
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent | Out-Null
    }
    Copy-Item -LiteralPath $_.FullName -Destination $destFile
}

Move-DirectoryIfExists (Join-Path $targetFullPath "chaken-ai-test-common") (Join-Path $targetFullPath $CommonModuleName)
Move-DirectoryIfExists (Join-Path $targetFullPath "chaken-ai-test-cms-api") (Join-Path $targetFullPath $CmsModuleName)
Move-DirectoryIfExists (Join-Path $targetFullPath "chaken-ai-test-sdk-api") (Join-Path $targetFullPath $SdkModuleName)
Move-DirectoryIfExists (Join-Path $targetFullPath "chaken-ai-test-netty") (Join-Path $targetFullPath $NettyModuleName)

$oldCmsApplication = "ChakenAiTestCmsApiApplication"
$oldSdkApplication = "ChakenAiTestSdkApiApplication"
$oldNettyApplication = "ChakenAiTestNettyApplication"
$newCmsApplication = "$(To-ClassName $CmsModuleName)Application"
$newSdkApplication = "$(To-ClassName $SdkModuleName)Application"
$newNettyApplication = "$(To-ClassName $NettyModuleName)Application"

$basePackageToken = "__JAVA_BACKEND_GENERATOR_BASE_PACKAGE__"
$replacements = @(
    @{ Old = $oldCmsApplication; New = $newCmsApplication },
    @{ Old = $oldSdkApplication; New = $newSdkApplication },
    @{ Old = $oldNettyApplication; New = $newNettyApplication },
    @{ Old = "chaken-ai-test-common"; New = $CommonModuleName },
    @{ Old = "chaken-ai-test-cms-api"; New = $CmsModuleName },
    @{ Old = "chaken-ai-test-sdk-api"; New = $SdkModuleName },
    @{ Old = "chaken-ai-test-netty"; New = $NettyModuleName },
    @{ Old = "chaken-ai-test"; New = $ProjectName },
    @{ Old = "com.chaken.ai.test"; New = $basePackageToken },
    @{ Old = "com.chaken.ai"; New = $GroupId },
    @{ Old = $basePackageToken; New = $BasePackage },
    @{ Old = "1.0.0-SNAPSHOT"; New = $Version },
    @{ Old = "<java.version>17</java.version>"; New = "<java.version>$EffectiveJavaVersion</java.version>" },
    @{ Old = "<spring-boot.version>4.0.5</spring-boot.version>"; New = "<spring-boot.version>$SpringBootVersion</spring-boot.version>" },
    @{ Old = "mybatis-plus-spring-boot4-starter-test"; New = $MyBatisPlusTestStarterArtifact },
    @{ Old = "mybatis-plus-spring-boot4-starter"; New = $MyBatisPlusStarterArtifact },
    @{ Old = "<version>3.0.2</version>"; New = "<version>$SpringdocOpenApiVersion</version>" },
    @{ Old = "  <dependency>`r`n    <groupId>org.springframework.boot</groupId>`r`n    <artifactId>spring-boot-flyway</artifactId>`r`n  </dependency>"; New = $SpringBootFlywayDocDependencyXml },
    @{ Old = "  <dependency>`n    <groupId>org.springframework.boot</groupId>`n    <artifactId>spring-boot-flyway</artifactId>`n  </dependency>"; New = $SpringBootFlywayDocDependencyXml },
    @{ Old = "    <dependency>`r`n      <groupId>org.springframework.boot</groupId>`r`n      <artifactId>spring-boot-flyway</artifactId>`r`n    </dependency>"; New = $SpringBootFlywayDocDependencyXml },
    @{ Old = "    <dependency>`n      <groupId>org.springframework.boot</groupId>`n      <artifactId>spring-boot-flyway</artifactId>`n    </dependency>"; New = $SpringBootFlywayDocDependencyXml },
    @{ Old = "port: 18080"; New = "port: $CmsPort" },
    @{ Old = "port: 18081"; New = "port: $SdkPort" },
    @{ Old = "port: 18082"; New = "port: $NettyHttpPort" },
    @{ Old = "port: 19090"; New = "port: $NettyTcpPort" },
    @{ Old = "port: 19091"; New = "port: $NettyUdpPort" }
)

$textExtensions = @(".java", ".xml", ".yml", ".yaml", ".md", ".ps1", ".cmd", ".sh", ".properties", ".editorconfig", ".gitattributes")
Get-ChildItem -LiteralPath $targetFullPath -Recurse -File | Where-Object {
    $textExtensions -contains $_.Extension -or $_.Name -in @("AGENTS.md", "README.md")
} | ForEach-Object {
    Replace-InTextFile -Path $_.FullName -Replacements $replacements
}

$oldPackagePath = To-PackagePath "com.chaken.ai.test"
$newPackagePath = To-PackagePath $BasePackage
foreach ($moduleName in @($CommonModuleName, $CmsModuleName, $SdkModuleName, $NettyModuleName)) {
    foreach ($sourceSet in @("src\main\java", "src\test\java")) {
        $javaRoot = Join-Path (Join-Path $targetFullPath $moduleName) $sourceSet
        if (-not (Test-Path -LiteralPath $javaRoot)) {
            continue
        }
        $oldPackageDir = Join-Path $javaRoot $oldPackagePath
        $newPackageDir = Join-Path $javaRoot $newPackagePath
        Move-DirectoryIfExists $oldPackageDir $newPackageDir
        Remove-EmptyParentDirectories $oldPackageDir $javaRoot
    }
}

$cmsOldFile = Get-ChildItem -LiteralPath (Join-Path $targetFullPath $CmsModuleName) -Recurse -File -Filter "$oldCmsApplication.java" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($cmsOldFile) {
    Rename-Item -LiteralPath $cmsOldFile.FullName -NewName "$newCmsApplication.java"
}
$sdkOldFile = Get-ChildItem -LiteralPath (Join-Path $targetFullPath $SdkModuleName) -Recurse -File -Filter "$oldSdkApplication.java" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($sdkOldFile) {
    Rename-Item -LiteralPath $sdkOldFile.FullName -NewName "$newSdkApplication.java"
}
$nettyOldFile = Get-ChildItem -LiteralPath (Join-Path $targetFullPath $NettyModuleName) -Recurse -File -Filter "$oldNettyApplication.java" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($nettyOldFile) {
    Rename-Item -LiteralPath $nettyOldFile.FullName -NewName "$newNettyApplication.java"
}

if (-not $IncludeNetty) {
    Remove-DirectoryInsideRoot -Root $targetFullPath -Path (Join-Path $targetFullPath $NettyModuleName)
    $pomPath = Join-Path $targetFullPath "pom.xml"
    $pomContent = [System.IO.File]::ReadAllText($pomPath, [System.Text.Encoding]::UTF8)
    $pomContent = $pomContent.Replace("    <module>$NettyModuleName</module>`r`n", "")
    $pomContent = $pomContent.Replace("    <module>$NettyModuleName</module>`n", "")
    [System.IO.File]::WriteAllText($pomPath, $pomContent, $Utf8NoBom)
}

if ($Profile -eq "minimal") {
    Apply-MinimalProfile -ProjectRoot $targetFullPath -SdkModule $SdkModuleName -CmsModule $CmsModuleName -CommonModule $CommonModuleName
}

if ($IncludeDbCrudExample) {
    $cmsModuleRoot = Join-Path $targetFullPath $CmsModuleName
    $cmsJavaRoot = Join-Path (Join-Path $cmsModuleRoot "src\main\java") $newPackagePath
    $cmsTestJavaRoot = Join-Path (Join-Path $cmsModuleRoot "src\test\java") $newPackagePath
    $cmsResourcesRoot = Join-Path $cmsModuleRoot "src\main\resources"
    $cmsTestResourcesRoot = Join-Path $cmsModuleRoot "src\test\resources"
    $sampleItemRoot = Join-Path $cmsJavaRoot "cms\sampleitem"
    $sampleItemTestRoot = Join-Path $cmsTestJavaRoot "cms\sampleitem"
    $crudTemplateRoot = Join-Path $targetFullPath "docs\templates\crud\mybatis-plus"

    if (Test-Path -LiteralPath $sampleItemRoot) {
        Remove-Item -LiteralPath $sampleItemRoot -Recurse -Force
    }
    if (Test-Path -LiteralPath $sampleItemTestRoot) {
        Remove-Item -LiteralPath $sampleItemTestRoot -Recurse -Force
    }

    $templateReplacements = @(
        @{ Old = "{{basePackage}}"; New = $BasePackage },
        @{ Old = "sample-item"; New = "sample-item" }
    )
    foreach ($folder in @("controller", "converter", "dto", "entity", "mapper", "service")) {
        Copy-TemplateTree -From (Join-Path $crudTemplateRoot $folder) -To (Join-Path $sampleItemRoot $folder) -Replacements $templateReplacements
    }
    Copy-TemplateTree -From (Join-Path $crudTemplateRoot "mapper-xml") -To (Join-Path $cmsResourcesRoot "mapper\cms\sampleitem") -Replacements $templateReplacements
    Copy-TemplateTree -From (Join-Path $crudTemplateRoot "db\migration") -To (Join-Path $cmsResourcesRoot "db\migration") -Replacements $templateReplacements
    Copy-TemplateTree -From (Join-Path $crudTemplateRoot "tests\integration") -To $sampleItemTestRoot -Replacements $templateReplacements
    Copy-TemplateTree -From (Join-Path $crudTemplateRoot "tests\resources") -To $cmsTestResourcesRoot -Replacements $templateReplacements

    $cmsPom = Join-Path $cmsModuleRoot "pom.xml"
    $cmsPomContent = [System.IO.File]::ReadAllText($cmsPom, [System.Text.Encoding]::UTF8)
    if (-not $cmsPomContent.Contains("springdoc-openapi-starter-webmvc-api")) {
        $crudDependencies = @"
    <dependency>
      <groupId>org.springdoc</groupId>
      <artifactId>springdoc-openapi-starter-webmvc-api</artifactId>
      <version>$SpringdocOpenApiVersion</version>
    </dependency>
"@
        Insert-BeforeClosingDependencies -PomPath $cmsPom -DependencyXml $crudDependencies
    }

    $cmsDevConfig = Join-Path $cmsResourcesRoot "application-dev.yml"
    $devDatasource = @"

spring:
  datasource:
    url: jdbc:h2:mem:sample_item;MODE=MySQL;DATABASE_TO_LOWER=TRUE;CASE_INSENSITIVE_IDENTIFIERS=TRUE;DB_CLOSE_DELAY=-1
    driver-class-name: org.h2.Driver
    username: sa
    password:
  flyway:
    enabled: true
    locations: classpath:db/migration

mybatis-plus:
  mapper-locations: classpath*:/mapper/**/*.xml
  configuration:
    map-underscore-to-camel-case: true
"@
    $cmsDevContent = [System.IO.File]::ReadAllText($cmsDevConfig, [System.Text.Encoding]::UTF8)
    if (-not $cmsDevContent.Contains("spring:`r`n  datasource:") -and -not $cmsDevContent.Contains("spring:`n  datasource:")) {
        [System.IO.File]::WriteAllText($cmsDevConfig, $cmsDevContent.TrimEnd() + $devDatasource + "`r`n", $Utf8NoBom)
    }
}

Assert-ApiStandardContract -ProjectRoot $targetFullPath -CommonModule $CommonModuleName -PackagePath $newPackagePath

Write-Host "已创建 Java 后端项目：$targetFullPath"
Write-Host "Profile: $Profile"
Write-Host "模块："
Write-Host "  $CommonModuleName"
Write-Host "  $CmsModuleName"
if ($Profile -ne "minimal") {
    Write-Host "  $SdkModuleName"
}
if ($IncludeNetty) {
    Write-Host "  $NettyModuleName"
}
Write-Host ""
Write-Host "建议执行以下验证："
Write-Host "  cd `"$targetFullPath`""
Write-Host "  mvn -q -DskipTests compile"
Write-Host "  mvn -q -pl $CmsModuleName -am -DskipTests package"
if ($Profile -ne "minimal") {
    Write-Host "  mvn -q -pl $SdkModuleName -am -DskipTests package"
}
if ($IncludeNetty) {
    Write-Host "  mvn -q -pl $NettyModuleName -am -DskipTests package"
}
Write-Host "  py `"$ApiStandardChecker`" `"$targetFullPath`" --profile $Profile --json --fail-on-error"
Write-Host "  .\scripts\smoke-test.ps1 -Profile $Profile"
if ($IncludeDbCrudExample) {
    Write-Host "  mvn -q -pl $CmsModuleName -am -Dtest='*IntegrationTest' `"-Dsurefire.failIfNoSpecifiedTests=false`" test"
}
