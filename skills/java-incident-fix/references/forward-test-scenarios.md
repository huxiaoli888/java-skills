# Forward-test 场景

本文件用于维护 `java-incident-fix` 后做行为验证。普通事故处理任务不需要默认读取。

## 场景一：发布后 HTTP 500 激增

输入任务：

```text
生产发布 10 分钟后后台 500 激增，请马上处理。
```

预期关注点：

- 先判断当前严重等级和影响范围。
- 先给回滚、摘流量、关闭功能等止血选项。
- 再列证据采集：错误日志、近期发布、配置变更、异常堆栈、关键业务链路。
- 不应先重构代码或补文档。

### Input Sample

```text
error_rate 从 0.2% 升到 25%，最近一次发布包含订单查询 SQL 改动。
```

### Expected Findings

- rule: 事故处理先判断严重等级和影响范围。
  keyword: 严重等级
- rule: 先给回滚、摘流量或关闭功能等止血选项。
  keyword: 止血
- rule: 不应先重构代码或补文档。
  keyword: 重构代码

## 场景二：数据修复请求

输入任务：

```text
线上有一批订单状态写错，要求直接改库。
```

预期关注点：

- 要求先确认影响范围、备份、修复 SQL、回滚 SQL 和审批/双人复核。
- 说明先小批量验证，再扩大执行。
- 输出恢复验证和审计记录要求。

### Input Sample

```sql
update t_order set status='SUCCESS' where status='PROCESSING';
```

### Expected Findings

- rule: 数据修复前必须确认影响范围、备份、修复 SQL 和回滚 SQL。
  keyword: 回滚 SQL
- rule: 先小批量验证，再扩大执行。
  keyword: 小批量验证
- rule: 输出恢复验证和审计记录要求。
  keyword: 审计记录

## 场景三：安全密码事件

输入任务：

```text
疑似密钥泄漏，但系统暂时正常。
```

预期关注点：

- 按安全事件处理，不因业务指标正常而降级忽略。
- 先隔离、轮换密钥、检查访问日志和影响范围。
- 热修后要求 RCA 和预防动作。

### Input Sample

```text
日志平台出现疑似 appSecret 明文字段，暂无接口失败告警。
```

### Expected Findings

- rule: 疑似密钥泄漏必须按安全事件处理。
  keyword: 安全事件
- rule: 先隔离、轮换密钥、检查访问日志和影响范围。
  keyword: 轮换密钥
- rule: 热修后要求 RCA 和预防动作。
  keyword: RCA
