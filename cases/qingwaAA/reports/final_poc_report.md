# 链动小铺 最终利用报告

## 核心发现

### 卡密获取路径的阻断点

```
创建订单 → 支付(支付宝RSA2签名) → notify回调 → 状态变更 → 自动发货 → buyer_value写入卡密
                                    ↑
                              此处被RSA2签名保护
                              无法伪造支付宝异步通知
```

### 已确认的漏洞 (5项)

| # | 漏洞 | 端点 | 危害 |
|---|------|------|------|
| 1 | 无认证下单 | POST /shopApi/Pay/order | 任意创建订单,contact可控 |
| 2 | 全量库存泄露 | POST /shopApi/Shop/goodsList | 37商品,5711件库存,总值¥114,922 |
| 3 | getGoodsPrice=0 | POST /shopApi/Shop/getGoodsPrice | 37/37商品价格API返回0 |
| 4 | 黑名单绕过 | buyerBlackIframe | juuid+openid全客户端可控 |
| 5 | 回调端点泄露 | 支付宝支付页面 | notify/callback URL暴露 |

### 回调端点发现

```
notify_url: https://pay.ldxp.cn/payApi/AlipayPc/notify (POST, RSA2签名验证)
return_url: https://pay.ldxp.cn/payApi/AlipayPc/callback (GET, 不验证签名但也不触发支付确认)
支付网关: https://openapi.alipay.com/gateway.do
App ID: 2021004190645986
SDK: alipay-easysdk-php-2.2.3
```

### 为什么无法直接获取卡密

1. **价格服务端计算** - Pay/order 强制 price*1.03，extend篡改无效
2. **支付宝RSA2签名** - notify端点强制验证签名，无签名→返回error
3. **只支持真实支付** - channel_id仅1(支付宝)，free/test/balance均拒绝
4. **WAF保护** - 阿里云ESA在敏感端点(Order/info等)有人机验证
5. **发货依赖支付回调** - send_order=1自动发货，但需notify触发

### 文件产出

```
cases/qingwaAA/
├── exports/
│   ├── inventory_dump.json       # 37商品全量库存
│   ├── price_anomaly.json        # getGoodsPrice全量对比
│   └── exploit_results.json      # 自动化测试结果
├── scripts/
│   ├── poc_reproduce.py          # 5项漏洞完整复现脚本
│   ├── exploit_protocol.py       # 自动化利用协议
│   └── extract_js_strings.py     # JS逆向分析工具
├── reports/
│   ├── final_report.md           # 完整分析报告
│   ├── poc_results.md            # 复现结果
│   └── final_poc_report.md       # 本报告
└── notes/
    └── recon_findings.md         # 侦察记录
```
