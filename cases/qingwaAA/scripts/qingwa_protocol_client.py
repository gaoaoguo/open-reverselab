#!/usr/bin/env python3
"""Low-impact protocol client for qingwaAA."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


BASE = "https://pay.ldxp.cn"


def post(session: requests.Session, path: str, payload: dict) -> dict:
    resp = session.post(f"{BASE}{path}", json=payload, timeout=20, verify=False)
    try:
        body = resp.json()
    except Exception:
        body = {"raw": resp.text}
    return {
        "url": f"{BASE}{path}",
        "status": resp.status_code,
        "headers": dict(resp.headers),
        "request": payload,
        "response": body,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", default="qingwaAA")
    parser.add_argument("--trade-no", default="")
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    s = requests.Session()
    s.headers.update({"User-Agent": "ReverseLab-qingwaAA-Client/1.0", "Origin": BASE, "Referer": f"{BASE}/shop/{args.token}"})

    result = {
        "system_config": post(s, "/shopApi/system/config", {}),
        "shop_info": post(s, "/shopApi/Shop/goodsList", {
            "token": args.token,
            "keywords": "",
            "category_id": "",
            "goods_type": "",
            "page": 1,
            "pageSize": 10,
        }),
    }
    if args.trade_no:
        result["order_info"] = post(s, "/shopApi/Order/info", {"trade_no": args.trade_no})
        result["pay_query"] = post(s, "/shopApi/Pay/query", {"trade_no": args.trade_no})

    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
