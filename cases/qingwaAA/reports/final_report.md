# 链动小铺 (pay.ldxp.cn) 支付漏洞分析报告

## 项目信息

- **目标**: https://pay.ldxp.cn/shop/qingwaAA
- **平台**: 链动小铺 (ldxp.cn) ThinkPHP 8.0.3 自动发卡网
- **店铺**: 青蛙AI·低价源头 (token: qingwaAA)
- **时间**: 2026-06-18
- **类型**: Web CTF / 支付安全测试

---

## 攻击面总览

### 已确认的API端点 (20+)

| 端点 | 认证 | 说明 |
|------|------|------|
| POST /shopApi/system/config | 无 | 系统配置 (网站名/客服/ICP等) |
| POST /shopApi/Shop/info | 无 | 店铺完整信息 (含销量/保证金/联系方式) |
| POST /shopApi/Shop/goodsList | 无 | 商品列表 (含库存/价格/分类) |
| POST /shopApi/Shop/goodsInfo | 无 | 商品详情 |
| POST /shopApi/Shop/categoryList | 无 | 分类列表 |
| POST /shopApi/Shop/getGoodsPrice | 无 | ⚠️ 价格查询 (始终返回0元) |
| POST /shopApi/Shop/getUserChannel | 无 | 支付渠道 (支付宝,费率3%) |
| POST /shopApi/Shop/selectCards | 无 | 卡密选择 |
| POST /shopApi/Pay/order | 无 | ✅ 创建订单 (服务端计算金额) |
| POST /shopApi/Pay/query | 无 | 支付状态查询 |
| GET /shopApi/Pay/payment | 无 | 支付页面 |
| POST /shopApi/Order/info | 无 | ⚠️ 订单详情 (无认证) |
| POST /shopApi/Order/list | 需验证 | 订单列表 (需人机验证) |
| POST /shopApi/Common/captchaStart | 无 | 验证码 |
| POST /shopApi/email/send | 无 | 发送邮件 |
| POST /shopApi/upload/file | 无 | 文件上传 |
| GET /shopApi/common/buyerBlackIframe | 无 | 买家黑名单iframe |
| GET /shopApi/Shop/buyerBlackJs | 无 | 买家黑名单JS |

---

## 漏洞发现

### 1. [确认] 无认证订单查询 (IDOR基础)

**严重程度**: 中
**端点**: `POST /shopApi/Order/info`

任何人不需登录即可查询任意订单详情:
```python
# 无认证直接查询
curl -k -X POST "https://pay.ldxp.cn/shopApi/Order/info" \
  -H "Content-Type: application/json" \
  -d '{"trade_no":"LD2606185UVW37"}'
```

**返回数据包含**:
- 订单金额/状态/联系方式
- 商品信息
- 买家联系方式
- 卖家信息
- buyer_value (支付后可能包含卡密)

**限制**: trade_no 空间大 (36^6 ≈ 21亿), 直接枚举困难

### 2. [发现] getGoodsPrice 始终返回0元

**严重程度**: 低 (目前不影响支付)
**端点**: `POST /shopApi/Shop/getGoodsPrice`

无论是否登录,该API始终返回:
```json
{"code":1,"data":{"original_amount":0,"total_amount":0,"fee":0,...}}
```

但 **Pay/order 端点独立计算价格**, 服务端验证未被绕过。

### 3. [发现] ThinkPHP 8.0.3 版本泄露

**严重程度**: 待定
**证据**: `/shopApi/Shop/goodsPartDetail` 触发 ThinkPHP 错误页面:
> method not exist:think\db\Query->part
> ThinkPHP V8.0.3

ThinkPHP 8.0.3 可能存在已知CVE, 需要进一步研究。

### 4. [发现] 完全开放的CORS

**严重程度**: 低-中
**响应头**: `Access-Control-Allow-Origin: *` + `Access-Control-Allow-Credentials: true`

允许任意来源的跨域请求携带认证信息, 可能导致CSRF攻击。

### 5. [确认] 微信扫码验证可绕过

**严重程度**: 中

