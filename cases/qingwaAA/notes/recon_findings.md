# 链动小铺 (pay.ldxp.cn) 侦察报告

## 目标信息

- **URL**: https://pay.ldxp.cn/shop/qingwaAA
- **平台**: 链动小铺 (ldxp.cn) - 自动发卡网平台
- **店铺**: 青蛙AI·低价源头 (token: qingwaAA)
- **框架**: ThinkPHP V8.0.3
- **前端**: Vue.js 3 + Arco Design
- **服务器**: ESA (阿里云 CDN/WAF)
- **卖家**: QQ群 424311895, 销量 12271, 保证金 1000

## 产品信息

- 37个卡片类商品 (ChatGPT账号/API中转/Pro订阅等)
- 价格范围: 1元 ~ 1170元
- 库存可见: stock_count 字段在 goodsList 返回中
- 手动发货 (send_order=0) 或自动发卡

## API 端点完整清单

### 商品/店铺
- `POST /shopApi/system/config` - 系统配置 ✅
- `POST /shopApi/Shop/info` - 店铺信息 (参数: token) ✅
- `POST /shopApi/Shop/goodsList` - 商品列表 (参数: token, keywords, category_id, goods_type, page, pageSize) ✅
- `POST /shopApi/Shop/goodsInfo` - 商品详情 (参数: goods_key, token) ✅
- `POST /shopApi/Shop/goodsPartDetail` - 商品部分详情 ❌ (ThinkPHP错误: method not exist:think\db\Query->part)
- `POST /shopApi/Shop/categoryList` - 分类列表 (参数: token, goods_type) ✅
- `POST /shopApi/Shop/getGoodsPrice` - 获取价格 (参数: goods_key, token) ⚠️ 始终返回0
- `POST /shopApi/Shop/getUserChannel` - 支付渠道 (参数: token) ✅
- `POST /shopApi/Shop/selectCards` - 选择卡密 (参数: goods_key, current, pageSize, ...) 
- `POST /shopApi/Shop/selectCardsPre` - 预选卡密 (参数: goods_key, ids)

### 订单
- `POST /shopApi/Pay/order` - 创建订单 (参数: goods_key, quantity, coupon_code, channel_id, contact, query_password, select_cards_ids, extend) ✅
- `POST /shopApi/Pay/query` - 查询支付状态 (参数: trade_no) ⚠️ ThinkPHP类型错误
- `GET /shopApi/Pay/payment` - 支付页面 (参数: trade_no) - 返回空
- `POST /shopApi/Order/list` - 订单列表 ⚠️ 需要人机验证
- `POST /shopApi/Order/info` - 订单详情 (参数: trade_no) ✅ 无需认证!

### 投诉
- `POST /shopApi/Order/complaintOrder` - 提交投诉
- `POST /shopApi/Order/checkNeedComplaintPwd` - 检查是否需要投诉密码
- `POST /shopApi/Order/complaintInfo` - 投诉信息
- `POST /shopApi/Order/complaintCancel` - 取消投诉
- `POST /shopApi/Order/complaintSendMessage` - 发送投诉消息

### 其他
- `POST /shopApi/Common/captchaStart` - 验证码 ✅
- `GET /shopApi/common/captchaImg.html` - 验证码图片
- `POST /shopApi/common/captchaCheck.html` - 验证码校验
- `POST /shopApi/email/send` - 发送邮件
- `POST /shopApi/upload/file` - 上传文件
- `GET /shopApi/common/buyerBlackIframe` - 买家黑名单iframe (返回juuid)
- `GET /shopApi/common/buyerBlackCheckQrcodeStatus` - 微信扫码状态检查
- `GET /shopApi/Shop/buyerBlackJs` - 买家黑名单JS

## 支付流程

1. `POST /shopApi/Shop/getGoodsPrice` → 获取价格 (疑似需登录才返回真实价格)
2. `POST /shopApi/Pay/order` → 创建订单 (服务端计算金额, 3%手续费)
   - `total_amount = price * quantity * 1.03`
3. 支付宝扫码支付
4. 支付回调 → 订单状态变更 → 发货

## 订单结构

```json
{
  "trade_no": "LD2606185UVW37",
  "goods_name": "...",
  "quantity": 1,
  "total_amount": 1.03,
  "status": 0,        // 0=未支付, 1=已支付?
  "transaction_id": "", // 支付平台交易号
  "sendout": 0,       // 0=未发货
  "contact": "...",
  "buyer_value": {},  // 卡密内容(支付后填充)
  "user": { ... },
  "goods": { ... }
}
```

## 初步漏洞发现

### 1. 未授权订单查询 (IDOR风险)
- `/shopApi/Order/info` 无需登录即可查询任意订单
- trade_no 格式: `LD` + `YYMMDD` + 6位随机字符
- 可枚举但空间较大 (36^6 ≈ 21亿)

### 2. getGoodsPrice 返回0元
- 无论是否携带Cookie,该API始终返回total_amount=0
- 但Pay/order服务端独立计算价格,不受影响

### 3. ThinkPHP 8.0.3 错误泄露
- `/shopApi/Shop/goodsPartDetail` → method not exist
- `/shopApi/Pay/query` 传入异常数据 → 类型混淆错误
- 框架版本暴露,可能存在已知CVE

### 4. 买家黑名单绕过可能
- juuid 由 iframe 生成并postMessage传递
- weixin_openid 存储在localStorage
- 两者都可能被客户端伪造

### 5. 无CSRF/Referer检查
- API 返回 `Access-Control-Allow-Origin: *`
- 可能受CSRF攻击

## 下一步攻击方向

1. ThinkPHP 8.0.3 CVE 研究
2. 并发购买竞态测试 (库存超卖)
3. 支付回调模拟
4. 卡密发货接口探测
5. 订单枚举工具开发
