#!/usr/bin/env python3
"""Validate the java-backend-project-generator skill package."""

from __future__ import annotations

import sys
import re
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_text_if_exists(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def section_between(text: str, start_marker: str, end_marker: str) -> str:
    start = text.find(start_marker)
    end = text.find(end_marker, start + len(start_marker)) if start >= 0 else -1
    if start < 0 or end < 0:
        return ""
    return text[start:end]


def require_order(errors: list[str], file_name: str, text: str, before: str, after: str, message: str) -> None:
    before_index = text.find(before)
    after_index = text.find(after)
    if before_index < 0 or after_index < 0 or before_index > after_index:
        errors.append(f"base-template {file_name} {message}")


def require_no_unicode_escapes(errors: list[str]) -> None:
    pattern = re.compile(r"\\u[0-9a-fA-F]{4}")
    scan_roots = [ROOT / "assets" / "base-template", ROOT / "scripts"]
    for scan_root in scan_roots:
        for path in scan_root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in {"target", "__pycache__"} for part in path.parts):
                continue
            try:
                text = read_text(path)
            except UnicodeDecodeError:
                continue
            if pattern.search(text):
                relative = path.relative_to(ROOT).as_posix()
                errors.append(f"生成器模板和脚本不得包含 Java Unicode 转义，请直接使用 UTF-8 中文：{relative}")


