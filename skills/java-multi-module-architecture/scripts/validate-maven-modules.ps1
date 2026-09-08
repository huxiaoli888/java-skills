param(
    [string]$ProjectDir = ".",
    [switch]$RunCompile
)

$ErrorActionPreference = "Stop"

function Fail {
    param([string]$Message)
    Write-Error $Message
    exit 1
}

function Read-XmlFile {
    param([Parameter(Mandatory = $true)][string]$Path)
    [xml](Get-Content -LiteralPath $Path -Raw -Encoding UTF8)
}

$root = [System.IO.Path]::GetFullPath($ProjectDir)
$pomPath = Join-Path $root "pom.xml"
if (-not (Test-Path -LiteralPath $pomPath)) {
    Fail "Parent POM not found: $pomPath"
}

$pom = Read-XmlFile $pomPath
$ns = New-Object System.Xml.XmlNamespaceManager($pom.NameTable)
$ns.AddNamespace("m", "http://maven.apache.org/POM/4.0.0")

$packaging = $pom.SelectSingleNode("/m:project/m:packaging", $ns)
if (-not $packaging -or $packaging.InnerText -ne "pom") {
    Fail "Parent POM must use <packaging>pom</packaging>"
}

$modules = @($pom.SelectNodes("/m:project/m:modules/m:module", $ns) | ForEach-Object { $_.InnerText.Trim() } | Where-Object { $_ })
if ($modules.Count -eq 0) {
    Fail "Parent POM does not declare any <modules>"
}

$errors = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]
$artifactToModule = @{}
$moduleDeps = @{}

foreach ($module in $modules) {
    $moduleDir = Join-Path $root $module
    $childPomPath = Join-Path $moduleDir "pom.xml"
    if (-not (Test-Path -LiteralPath $moduleDir)) {
        $errors.Add("Module directory does not exist: $module")
        continue
    }
    if (-not (Test-Path -LiteralPath $childPomPath)) {
        $errors.Add("Module is missing pom.xml: $module")
        continue
    }

    $child = Read-XmlFile $childPomPath
    $childNs = New-Object System.Xml.XmlNamespaceManager($child.NameTable)
    $childNs.AddNamespace("m", "http://maven.apache.org/POM/4.0.0")

    $artifactId = $child.SelectSingleNode("/m:project/m:artifactId", $childNs)
    if (-not $artifactId -or [string]::IsNullOrWhiteSpace($artifactId.InnerText)) {
        $errors.Add("Module artifactId is missing: $module")
        continue
    }
    $artifactToModule[$artifactId.InnerText.Trim()] = $module

    $parentArtifact = $child.SelectSingleNode("/m:project/m:parent/m:artifactId", $childNs)
    if (-not $parentArtifact) {
        $warnings.Add("Module does not declare parent: $module")
    }

    $depArtifactIds = @($child.SelectNodes("/m:project/m:dependencies/m:dependency/m:artifactId", $childNs) | ForEach-Object { $_.InnerText.Trim() } | Where-Object { $_ })
    $moduleDeps[$module] = $depArtifactIds

    $bootPlugin = $child.SelectSingleNode("/m:project/m:build/m:plugins/m:plugin[m:artifactId='spring-boot-maven-plugin']", $childNs)
    $mainClasses = @(Get-ChildItem -LiteralPath $moduleDir -Recurse -Filter "*.java" -ErrorAction SilentlyContinue | Select-String -Pattern "@SpringBootApplication" -List)
    if ($bootPlugin -and $mainClasses.Count -eq 0) {
        $warnings.Add("Module declares spring-boot-maven-plugin but no @SpringBootApplication was found: $module")
    }
    if (-not $bootPlugin -and $mainClasses.Count -gt 0) {
        $warnings.Add("Module has @SpringBootApplication but no spring-boot-maven-plugin: $module")
    }
}

foreach ($module in $moduleDeps.Keys) {
    foreach ($depArtifact in $moduleDeps[$module]) {
        if ($artifactToModule.ContainsKey($depArtifact)) {
            $targetModule = $artifactToModule[$depArtifact]
            if ($module -match "common|contract" -and $targetModule -notmatch "common|contract") {
                $errors.Add("Common/contract modules should not depend on business/deployable modules: $module -> $targetModule")
            }
        }
    }
}

if ($errors.Count -gt 0) {
    Write-Host "Maven multi-module validation failed:" -ForegroundColor Red
    $errors | ForEach-Object { Write-Host "ERROR: $_" -ForegroundColor Red }
    if ($warnings.Count -gt 0) {
        $warnings | ForEach-Object { Write-Host "WARN: $_" -ForegroundColor Yellow }
    }
    exit 1
}

Write-Host "Maven multi-module validation passed." -ForegroundColor Green
if ($warnings.Count -gt 0) {
    $warnings | ForEach-Object { Write-Host "WARN: $_" -ForegroundColor Yellow }
}

if ($RunCompile) {
    Push-Location $root
    try {
        mvn -q -DskipTests compile
    }
    finally {
        Pop-Location
    }
}
