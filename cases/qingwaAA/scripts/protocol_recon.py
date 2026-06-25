#!/usr/bin/env python3
"""Low-impact protocol recon for the qingwaAA payment CTF case."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


DEFAULT_TARGET = "https://pay.ldxp.cn/shop/qingwaAA"
CASE_ROOT = Path(__file__).resolve().parents[1]
RECON_DIR = CASE_ROOT / "recon"
ASSET_DIR = RECON_DIR / "assets"
PROBE_DIR = RECON_DIR / "api_probes"

KEYWORDS = (
    "api", "pay", "payment", "order", "trade", "notify", "callback",
    "webhook", "sign", "amount", "price", "total", "goods", "product",
    "shop", "status", "query", "submit", "wechat", "alipay", "refund",
    "complaint", "card", "code", "token", "auth",
)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def safe_name(url: str) -> str:
    parsed = urlparse(url)
    name = (parsed.path.strip("/") or "index").replace("/", "__")
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name)[:180]


def fetch(session: requests.Session, url: str) -> dict:
    started = time.perf_counter()
    response = session.get(url, timeout=20, allow_redirects=True, verify=False)
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    text = response.text
    return {
        "url": url,
        "final_url": response.url,
        "status_code": response.status_code,
        "elapsed_ms": elapsed_ms,
        "headers": dict(response.headers),
        "text": text,
        "sha256": sha256_text(text),
    }


def extract_asset_urls(base_url: str, html: str) -> list[str]:
    urls: set[str] = set()
    for pattern in (
        r"""<script[^>]+src=["']([^"']+)["']""",
        r"""<link[^>]+href=["']([^"']+)["']""",
    ):
        for match in re.findall(pattern, html, flags=re.I):
            absolute = urljoin(base_url, match)
            if urlparse(absolute).netloc == urlparse(base_url).netloc:
                urls.add(absolute)
    return sorted(urls)


def extract_bundle_urls(current_url: str, text: str) -> list[str]:
    urls: set[str] = set()
    parsed = urlparse(current_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    package_root = urljoin(origin, "/package/shop/")

    for match in re.findall(r"""["'](assets/[A-Za-z0-9_.-]+\.(?:js|css))["']""", text):
        urls.add(urljoin(package_root, match))

    for match in re.findall(r"""import\(["']\.\/([A-Za-z0-9_.-]+\.js)["']\)""", text):
        urls.add(urljoin(package_root + "assets/", match))

    for match in re.findall(r"""["'](\./[A-Za-z0-9_.-]+\.(?:js|css))["']""", text):
        urls.add(urljoin(package_root + "assets/", match))

    return sorted(urls)


def extract_candidates(text: str) -> dict:
    strings = set()
    for quote in ("'", '"', "`"):
        pattern = quote + r"([^" + re.escape(quote) + r"]{2,240})" + quote
        strings.update(re.findall(pattern, text))

    paths = set(re.findall(r"(?<![A-Za-z0-9_])/[A-Za-z0-9_./:{}?&=%-]{2,220}", text))
    urls = set(re.findall(r"https?://[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+", text))

    keyword_strings = sorted(
        s for s in strings
        if any(k in s.lower() for k in KEYWORDS)
    )
    keyword_paths = sorted(
        p for p in paths
        if any(k in p.lower() for k in KEYWORDS)
    )

    return {
        "keyword_strings": keyword_strings[:500],
        "keyword_paths": keyword_paths[:500],
        "urls": sorted(urls)[:300],
    }


def post_probe(session: requests.Session, base_url: str, path: str, data: dict | None = None) -> dict:
    url = urljoin(base_url, path)
    started = time.perf_counter()
    response = session.post(url, json=data or {}, timeout=20, allow_redirects=True, verify=False)
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    text = response.text
    try:
        parsed_json = response.json()
    except Exception:
        parsed_json = None
    record = {
        "url": url,
        "method": "POST",
        "request_json": data or {},
        "status_code": response.status_code,
        "elapsed_ms": elapsed_ms,
        "headers": dict(response.headers),
        "text_excerpt": text[:3000],
        "json": parsed_json,
        "text": text,
        "sha256": sha256_text(text),
    }
    name = safe_name(url) + ".json"
    (PROBE_DIR / name).write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return {k: v for k, v in record.items() if k != "text"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default=DEFAULT_TARGET)
    parser.add_argument("--max-assets", type=int, default=120)
    parser.add_argument("--api-probes", action="store_true")
    args = parser.parse_args()

    RECON_DIR.mkdir(parents=True, exist_ok=True)
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    PROBE_DIR.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({
        "User-Agent": "ReverseLab-qingwaAA-Recon/1.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": args.target,
        "Origin": f"{urlparse(args.target).scheme}://{urlparse(args.target).netloc}",
    })

    page = fetch(session, args.target)
    (RECON_DIR / "index.html").write_text(page["text"], encoding="utf-8")

    assets = []
    combined_text = page["text"]
    seen_assets: set[str] = set()
    queue = extract_asset_urls(page["final_url"], page["text"])

    while queue and len(seen_assets) < args.max_assets:
        asset_url = queue.pop(0)
        if asset_url in seen_assets:
            continue
        seen_assets.add(asset_url)
        try:
            item = fetch(session, asset_url)
        except Exception as exc:
            assets.append({"url": asset_url, "error": str(exc)})
            continue
        filename = safe_name(asset_url)
        (ASSET_DIR / filename).write_text(item["text"], encoding="utf-8")
        combined_text += "\n" + item["text"]
        assets.append({k: v for k, v in item.items() if k != "text"})
        for discovered in extract_bundle_urls(asset_url, item["text"]):
            if discovered not in seen_assets and discovered not in queue:
                queue.append(discovered)
        time.sleep(0.15)

    candidates = extract_candidates(combined_text)
    probes = []
    if args.api_probes:
        probes.append(post_probe(session, args.target, "/shopApi/system/config"))
        probes.append(post_probe(session, args.target, "/shopApi/Shop/info", {"token": "qingwaAA"}))
        probes.append(post_probe(session, args.target, "/shopApi/Shop/goodsList", {
            "token": "qingwaAA",
            "keywords": "",
            "category_id": "",
            "goods_type": "",
            "page": 1,
            "pageSize": 10,
        }))

    summary = {
        "target": args.target,
        "captured_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "page": {k: v for k, v in page.items() if k != "text"},
        "assets": assets,
        "candidates": candidates,
        "api_probes": probes,
    }
    (RECON_DIR / "protocol_recon.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (RECON_DIR / "candidate_paths.txt").write_text(
        "\n".join(candidates["keyword_paths"]) + "\n",
        encoding="utf-8",
    )
    (RECON_DIR / "candidate_strings.txt").write_text(
        "\n".join(candidates["keyword_strings"]) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({
        "target": args.target,
        "page_status": page["status_code"],
        "assets": len(assets),
        "candidate_paths": len(candidates["keyword_paths"]),
        "candidate_strings": len(candidates["keyword_strings"]),
        "api_probes": len(probes),
        "out": str(RECON_DIR / "protocol_recon.json"),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