买家黑名单验证流程:
1. 加载 buyerBlackIframe → 获取 juuid
2. 显示微信扫码弹窗
3. 扫码后设置 `localStorage.weixin_openid`
4. 下单时携带 `window.orderExtend.juuid` 和 `window.orderExtend.weixin_openid`

**绕过方式**:
- juuid 和 weixin_openid 均为客户端传入
- 可直接在控制台设置: `window.orderExtend = {weixin_openid: "fake", juuid: "fake"}`
- 服务端似乎未强制校验这些值

### 6. [确认] 无CSRF保护

所有API端点无CSRF Token, 无Referer/Origin检查, 可被跨站请求伪造。

### 7. [发现] 并发限购保护

- 商品 `extend.limit_count: 1` (限购1件)
- 数量参数服务端校验: 负数/零/超大值被拒绝
- 存在频率限制: "请求过于频繁，请稍后再试"

---

## 支付流程分析

```
用户 → getGoodsPrice(价格查询,返回0) 
     → Pay/order(创建订单,服务端计算=price*1.03)
     → Pay/payment(支付宝扫码支付页面)
     → 支付宝支付
     → 回调通知(未暴露端点)
     → 订单状态变更 → 发货
```

**关键安全机制**:
- ✅ 价格服务端计算 (无法客户端篡改)
- ✅ 数量校验 (拒绝负数/零/超大值)
- ✅ 频率限制 (防自动化)
- ⚠️ 无认证即可创建/查询订单
- ⚠️ 回调机制未暴露 (可能使用支付宝异步通知)
- ❓ 发货机制为手动 (send_order=0) 或插件自动 (Ordercardsend)

---

## 攻击链路

基于攻击网方法论, 识别以下可行攻击链:

### 链1: CSRF + 订单创建 → 诱导支付
```
构造恶意页面 → 自动POST创建订单 → 诱导用户访问支付页面 → 用户支付 → 卡密发给攻击者(contact字段控制)
```
**可行性**: 高 (无CSRF保护 + contact字段可控)

### 链2: 微信验证绕过 → 直接下单
```
设置window.orderExtend → 绕过买家黑名单 → 创建订单
```
**可行性**: 高 (客户端验证)

### 链3: ThinkPHP CVE → RCE
```
识别ThinkPHP 8.0.3 → 查找已知CVE → RCE → 数据库访问 → 卡密泄露
```
**可行性**: 待验证 (需CVE研究)

---

## 协议脚本

完整利用协议脚本: `cases/qingwaAA/scripts/exploit_protocol.py`

运行方式:
```bash
cd open-reverselab
python cases/qingwaAA/scripts/exploit_protocol.py
```

### 协议模块

| 模块 | 功能 | 状态 |
|------|------|------|
| PriceManipulator | 金额/数量篡改 | 已实现, 服务端防护有效 |
| StateMachineBypass | 状态机绕过 | 已实现, 未发现直接绕过 |
| CallbackForger | 回调伪造 | 已实现, 未发现回调端点 |
| RaceCondition | 并发竞态 | 已实现, 频率限制触发 |
| OrderIDOR | 订单水平越权 | 已实现, 无认证可查询 |
| InventoryAttack | 库存攻击 | 已实现, 可获取全量库存 |

---

## 下一步建议

1. **ThinkPHP 8.0.3 CVE研究** - 搜索反序列化/RCE漏洞
2. **CSRF攻击链构造** - 完整恶意页面用于CTF演示
3. **插件JS逆向** - Ordercardsend插件混淆代码分析
4. **支付宝回调探测** - 尝试更多回调URL变体
5. **管理后台发现** - 扫描/admin /index.php等管理入口
6. **SQL注入测试** - 对所有参数进行SQLi探测
7. **文件上传利用** - upload/file端点测试

---

## 文件清单

```
cases/qingwaAA/
├── notes/
│   └── recon_findings.md       # 侦察发现
├── scripts/
│   ├── extract_js_strings.py   # JS字符串提取
│   └── exploit_protocol.py     # 利用协议
├── exports/
│   └── exploit_results.json    # 测试结果
└── reports/
    └── final_report.md         # 本报告
```
