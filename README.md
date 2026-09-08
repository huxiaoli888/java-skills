# Java Skills

本项目集中存放 Java/Netty 后端相关 Codex skills，用于规范 AI 辅助开发、代码审查、项目脚手架、生产事故处理、Netty 协议设计和项目知识库沉淀。

## 目录结构

```text
java-skills/
|-- README.md
`-- skills/
    |-- java-backend-development-orchestrator
    |-- java-backend-api-standard
    |-- java-backend-project-generator
    |-- java-microservice-dev
    |-- java-multi-module-architecture
    |-- java-development-principles
    |-- java-code-review
    |-- java-incident-fix
    |-- netty-handler-dispatcher
    `-- vibecoding-knowledge-base
```

## Skill 职责

| Skill | 主要职责 |
| --- | --- |
| `java-backend-development-orchestrator` | Java/Netty 后端统一入口，负责选择主责 skill、辅助 skill 和执行顺序。 |
| `java-backend-api-standard` | HTTP/API 契约、统一响应、错误码、`reqid`、请求头、鉴权、签名、防重放、幂等和 OpenAPI 标准。 |
| `java-backend-project-generator` | 从零生成 Java/Spring Boot Maven 后端脚手架，支持 `minimal`、`standard` 和显式 Netty 模块。 |
| `java-microservice-dev` | 在已有 Spring Boot 项目中实现具体 Controller、Service、Mapper/JPA、Feign、MQ、Redis、配置和测试。 |
| `java-multi-module-architecture` | Maven 多模块、父子 POM、模块边界、依赖方向、`common` 边界和模块级 `AGENTS.md`。 |
| `java-development-principles` | SOLID、职责拆分、分层依赖、事务、异常、日志、测试、类/方法大小和组合复用。 |
| `java-code-review` | Java/Spring Boot PR、diff、commit 或已有代码变更的风险导向审查。 |
| `java-incident-fix` | Java/Spring Boot 生产事故、线上故障、数据风险、安全事件的止血、定位、恢复和 RCA。 |
| `netty-handler-dispatcher` | Netty TCP/UDP/WebSocket 协议入口、`func + version`、handler dispatcher、ACK、心跳和连接治理。 |
| `vibecoding-knowledge-base` | 生成或更新根/模块级 `AGENTS.md`、`docs/vibecoding`、系统边界、证据链和 AI 编程知识库。 |

## 推荐使用方式

新项目：

```text
java-backend-development-orchestrator
-> java-backend-project-generator
-> java-backend-api-standard
-> java-multi-module-architecture
-> java-development-principles
-> java-microservice-dev
```

已有项目开发：

```text
java-backend-development-orchestrator
-> java-multi-module-architecture
-> java-backend-api-standard
-> java-microservice-dev
-> java-development-principles
```

代码审查：

```text
java-code-review
+ java-backend-api-standard / java-development-principles / java-multi-module-architecture / netty-handler-dispatcher 按需辅助
```

生产事故：

```text
java-incident-fix
-> java-microservice-dev
-> java-code-review
```

知识库沉淀：

```text
vibecoding-knowledge-base
+ java-multi-module-architecture / java-backend-api-standard / netty-handler-dispatcher 按需辅助
```

## 维护原则

- `java-backend-development-orchestrator` 只做导航，不重复承载专项详细规则。
- 共享规则只保留在一个权威 skill 中，其他 skill 通过摘要和引用使用。
- 修改 skill 后必须运行对应 `scripts/check_*_skill.py`。
- 维护 forward-test 场景后必须运行对应 `scripts/run_forward_tests.py`。
- 不要保留同一内容的中英文双轨副本，避免规则漂移。

## 公开发布说明

- `java-backend-project-generator` 中包含脚手架模板和开发占位配置，例如示例账号、示例 token、示例 apiKey、示例 secret。
- 这些值仅用于本地开发和模板演示，不得作为生产凭证使用。
- 基于本项目生成真实业务系统后，必须替换所有开发占位密钥、内存实现、默认账号和示例配置。

## 全量验证

在 PowerShell 中可按以下方式运行所有 skill 的自检和 forward-test：

```powershell
$skills = Get-ChildItem -Path "F:\skills\java-skills\skills" -Directory
$failed = @()

foreach ($skill in $skills) {
  $scriptsDir = Join-Path $skill.FullName "scripts"
  $checks = Get-ChildItem -Path $scriptsDir -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -like "check_*skill.py" -or $_.Name -eq "run_forward_tests.py" } |
    Sort-Object Name

  foreach ($script in $checks) {
    Write-Host "== $($skill.Name) / $($script.Name) =="
    py -X utf8 $script.FullName
    if ($LASTEXITCODE -ne 0) {
      $failed += "$($skill.Name)/$($script.Name)"
    }
  }
}

if ($failed.Count -gt 0) {
  Write-Host "FAILED:"
  $failed | ForEach-Object { Write-Host "- $_" }
  exit 1
}

Write-Host "ALL CHECKS PASSED"
```

## 来源

本项目内容复制自：

```text
D:\Users\CodexData\.codex\skills
```
