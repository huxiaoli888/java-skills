# Java 微服务安全基线

当新增或修改外部可访问 API、文件上传、签名请求、加密 payload、认证、授权或敏感日志时使用本参考。

## 基线检查

- 校验所有外部输入。
- 保留现有认证和授权层。
- 对用户域数据校验资源归属。
- 不记录 token、key、签名、密码、手机号、身份证号或明文敏感数据。
- 使用参数化 SQL 或 mapper 参数。
- 校验文件上传大小、扩展名、content type、路径和权限。
- 对签名请求，按项目既有规则校验 timestamp、nonce/replay window、签名和 body canonicalization。
- 对加密请求，保持 key 标识、算法和错误行为兼容。
