#!/usr/bin/env python3
"""Extract API endpoints and key strings from minified JS"""
import re
import sys
import requests
import urllib3
urllib3.disable_warnings()

def extract_strings(js_content, min_len=4):
    """Extract all string literals"""
    strings = re.findall(r'"([^"]{'+str(min_len)+r',})"', js_content)
    strings += re.findall(r"'([^']{"+str(min_len)+r",})'", js_content)
    return set(strings)

def find_api_patterns(strings):
    """Filter strings that look like API paths"""
    patterns = []
    keywords = ['api', 'pay', 'order', 'url', 'http', 'get', 'post', 'notify',
                'callback', 'sign', 'goods', 'product', 'shop', 'token', 'auth',
                'login', 'user', 'create', 'query', 'list', 'delete', 'update',
                'checkout', 'cart', 'buy', 'wx', 'alipay', 'wechat', 'recharge',
                'redeem', 'coupon', 'card', 'cdkey', 'code', 'status', 'info',
                'detail', 'submit', 'confirm', 'cancel', 'refund', 'webhook',
                'trade', 'transaction', 'amount', 'price', 'total', 'plan',
                'subscription', 'vip', 'member', 'balance', 'credit']
    for s in sorted(strings):
        s_lower = s.lower()
        if any(kw in s_lower for kw in keywords):
            patterns.append(s)
    return patterns

def main():
    urls = [
        "https://pay.ldxp.cn/package/shop/assets/index.eb07c454.js",
        "https://pay.ldxp.cn/package/shop/assets/apply.767ae10c.js",
        "https://pay.ldxp.cn/package/shop/assets/info.2ac92e47.js",
        "https://pay.ldxp.cn/package/shop/assets/order-layout.a13805b5.js",
        "https://pay.ldxp.cn/package/shop/assets/plane.1e1294e3.js",
        "https://pay.ldxp.cn/package/shop/assets/select-cards.4cb9c683.js",
    ]

    all_strings = set()
    for url in urls:
        try:
            r = requests.get(url, verify=False, timeout=10)
            if r.status_code == 200:
                strings = extract_strings(r.text)
                print(f"[*] {url.split('/')[-1]}: {len(strings)} strings")
                all_strings.update(strings)
        except Exception as e:
            print(f"[!] {url}: {e}")

    api_patterns = find_api_patterns(all_strings)

    print("\n=== API-Related Strings ===")
    for s in api_patterns:
        print(f"  {s}")

if __name__ == "__main__":
    main()
