# Forward-test 场景

## 目录

- [场景一：CMS 与 SDK 请求头标准](#场景一cms-与-sdk-请求头标准)
- [场景二：异常与日志边界](#场景二异常与日志边界)
- [场景三：复杂 SQL 放置位置](#场景三复杂-sql-放置位置)

本文件用于维护 `java-backend-api-standard` 后做前向验证。普通 API 设计、评审或实现任务不需要默认读取。

## 场景一：CMS 与 SDK 请求头标准

输入任务：

```text
请评审一个 Spring Boot 前后端分离项目的 CMS 和 SDK API 契约。
CMS 支持 GET、POST JSON 和 application/x-www-form-urlencoded。
SDK 支持 GET 和 POST JSON。
登录、验证码、探活为公开接口。
```

预期关注点：

- CMS 和 SDK 都要求 `x-reqid/x-timestamp/x-sign/x-sign-alg/x-api-version`。
- SDK 额外要求 `x-api-key`。
- 登录后的接口通过 `authorization: Bearer token` 传递登录态。
- 公开接口可没有 `authorization` 和 `x-udid`，但需要防篡改时仍要签名。
- POST JSON 使用原始 JSON body 参与摘要，GET 使用排序 query，CMS 表单使用标准表单键值规范化。

### Input Sample

```http
POST /cms/order/create HTTP/1.1
Content-Type: application/x-www-form-urlencoded
authorization: Bearer token
x-sign: signature

amount=10&orderNo=A001
```

### Expected Findings

- rule: cms-sdk-header-contract
  keyword: CMS 和 SDK 都要补充 x-sign-alg 与 x-api-version
- rule: form-signature-canonicalization
  keyword: CMS 表单提交必须使用 HTTP 原始 form body bytes 参与验签

## 场景二：异常与日志边界

输入代码特征：

```text
service 层通过 throw new BusinessException 表达库存不足。
catch Exception 后只 return false，没有 log.error，也没有继续抛出。
```

预期关注点：

- 正常业务失败不应在 service/domain/application 层通过异常作为常规控制流。
- 真正程序异常不得吞掉，必须 `log.error` 打印、继续抛出，或进入明确的 onError 回调。
- Controller 边界可以把业务决策结果转换为统一错误码响应。

### Input Sample

```java
@Service
class StockService {
    boolean reserve(String sku) {
        try {
            if (sku == null) {
                throw new BusinessException("库存不足");
            }
            return true;
        } catch (Exception ex) {
            return false;
        }
    }
}
```

### Expected Findings

- rule: business-exception-control-flow
  keyword: 正常业务失败不应通过 BusinessException 作为常规控制流
- rule: swallowed-exception
  keyword: catch 块处理异常时缺少 log.error、继续抛出或 onError 回调

## 场景三：复杂 SQL 放置位置

输入代码特征：

```text
Mapper Java 注解里写了多表 join、group by、case when 和动态条件。
```

预期关注点：

- 复杂 SQL 应参考 renren 项目放到 Mapper XML。
- Mapper Java 注解只保留简单查询。
- 动态字段或排序必须使用服务端 allowlist，不能直接拼接用户输入。

### Input Sample

```java
@Mapper
interface OrderMapper {
    @Select("select u.id, count(o.id) total from user u left join orders o on u.id=o.user_id group by u.id order by ${sort}")
    List<Map<String, Object>> stats(@Param("sort") String sort);
}
```

### Expected Findings

- rule: complex-sql-location
  keyword: 复杂 SQL 应放到 Mapper XML
- rule: sql-injection-risk
  keyword: 动态字段应使用参数绑定或服务端白名单
