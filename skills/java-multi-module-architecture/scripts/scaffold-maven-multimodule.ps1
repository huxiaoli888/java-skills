param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectName,

    [Parameter(Mandatory = $true)]
    [string]$GroupId,

    [Parameter(Mandatory = $true)]
    [string]$BasePackage,

    [string]$Version = "1.0.0-SNAPSHOT",
    [string]$JavaVersion = "17",
    [string]$SpringBootVersion = "4.0.5",

    [Parameter(Mandatory = $true)]
    [string[]]$Modules,

    [string[]]$DeployableModules = @(),
    [string]$OutputDir = "."
)

$ErrorActionPreference = "Stop"
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function Write-Utf8File {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Content
    )
    if (Test-Path -LiteralPath $Path) {
        throw "File already exists, refusing to overwrite: $Path"
    }
    $parent = Split-Path -Parent $Path
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent | Out-Null
    }
    [System.IO.File]::WriteAllText((Resolve-OrCreatePath $Path), $Content, $Utf8NoBom)
}

function Resolve-OrCreatePath {
    param([Parameter(Mandatory = $true)][string]$Path)
    $full = [System.IO.Path]::GetFullPath($Path)
    return $full
}

function To-PackagePath {
    param([Parameter(Mandatory = $true)][string]$PackageName)
    return $PackageName.Replace(".", [System.IO.Path]::DirectorySeparatorChar)
}

function To-ClassName {
    param([Parameter(Mandatory = $true)][string]$ModuleName)
    $parts = $ModuleName -split "[-_]"
    return (($parts | ForEach-Object {
        if ($_.Length -eq 0) { "" } else { $_.Substring(0, 1).ToUpperInvariant() + $_.Substring(1) }
    }) -join "") + "Application"
}

$projectRoot = Join-Path $OutputDir $ProjectName
if (Test-Path -LiteralPath $projectRoot) {
    throw "Target directory already exists, refusing to overwrite: $projectRoot"
}

Write-Host "Creating Java Maven multi-module project: $projectRoot"
Write-Host "Modules: $($Modules -join ', ')"
Write-Host "Deployable modules: $($DeployableModules -join ', ')"

New-Item -ItemType Directory -Path $projectRoot | Out-Null

$moduleLines = ($Modules | ForEach-Object { "    <module>$_</module>" }) -join "`n"
$parentPom = @"
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>

  <groupId>$GroupId</groupId>
  <artifactId>$ProjectName</artifactId>
  <version>$Version</version>
  <packaging>pom</packaging>

  <modules>
$moduleLines
  </modules>

  <properties>
    <java.version>$JavaVersion</java.version>
    <spring-boot.version>$SpringBootVersion</spring-boot.version>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <project.reporting.outputEncoding>UTF-8</project.reporting.outputEncoding>
    <maven.compiler.encoding>UTF-8</maven.compiler.encoding>
  </properties>

  <dependencyManagement>
    <dependencies>
      <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-dependencies</artifactId>
        <version>`$`{spring-boot.version`}</version>
        <type>pom</type>
        <scope>import</scope>
      </dependency>
    </dependencies>
  </dependencyManagement>

  <build>
    <pluginManagement>
      <plugins>
        <plugin>
          <groupId>org.apache.maven.plugins</groupId>
          <artifactId>maven-compiler-plugin</artifactId>
          <version>3.13.0</version>
          <configuration>
            <release>`$`{java.version`}</release>
            <encoding>UTF-8</encoding>
          </configuration>
        </plugin>
        <plugin>
          <groupId>org.springframework.boot</groupId>
          <artifactId>spring-boot-maven-plugin</artifactId>
          <version>`$`{spring-boot.version`}</version>
        </plugin>
      </plugins>
    </pluginManagement>
  </build>
</project>
"@
Write-Utf8File -Path (Join-Path $projectRoot "pom.xml") -Content $parentPom

foreach ($module in $Modules) {
    $moduleDir = Join-Path $projectRoot $module
    $isDeployable = $DeployableModules -contains $module
    New-Item -ItemType Directory -Path $moduleDir | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $moduleDir "src/main/java") | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $moduleDir "src/test/java") | Out-Null

    $dependencies = ""
    $build = ""
    if ($isDeployable) {
        $dependencies = @"
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter</artifactId>
    </dependency>
"@
        $build = @"
  <build>
    <plugins>
      <plugin>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-maven-plugin</artifactId>
      </plugin>
    </plugins>
  </build>
"@
    }

    $childPom = @"
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>

  <parent>
    <groupId>$GroupId</groupId>
    <artifactId>$ProjectName</artifactId>
    <version>$Version</version>
  </parent>

  <artifactId>$module</artifactId>
  <packaging>jar</packaging>

  <dependencies>
$dependencies
  </dependencies>

$build</project>
"@
    Write-Utf8File -Path (Join-Path $moduleDir "pom.xml") -Content $childPom

    $moduleAgents = @"
# AGENTS.md

## 模块职责

``$module`` 的职责应在项目创建后补充明确。

## 是否可部署

$isDeployable

## 禁止事项

- 不要加入超出本模块职责的业务逻辑。
- 不要引入循环依赖。

## 测试与运行

~~~bash
mvn test -pl $module -DskipTests=false
mvn clean package -pl $module -am -DskipTests
~~~
"@
    Write-Utf8File -Path (Join-Path $moduleDir "AGENTS.md") -Content $moduleAgents

    if ($isDeployable) {
        $packagePath = To-PackagePath $BasePackage
        $javaDir = Join-Path (Join-Path $moduleDir "src/main/java") $packagePath
        New-Item -ItemType Directory -Path $javaDir | Out-Null
        $className = To-ClassName $module
        $application = @"
package $BasePackage;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class $className {
    public static void main(String[] args) {
        SpringApplication.run($className.class, args);
    }
}
"@
        Write-Utf8File -Path (Join-Path $javaDir "$className.java") -Content $application
    }
}

$moduleRows = ($Modules | ForEach-Object {
    $deployable = ($DeployableModules -contains $_).ToString().ToLowerInvariant()
    "| $_ | $deployable | 需确认 |"
}) -join "`n"

$rootAgents = @"
# AGENTS.md

## 项目概况

``$ProjectName`` 是 Java $JavaVersion / Spring Boot $SpringBootVersion Maven 多模块项目。

## 模块结构

| 模块 | 是否可部署 | 职责 |
| --- | --- | --- |
$moduleRows

## 构建与运行

~~~bash
mvn -q -DskipTests compile
mvn spring-boot:run -pl <module>
~~~

## 编码规则

- 保持依赖方向单向。
- 不要把业务实现放入 common 模块。
- 新增模块前，先说明职责、上游、下游和验证方式。
"@
Write-Utf8File -Path (Join-Path $projectRoot "AGENTS.md") -Content $rootAgents

Write-Host "Created: $projectRoot"
Write-Host "Suggested verification: cd `"$projectRoot`"; mvn -q -DskipTests compile"
