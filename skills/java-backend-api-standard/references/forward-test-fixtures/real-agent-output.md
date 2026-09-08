# Forward-test 真实子任务输出

> 来源：独立子任务使用 `java-backend-api-standard` 对 CMS/SDK 请求头与表单签名场景做评审。

## 评审结论

1. **样例请求不满足受保护 CMS 写接口契约。**
   `POST /cms/order/create` 是受保护写接口，且属于订单类高风险交易接口。样例只带了 `authorization` 和 `x-sign`，缺少至少这些头：`x-reqid`、`x-udid`、`x-sign-alg`、`x-api-version`；若启用防重放，订单创建还应带 `x-timestamp`。
   当前样例应判定为契约不完整，不能进入业务 Service。

2. **`application/x-www-form-urlencoded` 对 CMS 是允许的，但签名规则必须写清。**
   CMS 表单请求可以支持：

```http
Content-Type: application/x-www-form-urlencoded
```

   但 `x-sign` 必须基于 HTTP 原始 form body bytes 计算，也就是签名输入要使用原始 `amount=10&orderNo=A001` 字节，不能由后端解析参数后重新排序、重新编码或重新拼接。

3. **SDK 不应支持 form-urlencoded。**
   SDK 契约应限制为 `GET` 和 `POST application/json; charset=UTF-8`。如果 SDK 收到 `application/x-www-form-urlencoded`，建议返回 `415 Unsupported Media Type` 或统一错误码响应，避免 CMS/SDK 签名口径混淆。

4. **路由风格不符合推荐契约。**
   `/cms/order/create` 是动作式路径，建议标准化为版本化资源路径，例如：

```text
POST /api/v1/cms/orders
```

   或在确有领域命令时使用：

```text
POST /api/v1/cms/orders/{orderNo}/cancel
```

5. **订单创建必须定义业务幂等。**
   `orderNo=A001` 可作为业务唯一键，但契约需要明确：相同调用方 + 相同 `orderNo` + 相同请求指纹可返回原结果；相同 `orderNo` + 不同请求内容应返回幂等冲突错误，例如 `AC0005` 或业务模块码。不要使用公共 `Idempotency-Key` 请求头替代业务唯一键。

6. **公开接口白名单规则正确，但要排除整条认证链。**
   登录、验证码、探活应放入 `auth-exclude-paths`，不要求 token、签名、`x-udid`，也不进入受保护接口 replay cache。它们仍需要限流，尤其是登录和验证码。

7. **仓库现有文档/示例存在旧契约残留。**
   `renren-standard-template-transformation-pdr-v1.0.md` 使用 `x-nonce/x-signature-alg/x-signature`，与当前标准要求的 `x-reqid/x-sign-alg/x-sign` 冲突。
   `SignatureHeaders.java` 仍定义 `X-App-Id`、`X-Nonce`、`X-Signature`、`X-Body-Hash`、`Idempotency-Key`，也不符合当前标准。

8. **仓库示例响应格式不符合统一响应契约。**
   `ApiResult.java` 使用 `int code/msg/traceId/timestamp`，而标准要求 `reqid/code/message/ts/data`，其中 `code` 应为字符串，成功码为 `"000000"`，`traceId` 不应出现在公开 JSON 响应体。

9. **仓库示例 OrderController 不是 CMS/SDK 契约实现。**
   `OrderController.java` 路由为 `/api/v1/secure/orders`，创建接口只使用 `@RequestBody` JSON，不支持 CMS form-urlencoded，也没有体现 CMS 与 SDK 的模块/DTO/安全边界。该示例不能直接作为本任务的 CMS/SDK API 契约依据。

**最终判断：** 样例请求方向部分正确，`authorization` 和 `x-sign` 使用位置正确，CMS form body 也允许；但缺少请求唯一编号、设备标识、签名算法、契约版本和交易防重放/幂等约束，不能通过标准评审。
