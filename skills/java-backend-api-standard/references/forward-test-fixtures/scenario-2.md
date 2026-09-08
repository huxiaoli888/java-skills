# Fixture: 场景二：异常与日志边界

正常业务失败不应通过 BusinessException 作为常规控制流
catch 块处理异常时缺少 log.error、继续抛出或 onError 回调