def main() -> int:
    errors: list[str] = []
    require_no_unicode_escapes(errors)
    template_root = ROOT / "assets" / "base-template"
    cms_api_root = template_root / "chaken-ai-test-cms-api"
    sdk_api_root = template_root / "chaken-ai-test-sdk-api"
    common_root = template_root / "chaken-ai-test-common"
    skill_text = read_text(ROOT / "SKILL.md")
    agents_text = read_text(ROOT / "agents" / "openai.yaml")
    generation_contract = read_text(ROOT / "references" / "generation-contract.md")
    generation_workflow = read_text(ROOT / "references" / "generation-workflow.md")
    profile_design = read_text(ROOT / "references" / "profile-design.md")
    forward_tests = read_text(ROOT / "references" / "forward-test-scenarios.md")
    forward_test_script = read_text(ROOT / "scripts" / "run_forward_tests.py")
    scaffold_script = read_text(ROOT / "scripts" / "scaffold-java-backend-project.ps1")
    profile_helpers_text = read_text(ROOT / "scripts" / "generator-profile-helpers.ps1")
    profile_test_script = read_text(ROOT / "scripts" / "test-generator-profiles.ps1")
    base_smoke_script = read_text(ROOT / "assets" / "base-template" / "scripts" / "smoke-test.ps1")
    api_exception_rule = read_text(
        ROOT.parent
        / "java-backend-api-standard"
        / "scripts"
        / "api_standard_rules"
        / "exception_logging.py"
    )
    api_result = read_text(
        ROOT
        / "assets"
        / "base-template"
        / "chaken-ai-test-common"
        / "src"
        / "main"
        / "java"
        / "com"
        / "chaken"
        / "ai"
        / "test"
        / "common"
        / "api"
        / "ApiResult.java"
    )
    logging_operation_audit_service_path = (
        common_root
        / "src"
        / "main"
        / "java"
        / "com"
        / "chaken"
        / "ai"
        / "test"
        / "common"
        / "log"
        / "service"
        / "LoggingOperationAuditService.java"
    )
    logging_operation_audit_service = read_text_if_exists(logging_operation_audit_service_path)
    base_entity = read_text(
        common_root
        / "src"
        / "main"
        / "java"
        / "com"
        / "chaken"
        / "ai"
        / "test"
        / "common"
        / "persistence"
        / "BaseEntity.java"
    )
    entity_audit_fill_support = read_text(
        common_root
        / "src"
        / "main"
        / "java"
        / "com"
        / "chaken"
        / "ai"
        / "test"
        / "common"
        / "persistence"
        / "EntityAuditFillSupport.java"
    )
    persistence_configuration = read_text(
        common_root
        / "src"
        / "main"
        / "java"
        / "com"
        / "chaken"
        / "ai"
        / "test"
        / "common"
        / "config"
        / "PersistenceConfiguration.java"
    )
    cms_pom = read_text(cms_api_root / "pom.xml")
    sdk_pom = read_text(template_root / "chaken-ai-test-sdk-api" / "pom.xml")
    netty_pom = read_text(template_root / "chaken-ai-test-netty" / "pom.xml")
    replay_request_store = read_text(
        common_root
        / "src"
        / "main"
        / "java"
        / "com"
        / "chaken"
        / "ai"
        / "test"
        / "security"
        / "replay"
        / "ReplayRequestStore.java"
    )
    in_memory_replay_request_store = read_text(
        common_root
        / "src"
        / "main"
        / "java"
        / "com"
        / "chaken"
        / "ai"
        / "test"
        / "security"
        / "replay"
        / "InMemoryReplayRequestStore.java"
    )
    redis_replay_request_store = read_text(
        ROOT
        / "assets"
        / "base-template"
        / "docs"
        / "templates"
        / "production"
        / "redis"
        / "RedisReplayRequestStore.java"
    )
    redis_replay_and_rate_limit_test = read_text(
        ROOT
        / "assets"
        / "base-template"
        / "docs"
        / "templates"
        / "production"
        / "tests"
        / "RedisReplayAndRateLimitIntegrationTest.java"
    )
    sdk_security_filter = read_text(
        ROOT
        / "assets"
        / "base-template"
        / "chaken-ai-test-sdk-api"
        / "src"
        / "main"
        / "java"
        / "com"
        / "chaken"
        / "ai"
        / "test"
        / "sdk"
        / "security"
        / "SdkSecurityFilter.java"
    )
    cms_security_filter = read_text(
        ROOT
        / "assets"
        / "base-template"
        / "chaken-ai-test-cms-api"
        / "src"
        / "main"
        / "java"
        / "com"
        / "chaken"
        / "ai"
        / "test"
        / "cms"
        / "security"
        / "CmsSecurityFilter.java"
    )
    db_operation_audit_service = read_text(
        ROOT
        / "assets"
        / "base-template"
        / "chaken-ai-test-cms-api"
        / "src"
        / "main"
        / "java"
        / "com"
        / "chaken"
        / "ai"
        / "test"
        / "cms"
        / "log"
        / "service"
        / "impl"
        / "DbOperationAuditService.java"
    )
    cms_auth_service_impl = read_text(
        ROOT
        / "assets"
        / "base-template"
        / "chaken-ai-test-cms-api"
        / "src"
        / "main"
        / "java"
        / "com"
        / "chaken"
        / "ai"
        / "test"
        / "cms"
        / "auth"
        / "service"
        / "impl"
        / "CmsAuthServiceImpl.java"
    )
    cms_security_properties = read_text(
        ROOT
        / "assets"
        / "base-template"
        / "chaken-ai-test-cms-api"
        / "src"
        / "main"
        / "java"
        / "com"
        / "chaken"
        / "ai"
        / "test"
        / "cms"
        / "security"
        / "CmsSecurityProperties.java"
    )
    signature_authentication_support = read_text(
        ROOT
        / "assets"
        / "base-template"
        / "chaken-ai-test-common"
        / "src"
        / "main"
        / "java"
        / "com"
        / "chaken"
        / "ai"
        / "test"
        / "security"
        / "signature"
        / "SignatureAuthenticationSupport.java"
    )
    cached_body_http_servlet_request = read_text(
        ROOT
        / "assets"
        / "base-template"
        / "chaken-ai-test-common"
        / "src"
        / "main"
        / "java"
        / "com"
        / "chaken"
        / "ai"
        / "test"
        / "security"
        / "body"
        / "CachedBodyHttpServletRequest.java"
    )
    cached_body_http_servlet_request_test = read_text(
        ROOT
        / "assets"
        / "base-template"
        / "chaken-ai-test-common"
        / "src"
        / "test"
        / "java"
        / "com"
        / "chaken"
        / "ai"
        / "test"
        / "common"
        / "security"
        / "body"
        / "CachedBodyHttpServletRequestTest.java"
    )
    netty_tcp_handler = read_text(
        ROOT
        / "assets"
        / "base-template"
        / "chaken-ai-test-netty"
        / "src"
        / "main"
        / "java"
        / "com"
        / "chaken"
        / "ai"
        / "test"
        / "netty"
        / "tcp"
        / "NettyTcpMessageHandler.java"
    )
    netty_udp_handler = read_text(
        ROOT
        / "assets"
        / "base-template"
        / "chaken-ai-test-netty"
        / "src"
        / "main"
        / "java"
        / "com"
        / "chaken"
        / "ai"
        / "test"
        / "netty"
        / "udp"
        / "NettyUdpMessageHandler.java"
    )
    netty_response_writer = read_text(
        ROOT
        / "assets"
        / "base-template"
        / "chaken-ai-test-netty"
        / "src"
        / "main"
        / "java"
        / "com"
        / "chaken"
        / "ai"
        / "test"
        / "netty"
        / "protocol"
        / "NettyResponseWriter.java"
    )
    base_agents = read_text(ROOT / "assets" / "base-template" / "AGENTS.md")
    common_agents = read_text(ROOT / "assets" / "base-template" / "chaken-ai-test-common" / "AGENTS.md")
    cms_agents = read_text(ROOT / "assets" / "base-template" / "chaken-ai-test-cms-api" / "AGENTS.md")
    sdk_agents = read_text(ROOT / "assets" / "base-template" / "chaken-ai-test-sdk-api" / "AGENTS.md")
    base_readme = read_text(ROOT / "assets" / "base-template" / "README.md")
    api_inventory = read_text(ROOT / "assets" / "base-template" / "docs" / "api" / "api_inventory.md")
    system_architecture = read_text(
        ROOT / "assets" / "base-template" / "docs" / "architecture" / "system_architecture.md"
    )
    generated_permission_standard = read_text(
        ROOT / "assets" / "base-template" / "docs" / "development" / "permission_standard.md"
    )

    required_files = [
        "references/generation-contract.md",
        "references/generation-workflow.md",
        "references/profile-design.md",
        "references/forward-test-scenarios.md",
        "scripts/run_forward_tests.py",
        "scripts/scaffold-java-backend-project.ps1",
        "scripts/test-generator-profiles.ps1",
        "assets/base-template/pom.xml",
        "assets/base-template/chaken-ai-test-common/pom.xml",
    ]
    for relative in required_files:
        if not (ROOT / relative).exists():
            errors.append(f"缺少生成器关键文件：{relative}")

    common_package_required_files = [
        "src/main/java/com/chaken/ai/test/common/log/annotation/OperationAudit.java",
        "src/main/java/com/chaken/ai/test/common/log/aspect/OperationAuditAspect.java",
        "src/main/java/com/chaken/ai/test/common/log/model/OperationAuditRecord.java",
        "src/main/java/com/chaken/ai/test/common/log/model/OperationType.java",
        "src/main/java/com/chaken/ai/test/common/log/service/OperationAuditService.java",
        "src/main/java/com/chaken/ai/test/common/log/service/LoggingOperationAuditService.java",
        "src/main/java/com/chaken/ai/test/common/permission/annotation/RequirePermission.java",
        "src/main/java/com/chaken/ai/test/common/permission/aspect/PermissionAuthorizationAspect.java",
        "src/main/java/com/chaken/ai/test/common/permission/context/DataPermissionContext.java",
        "src/main/java/com/chaken/ai/test/common/permission/context/PrincipalContext.java",
        "src/main/java/com/chaken/ai/test/common/permission/context/TenantContext.java",
        "src/main/java/com/chaken/ai/test/common/permission/model/AuthenticatedPrincipal.java",
        "src/main/java/com/chaken/ai/test/common/permission/model/DataPermissionScope.java",
        "src/main/java/com/chaken/ai/test/common/permission/service/DefaultPermissionEvaluator.java",
        "src/main/java/com/chaken/ai/test/common/permission/service/PermissionEvaluator.java",
    ]
    for relative in common_package_required_files:
        if not (common_root / relative).exists():
            errors.append(f"common 横切能力必须按能力域和职责子包存放，缺少：{relative}")
    forbidden_common_package_paths = [
        "src/main/java/com/chaken/ai/test/common/audit",
        "src/main/java/com/chaken/ai/test/common/authz",
        "src/test/java/com/chaken/ai/test/common/authz",
    ]
    for relative in forbidden_common_package_paths:
        if (common_root / relative).exists():
            errors.append(f"common 横切能力包名必须使用 common.log/common.permission，不应保留旧目录：{relative}")
    if "@TableId(type = IdType.ASSIGN_ID)" not in base_entity:
        errors.append("BaseEntity 主键必须使用 MyBatis-Plus @TableId(type = IdType.ASSIGN_ID)")
    if "private Long version" not in base_entity:
        errors.append("BaseEntity 乐观锁字段必须使用 Java 属性 version")
    if "op_version" in base_entity or "private Long opVersion" in base_entity:
        errors.append("BaseEntity 不应使用 op_version/opVersion，乐观锁字段应改回 version")
    if "getOpVersion()" in entity_audit_fill_support or "setOpVersion(" in entity_audit_fill_support:
        errors.append("EntityAuditFillSupport 不应继续调用 getOpVersion/setOpVersion")
    if "getVersion()" not in entity_audit_fill_support or "setVersion(0L)" not in entity_audit_fill_support:
        errors.append("EntityAuditFillSupport 必须在新增时初始化 version=0")
    if "SnowflakeIdGenerator" in entity_audit_fill_support or "setId(" in entity_audit_fill_support:
        errors.append("EntityAuditFillSupport 只填充审计字段，不应依赖 SnowflakeIdGenerator 或手动 setId")
    if "SnowflakeIdGenerator" in persistence_configuration:
        errors.append("PersistenceConfiguration 不应注册 SnowflakeIdGenerator；实体 id 由 MyBatis-Plus ASSIGN_ID 生成")
    for module_name, pom_text, main_class in [
        ("CMS", cms_pom, "com.chaken.ai.test.ChakenAiTestCmsApiApplication"),
        ("SDK", sdk_pom, "com.chaken.ai.test.ChakenAiTestSdkApiApplication"),
        ("Netty", netty_pom, "com.chaken.ai.test.ChakenAiTestNettyApplication"),
    ]:
        if f"<mainClass>{main_class}</mainClass>" not in pom_text:
            errors.append(f"{module_name} 可运行模块 spring-boot-maven-plugin 必须显式配置 mainClass，避免 repackage 自动扫描失败")

    sdk_testtask_root = sdk_api_root / "src" / "main" / "java" / "com" / "chaken" / "ai" / "test" / "sdk" / "testtask"
    if (sdk_testtask_root / "command").exists() or (sdk_testtask_root / "model").exists():
        errors.append("SDK 默认 testtask 示例必须采用 renren 风格 controller/dto/service/impl，不应生成 command/model 包")
    sdk_service_files = [path.name for path in (sdk_testtask_root / "service").glob("*.java")]
    if "TestTaskService.java" not in sdk_service_files:
        errors.append("SDK 默认 testtask 示例必须只有轻量 TestTaskService 门面，不应拆成 CommandService/QueryService")
    if "TestTaskCommandService.java" in sdk_service_files or "TestTaskQueryService.java" in sdk_service_files:
        errors.append("SDK 默认 testtask 示例不应拆分 TestTaskCommandService/TestTaskQueryService")

    cms_log_required_files = [
        "src/main/java/com/chaken/ai/test/cms/log/controller/CmsOperationLogController.java",
        "src/main/java/com/chaken/ai/test/cms/log/controller/CmsLoginLogController.java",
        "src/main/java/com/chaken/ai/test/cms/log/dto/request/OperationLogPageQuery.java",
        "src/main/java/com/chaken/ai/test/cms/log/dto/request/LoginLogPageQuery.java",
        "src/main/java/com/chaken/ai/test/cms/log/dto/response/OperationLogResponse.java",
        "src/main/java/com/chaken/ai/test/cms/log/dto/response/LoginLogResponse.java",
        "src/main/java/com/chaken/ai/test/cms/log/entity/OperationLogEntity.java",
        "src/main/java/com/chaken/ai/test/cms/log/entity/LoginLogEntity.java",
        "src/main/java/com/chaken/ai/test/cms/log/mapper/OperationLogMapper.java",
        "src/main/java/com/chaken/ai/test/cms/log/mapper/LoginLogMapper.java",
        "src/main/java/com/chaken/ai/test/cms/log/service/OperationLogService.java",
        "src/main/java/com/chaken/ai/test/cms/log/service/LoginLogService.java",
        "src/main/java/com/chaken/ai/test/cms/log/service/impl/DbOperationAuditService.java",
        "src/main/java/com/chaken/ai/test/cms/log/service/impl/OperationLogServiceImpl.java",
        "src/main/java/com/chaken/ai/test/cms/log/service/impl/LoginLogServiceImpl.java",
        "src/main/resources/mapper/cms/log/OperationLogMapper.xml",
        "src/main/resources/mapper/cms/log/LoginLogMapper.xml",
        "src/main/resources/db/migration/V1__create_cms_log_tables.sql",
    ]
    for relative in cms_log_required_files:
        if not (cms_api_root / relative).exists():
            errors.append(f"minimal 模板缺少 renren 风格后台日志文件：{relative}")
    if "@ConditionalOnMissingBean(OperationAuditService.class)" in logging_operation_audit_service:
        errors.append("LoggingOperationAuditService 不应依赖组件扫描阶段的 @ConditionalOnMissingBean，否则 SDK 可能缺少兜底审计 bean")
    if "@Primary" not in db_operation_audit_service:
        errors.append("DbOperationAuditService 必须使用 @Primary，确保 CMS 优先使用数据库审计实现")

    cms_auth_required_files = [
        "src/main/java/com/chaken/ai/test/cms/auth/controller/CmsAuthController.java",
        "src/main/java/com/chaken/ai/test/cms/auth/dto/request/CmsLoginRequest.java",
        "src/main/java/com/chaken/ai/test/cms/auth/dto/response/CmsLoginResponse.java",
        "src/main/java/com/chaken/ai/test/cms/auth/entity/AdminTokenEntity.java",
        "src/main/java/com/chaken/ai/test/cms/auth/mapper/AdminTokenMapper.java",
        "src/main/java/com/chaken/ai/test/cms/auth/service/CmsAuthService.java",
        "src/main/java/com/chaken/ai/test/cms/auth/service/CmsTokenService.java",
        "src/main/java/com/chaken/ai/test/cms/auth/service/PasswordHashService.java",
        "src/main/java/com/chaken/ai/test/cms/auth/service/impl/CmsAuthServiceImpl.java",
        "src/main/java/com/chaken/ai/test/cms/auth/service/impl/DbCmsTokenService.java",
        "src/main/java/com/chaken/ai/test/cms/auth/service/impl/Pbkdf2PasswordHashService.java",
        "src/main/resources/mapper/cms/auth/AdminTokenMapper.xml",
    ]
    for relative in cms_auth_required_files:
        if not (cms_api_root / relative).exists():
            errors.append(f"minimal 模板缺少 renren 风格 CMS 登录/token 文件：{relative}")

    cms_sys_required_files = [
        "src/main/java/com/chaken/ai/test/cms/sys/controller/CmsSysUserController.java",
        "src/main/java/com/chaken/ai/test/cms/sys/controller/CmsSysRoleController.java",
        "src/main/java/com/chaken/ai/test/cms/sys/controller/CmsSysMenuController.java",
        "src/main/java/com/chaken/ai/test/cms/sys/controller/CmsSysDictController.java",
        "src/main/java/com/chaken/ai/test/cms/sys/controller/CmsSysParamController.java",
        "src/main/java/com/chaken/ai/test/cms/sys/controller/CmsCurrentUserController.java",
        "src/main/java/com/chaken/ai/test/cms/sys/dto/request/SysUserPageQuery.java",
        "src/main/java/com/chaken/ai/test/cms/sys/dto/request/SysDictPageQuery.java",
        "src/main/java/com/chaken/ai/test/cms/sys/dto/request/SysParamPageQuery.java",
        "src/main/java/com/chaken/ai/test/cms/sys/dto/response/SysCurrentUserResponse.java",
        "src/main/java/com/chaken/ai/test/cms/sys/dto/response/SysDictItemResponse.java",
        "src/main/java/com/chaken/ai/test/cms/sys/dto/response/SysDictResponse.java",
        "src/main/java/com/chaken/ai/test/cms/sys/dto/response/SysMenuResponse.java",
        "src/main/java/com/chaken/ai/test/cms/sys/dto/response/SysParamResponse.java",
        "src/main/java/com/chaken/ai/test/cms/sys/dto/response/SysRoleResponse.java",
        "src/main/java/com/chaken/ai/test/cms/sys/dto/response/SysUserResponse.java",
        "src/main/java/com/chaken/ai/test/cms/sys/entity/SysDictEntity.java",
        "src/main/java/com/chaken/ai/test/cms/sys/entity/SysDictItemEntity.java",
        "src/main/java/com/chaken/ai/test/cms/sys/entity/SysMenuEntity.java",
        "src/main/java/com/chaken/ai/test/cms/sys/entity/SysParamEntity.java",
        "src/main/java/com/chaken/ai/test/cms/sys/entity/SysRoleEntity.java",
        "src/main/java/com/chaken/ai/test/cms/sys/entity/SysUserEntity.java",
        "src/main/java/com/chaken/ai/test/cms/sys/mapper/SysDictItemMapper.java",
        "src/main/java/com/chaken/ai/test/cms/sys/mapper/SysDictMapper.java",
        "src/main/java/com/chaken/ai/test/cms/sys/mapper/SysMenuMapper.java",
        "src/main/java/com/chaken/ai/test/cms/sys/mapper/SysParamMapper.java",
        "src/main/java/com/chaken/ai/test/cms/sys/mapper/SysRoleMapper.java",
        "src/main/java/com/chaken/ai/test/cms/sys/mapper/SysUserMapper.java",
        "src/main/java/com/chaken/ai/test/cms/sys/service/SysDictService.java",
        "src/main/java/com/chaken/ai/test/cms/sys/service/SysMenuService.java",
        "src/main/java/com/chaken/ai/test/cms/sys/service/SysParamService.java",
        "src/main/java/com/chaken/ai/test/cms/sys/service/SysRoleService.java",
        "src/main/java/com/chaken/ai/test/cms/sys/service/SysUserService.java",
        "src/main/java/com/chaken/ai/test/cms/sys/service/impl/SysDictServiceImpl.java",
        "src/main/java/com/chaken/ai/test/cms/sys/service/impl/SysMenuServiceImpl.java",
        "src/main/java/com/chaken/ai/test/cms/sys/service/impl/SysParamServiceImpl.java",
        "src/main/java/com/chaken/ai/test/cms/sys/service/impl/SysRoleServiceImpl.java",
        "src/main/java/com/chaken/ai/test/cms/sys/service/impl/SysUserServiceImpl.java",
        "src/main/resources/mapper/cms/sys/SysDictItemMapper.xml",
        "src/main/resources/mapper/cms/sys/SysDictMapper.xml",
        "src/main/resources/mapper/cms/sys/SysMenuMapper.xml",
        "src/main/resources/mapper/cms/sys/SysParamMapper.xml",
        "src/main/resources/mapper/cms/sys/SysRoleMapper.xml",
        "src/main/resources/mapper/cms/sys/SysUserMapper.xml",
    ]
    for relative in cms_sys_required_files:
        if not (cms_api_root / relative).exists():
            errors.append(f"minimal 模板缺少 renren 风格 cms.sys 系统管理骨架文件：{relative}")

    cms_log_migration = read_text(cms_api_root / "src" / "main" / "resources" / "db" / "migration" / "V1__create_cms_log_tables.sql")
    for table_name in [
        "cms_sys_user",
        "cms_sys_role",
        "cms_sys_menu",
        "cms_sys_user_role",
        "cms_sys_role_menu",
        "cms_sys_dict",
        "cms_sys_dict_item",
        "cms_sys_param",
        "cms_admin_token",
        "cms_login_log",
    ]:
        if table_name not in cms_log_migration:
            errors.append(f"CMS 默认迁移脚本必须包含 {table_name}")
    for permission_code in ["sys:dict:list", "sys:param:list"]:
        if permission_code not in cms_log_migration:
            errors.append(f"CMS 默认迁移脚本必须包含系统管理权限码：{permission_code}")
    if "cms_admin_user" in cms_log_migration:
        errors.append("CMS 默认迁移脚本不应继续保留 cms_admin_user，登录用户应统一使用 cms_sys_user")
    if "'系统管理', 'MENU', '/sys', ''," in cms_log_migration:
        errors.append("cms_sys_menu 父级菜单 permission_code 应使用 null，避免多个目录菜单使用空字符串撞唯一索引")
    cms_auth_impl = read_text(
        cms_api_root
        / "src"
        / "main"
        / "java"
        / "com"
        / "chaken"
        / "ai"
        / "test"
        / "cms"
        / "auth"
        / "service"
        / "impl"
        / "CmsAuthServiceImpl.java"
    )
    cms_token_service = read_text(
        cms_api_root
        / "src"
        / "main"
        / "java"
        / "com"
        / "chaken"
        / "ai"
        / "test"
        / "cms"
        / "auth"
        / "service"
        / "impl"
        / "DbCmsTokenService.java"
    )
    if "cms.sys.mapper.SysUserMapper" not in cms_auth_impl or "cms.sys.entity.SysUserEntity" not in cms_auth_impl:
        errors.append("CmsAuthServiceImpl 必须使用 cms.sys 的 SysUserMapper/SysUserEntity，不得维护第二套 auth 用户表")
    if "cms.sys.entity.SysUserEntity" not in cms_token_service:
        errors.append("DbCmsTokenService.issueToken 必须接收 cms.sys 的 SysUserEntity，保证登录用户来源统一")
    if "CmsTokenService" not in cms_security_filter or "validateBearerToken" not in cms_security_filter:
        errors.append("CmsSecurityFilter 必须通过 CmsTokenService 校验 Bearer token，不得继续使用固定 default-token")
    if "defaultToken" in cms_security_properties or "getDefaultToken" in cms_security_properties:
        errors.append("CmsSecurityProperties 不应继续暴露 default-token，占位 token 应升级为登录生成的数据库 token")
    for needle in [
        "cmsReplaySubject(authorization, udid)",
        "tokenService.tokenFingerprint(authorization)",
        "udid",
    ]:
        if needle not in cms_security_filter:
            errors.append(f"CmsSecurityFilter 的 CMS replay key 必须包含 token 指纹和 x-udid，缺少：{needle}")
    for file_name, text in {
        "ReplayRequestStore.java": replay_request_store,
        "InMemoryReplayRequestStore.java": in_memory_replay_request_store,
        "RedisReplayRequestStore.java": redis_replay_request_store,
    }.items():
        if "String replaySubject" not in text:
            errors.append(f"base-template {file_name} 的 replay store 第一参数必须命名为 replaySubject，兼容 CMS 和 SDK")
        if "String apiKey" in text:
            errors.append(f"base-template {file_name} 不应把 replay store 第一参数命名为 apiKey，CMS 也复用该组件")
    if 'saveIfAbsent("replay-subject", "reqid-1"' not in redis_replay_and_rate_limit_test:
        errors.append("RedisReplayAndRateLimitIntegrationTest 必须使用 replay-subject 示例，避免误导 replay store 只能按 api-key 防重放")
    if 'saveIfAbsent("api-key", "reqid-1"' in redis_replay_and_rate_limit_test:
        errors.append("RedisReplayAndRateLimitIntegrationTest 不应继续使用 api-key 作为 replay store 第一参数示例")

    for needle in [
        "check_java_backend_project_generator_skill.py",
        "run_forward_tests.py",
        "test-generator-profiles.ps1",
        "java-backend-api-standard",
        "java-multi-module-architecture",
        "netty-handler-dispatcher",
        "Profile minimal|standard",
        "生产增强只保留路线图",
        "只支持 Java 17+",
        "只支持 Spring Boot 3.x/4.x",
    ]:
        if needle not in skill_text:
            errors.append(f"SKILL.md 缺少生成器维护或边界说明：{needle}")

    for needle in [
        "Java 17+",
        "Spring Boot 3.x/4.x",
        "不支持 Spring Boot 2.x 或 JDK8",
    ]:
        if needle not in generation_contract:
            errors.append(f"references/generation-contract.md 缺少版本边界：{needle}")
    for needle in [
        "通用请求头包含 `authorization`、`accept-language`、`x-trace-id`、`x-reqid`、`x-timestamp`、`x-sign`、`x-sign-alg`、`x-api-version` 和 `x-udid`。",
        "CMS security filter 对受保护路径要求 `authorization: Bearer <token>`、`x-udid`、`x-reqid`、`x-timestamp`、`x-sign`、`x-sign-alg` 和 `x-api-version`",
        "CMS 的 CORS allowed headers 默认包含 `authorization`、`accept-language`、`content-type`、`x-trace-id`、`x-udid`、`x-reqid`、`x-timestamp`、`x-sign`、`x-sign-alg` 和 `x-api-version`。",
    ]:
        if needle not in generation_contract:
            errors.append(f"references/generation-contract.md 缺少 CMS/common 请求头 x-timestamp 契约：{needle}")
    if "CMS token 指纹加 `x-udid + x-reqid`" not in generation_workflow:
        errors.append("references/generation-workflow.md 生产替换项中的 CMS replay key 必须包含 x-udid + x-reqid")
    if "CMS token 指纹加 `x-reqid`" in generation_workflow:
        errors.append("references/generation-workflow.md 不应继续建议 CMS replay key 只使用 token 指纹 + x-reqid")
    if "function Get-CanonicalUrlEncoded" not in profile_helpers_text:
        errors.append("scripts/generator-profile-helpers.ps1 生成的 minimal smoke 脚本必须包含 GET query 规范化函数")
    if '$canonicalQuery = Get-CanonicalUrlEncoded -Value $Query' not in profile_helpers_text:
        errors.append("scripts/generator-profile-helpers.ps1 生成的 minimal smoke 脚本 CMS 签名必须规范化 GET query")
    if '$Path, $Query, $timestamp, $Reqid, $authorization' in profile_helpers_text:
        errors.append("scripts/generator-profile-helpers.ps1 生成的 minimal smoke 脚本不应直接用未规范化 Query 参与 CMS 签名")

    for needle in [
        "Assert-SupportedRuntimeVersion",
        "[regex]::Match($JavaVersion, \"^(\\d+)\")",
        "[int]$javaMajorMatch.Groups[1].Value -lt 17",
        "$script:EffectiveJavaVersion = $javaMajorMatch.Groups[1].Value",
        "<java.version>$EffectiveJavaVersion</java.version>",
        '$springBootMajorMatch = [regex]::Match($SpringBootVersion, "^(3|4)\\.")',
        "$script:EffectiveSpringBootMajor = $springBootMajorMatch.Groups[1].Value",
        'mybatis-plus-spring-boot3-starter',
        'mybatis-plus-spring-boot4-starter',
        '$script:SpringdocOpenApiVersion = "2.8.14"',
        '$script:SpringdocOpenApiVersion = "3.0.2"',
        '$script:SpringBootFlywayDocDependencyXml = ""',
        '$SpringBootFlywayDocDependencyXml',
    ]:
        if needle not in scaffold_script:
            errors.append(f"scripts/scaffold-java-backend-project.ps1 缺少版本保护：{needle}")

    for needle in [
        "-SpringBootVersion 3.3.7",
        "-IncludeDbCrudExample",
        "mybatis-plus-spring-boot3-starter",
        "mybatis-plus-spring-boot4-starter",
        "springdoc-openapi-starter-webmvc-api",
        "<version>2.8.14</version>",
        "spring-boot-flyway",
        "business-exception-control-flow",
        "ConvertFrom-Json",
    ]:
        if needle not in profile_test_script:
            errors.append(f"scripts/test-generator-profiles.ps1 缺少 Boot3 CRUD 版本回归：{needle}")

    for forbidden in ['"/docs/templates/" in normalized', "path.name.startswith(\"InMemory\")"]:
        if forbidden in api_exception_rule:
            errors.append(f"API 标准检查器不应跳过生成器模板或 InMemory 样例：{forbidden}")

    if "reqid/code/message/ts/data" not in generation_contract:
        errors.append("references/generation-contract.md 缺少统一响应字段顺序：reqid/code/message/ts/data")
    if "reqid/code/message/data/ts" in generation_contract:
        errors.append("references/generation-contract.md 不应继续使用旧响应字段顺序：reqid/code/message/data/ts")
    if "先使用 `log.error` 记录脱敏堆栈，再尝试返回兜底错误码" not in generation_contract:
        errors.append("references/generation-contract.md 缺少 Netty 不可预期异常先记录原始异常再写兜底响应的顺序要求")
    for needle in [
        "HTTP 请求缺失 `x-reqid` 时，错误响应使用空字符串",
        "不得返回 `reqid: null`",
        "Netty 无法解析请求、请求缺失 `reqid` 或服务端主动响应时",
        "server-UUID",
    ]:
        if needle not in generation_contract:
            errors.append(f"references/generation-contract.md 缺少 reqid 缺失边界规则：{needle}")

    for needle in ["policy:", "trigger_keywords:", "Spring Boot 脚手架", "minimal profile", "standard profile"]:
        if needle not in agents_text:
            errors.append(f"agents/openai.yaml 缺少触发关键词：{needle}")

    for scenario in ["默认轻量后台脚手架", "minimal 小项目", "显式 Netty 长连接"]:
        if scenario not in forward_tests:
            errors.append(f"references/forward-test-scenarios.md 缺少场景：{scenario}")
    if forward_tests.count("### Expected Findings") < 3:
        errors.append("references/forward-test-scenarios.md forward 场景数量不足")
    if forward_tests.count("keyword:") < 12:
        errors.append("references/forward-test-scenarios.md keyword 覆盖不足")
    for needle in ["--score-output", "--score-fixtures", "FIXTURE_OUTPUT_DIR", "--min-score", "SKILL_NAME = ROOT.name"]:
        if needle not in forward_test_script:
            errors.append(f"scripts/run_forward_tests.py 缺少能力：{needle}")

    if '[string]$Profile = "minimal"' not in scaffold_script:
        errors.append("scripts/scaffold-java-backend-project.ps1 默认 Profile 必须是 minimal")
    if "默认使用 `minimal`" not in skill_text:
        errors.append("SKILL.md 必须说明默认使用 minimal profile")
    if "CMS 受保护接口使用 `authorization`、`x-udid`、`x-reqid`、`x-timestamp`、`x-sign`、`x-sign-alg`、`x-api-version`" not in skill_text:
        errors.append("SKILL.md 的 CMS 受保护接口摘要必须包含 x-timestamp，避免和模板实际防重放规则不一致")
    if "默认使用 `minimal`" not in profile_design:
        errors.append("references/profile-design.md 必须说明默认使用 minimal profile")
    if "CMS 受保护接口要求 `authorization`、`x-udid`、`x-reqid`、`x-timestamp`、`x-sign`、`x-sign-alg`、`x-api-version`" not in profile_design:
        errors.append("references/profile-design.md 的 CMS 受保护接口摘要必须包含 x-timestamp")
    if "SDK 受保护接口要求 `x-api-key`、`x-udid`、`x-reqid`、`x-timestamp`、`x-sign`、`x-sign-alg`、`x-api-version`" not in profile_design:
        errors.append("references/profile-design.md 的 SDK 受保护接口摘要必须包含 x-udid")
    if "renren 风格轻量后台框架" not in generation_contract:
        errors.append("references/generation-contract.md 必须说明 minimal 面向 renren 风格轻量后台框架")

    for needle in ["reqid", "code", "message", "ts", "data", '"000000"']:
        if needle not in api_result:
            errors.append(f"base-template ApiResult.java 缺少统一响应字段或成功码：{needle}")

    for needle in ["reqidOrEmpty", "this.reqid = reqidOrEmpty(reqid)", "setReqid(String reqid)"]:
        if needle not in api_result:
            errors.append(f"base-template ApiResult.java 必须将 null reqid 归一化为空字符串：{needle}")

    for forbidden in ['code = "0"', "private String status", "private String traceId"]:
        if forbidden in api_result:
            errors.append(f"base-template ApiResult.java 不应包含旧响应契约：{forbidden}")

    for file_name, text in {
        "AGENTS.md": base_agents,
        "chaken-ai-test-common/AGENTS.md": common_agents,
        "chaken-ai-test-cms-api/AGENTS.md": cms_agents,
        "chaken-ai-test-sdk-api/AGENTS.md": sdk_agents,
        "README.md": base_readme,
    }.items():
        for needle in ["模块", "职责"]:
            if needle not in text:
                errors.append(f"base-template {file_name} 缺少中文模块职责说明：{needle}")
        for stale in ["Project Overview", "Module Structure", "Module Responsibility", "Do Not Put Here", "Build and Run"]:
            if stale in text:
                errors.append(f"base-template {file_name} 存在英文 AGENTS/README 标题残留：{stale}")

    for needle in ["java.util.UUID", "reqidOrGenerated", "server-", "UUID.randomUUID().toString()"]:
        if needle not in netty_response_writer:
            errors.append(f"base-template NettyResponseWriter.java 在 reqid 缺失时应生成服务端唯一 reqid：{needle}")

    expected_rejection_templates = {
        "SdkSecurityFilter.java": sdk_security_filter,
        "CmsSecurityFilter.java": cms_security_filter,
        "SignatureAuthenticationSupport.java": signature_authentication_support,
        "NettyTcpMessageHandler.java": netty_tcp_handler,
        "NettyUdpMessageHandler.java": netty_udp_handler,
    }
    for file_name, text in expected_rejection_templates.items():
        for forbidden in [
            'log.error("sdk_signature_auth_failed',
            'log.error("cms_signature_timestamp_invalid',
            'log.error("signature_timestamp_invalid',
            'log.error("netty_tcp_auth_failed',
            'log.error("netty_udp_auth_failed',
        ]:
            if forbidden in text:
                errors.append(f"base-template {file_name} 不应把可预期鉴权/签名/时间戳拒绝记录为 log.error 堆栈：{forbidden}")

    netty_protocol_error_templates = {
        "NettyTcpMessageHandler.java": netty_tcp_handler,
        "NettyUdpMessageHandler.java": netty_udp_handler,
    }
    for file_name, text in netty_protocol_error_templates.items():
        normalized_text = text.replace("\r\n", "\n")
        for needle in [
            "JsonProcessingException",
            "protocol_invalid",
            'responseWriter.fail(reqid, "AC0001", "协议格式错误")',
            'log.info("netty_',
        ]:
            if needle not in text:
                errors.append(f"base-template {file_name} 应将可预期协议格式错误单独捕获并用 info 记录：{needle}")
        for forbidden in [
            'catch (Exception ex) {\n            context.writeAndFlush(responseWriter.fail(reqid, "AC0001", "协议格式错误")',
            'catch (Exception ex) {\n            writeError(context, packet, responseWriter.fail(reqid, "AC0001", "协议格式错误"))',
        ]:
            if forbidden in normalized_text:
                errors.append(f"base-template {file_name} 不应把可预期协议格式错误和程序异常混在一起：{forbidden}")

    require_order(
        errors,
        "NettyTcpMessageHandler.java",
        netty_tcp_handler,
        'log.error("netty_tcp_message_failed',
        'context.writeAndFlush(responseWriter.fail(reqid, "AC9999", "系统异常")',
        "catch-all 程序异常应先 log.error 记录原始异常，再尝试写兜底响应",
    )
    require_order(
        errors,
        "NettyUdpMessageHandler.java",
        netty_udp_handler,
        'log.error("netty_udp_message_failed',
        'writeError(context, packet, responseWriter.fail(reqid, "AC9999", "系统异常"))',
        "catch-all 程序异常应先 log.error 记录原始异常，再尝试写兜底响应",
    )

    if 'org.slf4j.MDC.get("reqid")' in cms_security_filter:
        errors.append('base-template CmsSecurityFilter.java 不应读取错误 MDC key：org.slf4j.MDC.get("reqid")')
    if "TraceContext.requestId()" not in cms_security_filter:
        errors.append("base-template CmsSecurityFilter.java 应使用 TraceContext.requestId() 读取 reqid")

    for needle in [
        "String udid = request.getHeader(SignatureHeaders.UDID)",
        "x-timestamp;x-reqid;x-api-key;x-udid;x-sign-alg;x-api-version",
        "timestamp,\n                reqid,\n                apiKey,\n                udid,\n                signatureAlg,\n                apiVersion,",
    ]:
        if needle not in signature_authentication_support:
            errors.append(f"base-template SignatureAuthenticationSupport.java SDK 签名 canonical 必须覆盖 x-udid，缺少：{needle}")
    signature_canonical_payload = read_text(
        ROOT
        / "assets"
        / "base-template"
        / "chaken-ai-test-common"
        / "src"
        / "main"
        / "java"
        / "com"
        / "chaken"
        / "ai"
        / "test"
        / "security"
        / "signature"
        / "SignatureCanonicalPayload.java"
    )
    if "supportFormUrlEncoded" in signature_canonical_payload:
        errors.append("base-template SignatureCanonicalPayload.java 不应保留 supportFormUrlEncoded 参数，JSON/form 都统一使用原始 body bytes")
    if "body(request, wrappedRequest.getCachedBody()," in signature_authentication_support or "body(request, wrappedRequest.getCachedBody()," in cms_security_filter:
        errors.append("base-template 签名验签调用不应继续传 supportFormUrlEncoded，避免 CMS/SDK body 口径分叉")
    if '$Path, $canonicalQuery, $timestamp, $Reqid, $SdkApiKey, $SdkUdid, $signatureAlg, $apiVersion' not in base_smoke_script:
        errors.append("base-template scripts/smoke-test.ps1 的 SDK 签名计算必须把 x-udid 纳入 canonical 顺序")
    if "Get-CmsCanonicalBody -Body $Body -ContentType $ContentType" in base_smoke_script:
        errors.append("base-template scripts/smoke-test.ps1 的 CMS 签名必须使用原始 body bytes，不得把 form-urlencoded body 重新排序或重编码")
    if "function Get-CmsCanonicalBody" in base_smoke_script:
        errors.append("base-template scripts/smoke-test.ps1 不应保留 CMS form body canonicalizer，CMS JSON/form 都应按原始 body 签名")
    for needle in [
        "application/x-www-form-urlencoded",
        "getParameter(String name)",
        "getParameterMap()",
        "getParameterValues(String name)",
        "URLDecoder.decode",
    ]:
        if needle not in cached_body_http_servlet_request:
            errors.append(f"base-template CachedBodyHttpServletRequest.java 必须支持缓存后 form 参数读取，缺少：{needle}")
    for needle in [
        "exposesFormParametersFromCachedBody",
        "application/x-www-form-urlencoded; charset=UTF-8",
        "getParameter(\"name\")",
        "getParameterValues(\"name\")",
        "getParameterMap()",
    ]:
        if needle not in cached_body_http_servlet_request_test:
            errors.append(f"base-template CachedBodyHttpServletRequestTest.java 必须覆盖 form body 参数读取，缺少：{needle}")

    if re.search(r"(?m)^`{3}(?!`)", profile_helpers_text):
        errors.append("scripts/generator-profile-helpers.ps1 的双引号 here-string 中 Markdown 代码围栏必须写成转义后的六反引号，避免生成文档出现 `\\text 或单反引号")

    for stale in [
        "生产级 CMS 登录鉴权和权限授权。",
        "数据库 repository/mapper/entity。",
    ]:
        if stale in api_inventory:
            errors.append(f"base-template docs/api/api_inventory.md 存在过时实现状态说明：{stale}")
    protected_cms_signature_sources = {
        "base-template docs/api/api_inventory.md": api_inventory,
        "scripts/generator-profile-helpers.ps1": profile_helpers_text,
    }
    for file_name, text in protected_cms_signature_sources.items():
        if "Bearer token + x-udid | 否" in text:
            errors.append(f"{file_name} 中 CMS 受保护接口必须标记签名=是，不得写成 Bearer token + x-udid | 否")
        if "Bearer token + x-udid | 是 | 可选" in text:
            errors.append(f"{file_name} 中 CMS 受保护接口必须标记防重放=是，不得写成 Bearer token + x-udid | 是 | 可选")
    api_inventory_common_headers = section_between(api_inventory, "所有 API：", "SDK/开放平台/敏感写接口额外要求：")
    if "x-timestamp" not in api_inventory_common_headers:
        errors.append("base-template docs/api/api_inventory.md 的所有 API 通用请求头必须包含 x-timestamp，CMS 受保护接口也依赖它防重放")
    if "CMS `CmsSecurityFilter`，支持 Bearer token + `x-udid` + `x-timestamp` 时间窗口 + `x-sign` 防篡改签名 + `x-sign-alg`/`x-api-version`。" not in api_inventory:
        errors.append("base-template docs/api/api_inventory.md 的 CMS 安全骨架说明必须列完整受保护接口安全头")
    if "登录、验证码、探活等公开接口必须配置到 `auth-exclude-paths`，不能只放入 `udid-exclude-paths`" not in api_inventory:
        errors.append("base-template docs/api/api_inventory.md 必须明确公开接口走 auth-exclude-paths，不能只跳过 x-udid")
    if "登录、验证码、探活等接口可通过 `auth-exclude-paths` 排除整体鉴权，或通过 `udid-exclude-paths`" in api_inventory:
        errors.append("base-template docs/api/api_inventory.md 不应建议登录/验证码/探活只通过 udid-exclude-paths 排除")
    if 'issueToken(user, httpRequest.getHeader("x-udid"))' in cms_auth_service_impl:
        errors.append("base-template CmsAuthServiceImpl 登录公开接口不应读取 x-udid 并绑定到 token")
    if "udid-exclude-paths` 的接口仅跳过 `x-udid` 前置校验，不跳过 token、`x-timestamp` 时间窗口或 `x-sign` 验签" not in system_architecture:
        errors.append("base-template docs/architecture/system_architecture.md 必须说明 udid-exclude-paths 不跳过 token、时间窗口或验签")
    if "``x-timestamp`` 做时间窗口校验，``x-sign`` 做防篡改签名，防重放 replay key 使用 token 指纹 + ``x-udid`` + ``x-reqid``" not in profile_helpers_text:
        errors.append("scripts/generator-profile-helpers.ps1 生成的 CMS API 说明必须区分时间窗口、签名和 replay key")
    if "x-timestamp" not in generated_permission_standard or "x-sign-alg" not in generated_permission_standard or "x-api-version" not in generated_permission_standard:
        errors.append("base-template docs/development/permission_standard.md 必须列出 CMS 受保护接口的 x-timestamp、x-sign-alg 和 x-api-version")
    if "x-udid` 前置校验，不代表跳过认证、`x-timestamp` 时间窗口或 `x-sign` 验签" not in generated_permission_standard:
        errors.append("base-template docs/development/permission_standard.md 必须说明 udid-exclude-paths 不跳过时间窗口或验签")
    smoke_test_doc = read_text(ROOT / "assets" / "base-template" / "docs" / "development" / "smoke_test.md")
    if "SDK 防重放依赖 `x-api-key + x-reqid + x-timestamp`" in smoke_test_doc:
        errors.append("base-template docs/development/smoke_test.md 不应把 x-timestamp 写入 SDK replay key，它只用于时间窗口校验")
    if "SDK 防重放键使用 `x-api-key + x-reqid`，`x-timestamp` 用于时间窗口校验" not in smoke_test_doc:
        errors.append("base-template docs/development/smoke_test.md 必须区分 SDK replay key 和 x-timestamp 时间窗口")

    for needle in [
        "$nettySkillChecker",
        "Assert-NoExpectedRejectionErrorStack",
        "Assert-NettyProtocolErrorsSeparated",
        "Assert-NettyUnexpectedExceptionLoggedBeforeResponse",
        "sdk_signature_auth_failed",
        "netty_tcp_auth_failed",
        "netty_udp_auth_failed",
        "protocol_invalid",
        "cms_signature_timestamp_invalid",
        "signature_timestamp_invalid",
    ]:
        if needle not in profile_test_script:
            errors.append(f"scripts/test-generator-profiles.ps1 缺少 IncludeNetty/安全拒绝日志回归检查：{needle}")

    common_header_section = section_between(generation_workflow, "所有接口通用请求头：", "CMS 默认启用登录态认证：")
    for header in ["authorization", "accept-language", "x-trace-id", "x-udid", "x-reqid", "x-timestamp", "x-sign", "x-sign-alg", "x-api-version"]:
        if header not in common_header_section:
            errors.append(f"references/generation-workflow.md 所有接口通用请求头缺少：{header}")

    generation_workflow_sdk_extra = section_between(generation_workflow, "SDK/OpenAPI 默认启用：", "生成器必须在文档中标注")
    for header in ["x-timestamp", "x-reqid", "x-sign", "x-sign-alg", "x-api-version"]:
        if header in generation_workflow_sdk_extra:
            errors.append(f"references/generation-workflow.md SDK/OpenAPI 额外请求头不应重复列通用请求头：{header}")
    if 'API_KEY + "\\n" +\n  UDID + "\\n" +\n  SIGNATURE_ALG + "\\n" +' not in generation_workflow:
        errors.append("references/generation-workflow.md 签名输入示例必须在 API_KEY 后包含 UDID，和 SDK canonical 覆盖 x-udid 的规则一致")

    system_architecture_common_headers = section_between(system_architecture, "通用请求头：", "SDK/开放平台接口额外要求：")
    for header in ["authorization", "accept-language", "x-trace-id", "x-udid", "x-reqid", "x-timestamp", "x-sign", "x-sign-alg", "x-api-version"]:
        if header not in system_architecture_common_headers:
            errors.append(f"base-template docs/architecture/system_architecture.md 通用请求头缺少：{header}")
    system_architecture_sdk_extra = section_between(system_architecture, "SDK/开放平台接口额外要求：", "幂等不使用公共")
    if "x-api-key" not in system_architecture_sdk_extra:
        errors.append("base-template docs/architecture/system_architecture.md SDK/开放平台额外请求头必须保留 x-api-key")
    for header in ["x-timestamp", "x-reqid", "x-sign", "x-sign-alg", "x-api-version"]:
        if header in system_architecture_sdk_extra:
            errors.append(f"base-template docs/architecture/system_architecture.md SDK/开放平台额外请求头不应重复列通用请求头：{header}")

    cms_cors_section = section_between(generation_workflow, "CMS 默认 CORS allowed headers 只声明：", "SDK/OpenAPI 默认启用：")
    for header in ["authorization", "accept-language", "content-type", "x-timestamp", "x-reqid", "x-sign", "x-sign-alg", "x-api-version", "x-trace-id", "x-udid"]:
        if header not in cms_cors_section:
            errors.append(f"references/generation-workflow.md CMS 默认 CORS allowed headers 缺少：{header}")

    if errors:
        print("java-backend-project-generator 技能检查失败：")
        for error in errors:
            print(f"- {error}")
        return 1
    print("java-backend-project-generator 技能检查通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
