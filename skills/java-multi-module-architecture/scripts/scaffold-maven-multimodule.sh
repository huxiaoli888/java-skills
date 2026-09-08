#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scaffold-maven-multimodule.sh \
    --project-name demo \
    --group-id com.example \
    --base-package com.example.demo \
    --modules demo-common,demo-api \
    --deployable-modules demo-api
EOF
}

PROJECT_NAME=""
GROUP_ID=""
BASE_PACKAGE=""
VERSION="1.0.0-SNAPSHOT"
JAVA_VERSION="17"
SPRING_BOOT_VERSION="4.0.5"
MODULES=""
DEPLOYABLE_MODULES=""
OUTPUT_DIR="."

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-name) PROJECT_NAME="$2"; shift 2 ;;
    --group-id) GROUP_ID="$2"; shift 2 ;;
    --base-package) BASE_PACKAGE="$2"; shift 2 ;;
    --version) VERSION="$2"; shift 2 ;;
    --java-version) JAVA_VERSION="$2"; shift 2 ;;
    --spring-boot-version) SPRING_BOOT_VERSION="$2"; shift 2 ;;
    --modules) MODULES="$2"; shift 2 ;;
    --deployable-modules) DEPLOYABLE_MODULES="$2"; shift 2 ;;
    --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

if [[ -z "$PROJECT_NAME" || -z "$GROUP_ID" || -z "$BASE_PACKAGE" || -z "$MODULES" ]]; then
  usage
  exit 1
fi

IFS=',' read -r -a MODULE_ARRAY <<< "$MODULES"
IFS=',' read -r -a DEPLOYABLE_ARRAY <<< "$DEPLOYABLE_MODULES"

contains() {
  local item="$1"
  shift
  for value in "$@"; do
    [[ "$value" == "$item" ]] && return 0
  done
  return 1
}

to_class_name() {
  local name="$1"
  awk -F'[-_]' '{
    for (i = 1; i <= NF; i++) {
      printf toupper(substr($i,1,1)) substr($i,2)
    }
    printf "Application"
  }' <<< "$name"
}

PROJECT_ROOT="$OUTPUT_DIR/$PROJECT_NAME"
if [[ -e "$PROJECT_ROOT" ]]; then
  echo "目标目录已存在，已停止以避免覆盖：$PROJECT_ROOT" >&2
  exit 1
fi

mkdir -p "$PROJECT_ROOT"

MODULE_LINES=""
for module in "${MODULE_ARRAY[@]}"; do
  MODULE_LINES+="    <module>${module}</module>"$'\n'
done

cat > "$PROJECT_ROOT/pom.xml" <<EOF
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>$GROUP_ID</groupId>
  <artifactId>$PROJECT_NAME</artifactId>
  <version>$VERSION</version>
  <packaging>pom</packaging>
  <modules>
${MODULE_LINES%$'\n'}
  </modules>
  <properties>
    <java.version>$JAVA_VERSION</java.version>
    <spring-boot.version>$SPRING_BOOT_VERSION</spring-boot.version>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <project.reporting.outputEncoding>UTF-8</project.reporting.outputEncoding>
    <maven.compiler.encoding>UTF-8</maven.compiler.encoding>
  </properties>
  <dependencyManagement>
    <dependencies>
      <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-dependencies</artifactId>
        <version>\${spring-boot.version}</version>
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
            <release>\${java.version}</release>
            <encoding>UTF-8</encoding>
          </configuration>
        </plugin>
        <plugin>
          <groupId>org.springframework.boot</groupId>
          <artifactId>spring-boot-maven-plugin</artifactId>
          <version>\${spring-boot.version}</version>
        </plugin>
      </plugins>
    </pluginManagement>
  </build>
</project>
EOF

for module in "${MODULE_ARRAY[@]}"; do
  module_dir="$PROJECT_ROOT/$module"
  mkdir -p "$module_dir/src/main/java" "$module_dir/src/test/java"
  deployable="false"
  dependencies=""
  build=""
  if contains "$module" "${DEPLOYABLE_ARRAY[@]}"; then
    deployable="true"
    dependencies='    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter</artifactId>
    </dependency>'
    build='  <build>
    <plugins>
      <plugin>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-maven-plugin</artifactId>
      </plugin>
    </plugins>
  </build>'
  fi

  cat > "$module_dir/pom.xml" <<EOF
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <parent>
    <groupId>$GROUP_ID</groupId>
    <artifactId>$PROJECT_NAME</artifactId>
    <version>$VERSION</version>
  </parent>
  <artifactId>$module</artifactId>
  <packaging>jar</packaging>
  <dependencies>
$dependencies
  </dependencies>
$build
</project>
EOF

  cat > "$module_dir/AGENTS.md" <<EOF
# AGENTS.md

## 模块职责

\`$module\` 的职责需要在创建后按业务补充。

## 是否可部署

$deployable

## 本模块不要放

- 不要放入不属于本模块职责的业务实现。
- 不要引入循环依赖。

## 测试与启动

\`\`\`bash
mvn test -pl $module -DskipTests=false
mvn clean package -pl $module -am -DskipTests
\`\`\`
EOF

  if [[ "$deployable" == "true" ]]; then
    package_path="${BASE_PACKAGE//./\/}"
    java_dir="$module_dir/src/main/java/$package_path"
    mkdir -p "$java_dir"
    class_name="$(to_class_name "$module")"
    cat > "$java_dir/$class_name.java" <<EOF
package $BASE_PACKAGE;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class $class_name {
    public static void main(String[] args) {
        SpringApplication.run($class_name.class, args);
    }
}
EOF
  fi
done

cat > "$PROJECT_ROOT/AGENTS.md" <<EOF
# AGENTS.md

## 项目概览

\`$PROJECT_NAME\` 是 Java $JAVA_VERSION / Spring Boot $SPRING_BOOT_VERSION Maven 多模块项目。

## 构建与启动

\`\`\`bash
mvn -q -DskipTests compile
mvn spring-boot:run -pl <module>
\`\`\`

## 编码规则

- 遵守单向依赖。
- 不把业务实现放入 common。
- 新增模块前先说明职责、上下游和验证方式。
EOF

echo "创建完成：$PROJECT_ROOT"
echo "建议验证：cd \"$PROJECT_ROOT\" && mvn -q -DskipTests compile"
