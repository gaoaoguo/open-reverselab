#!/usr/bin/env python3
"""Extract API call context from captured qingwaAA frontend bundles."""

from __future__ import annotations

import json
import re
from pathlib import Path


CASE_ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = CASE_ROOT / "recon" / "assets"
OUT = CASE_ROOT / "recon" / "api_context.json"

TERMS = [
    "shopApi", "baseURL", "api-url", "/shopApi/", "system/config",
    "goods", "order", "tradeNo", "trade_no", "submit", "result",
    "pay", "wechat", "alipay", "query_pwd", "complaint",
    "coupon_code", "channel_id", "contact", "quantity", "select_cards",
    "query_password", "Visitorid", "juuid", "buyerBlack",
]


def snippets(text: str, term: str, radius: int = 420) -> list[str]:
    out = []
    for match in re.finditer(re.escape(term), text, flags=re.I):
        start = max(0, match.start() - radius)
        end = min(len(text), match.end() + radius)
        out.append(text[start:end])
    return out[:30]


def call_like_strings(text: str) -> list[str]:
    calls = set()
    for pattern in [
        r"\.post\((.{0,520}?)\)",
        r"\.get\((.{0,520}?)\)",
        r"\.request\((.{0,520}?)\)",
        r"\$[A-Za-z0-9_]+Api",
    ]:
        try:
            calls.update(re.findall(pattern, text, flags=re.S))
        except re.error:
            continue
    filtered = []
    for call in calls:
        compact = re.sub(r"\s+", " ", call)
        if any(term.lower() in compact.lower() for term in TERMS):
            filtered.append(compact[:500])
    return sorted(filtered)[:500]


def api_paths(text: str) -> list[str]:
    paths = set(re.findall(r"""["'](/shopApi/[A-Za-z0-9_./-]+)["']""", text))
    paths.update(re.findall(r"""["'](shopApi/[A-Za-z0-9_./-]+)["']""", text))
    return sorted("/" + p.lstrip("/") for p in paths)


def route_paths(text: str) -> list[str]:
    paths = set(re.findall(r"""path:["']([^"']+)["']""", text))
    paths.update(re.findall(r"""name:["']([^"']+)["']""", text))
    return sorted(p for p in paths if any(term.lower() in p.lower() for term in TERMS))


def field_names(text: str) -> list[str]:
    names = set()
    for pattern in [
        r"""["']([A-Za-z_][A-Za-z0-9_]{2,40})["']\s*:""",
        r"""([A-Za-z_][A-Za-z0-9_]{2,40})\s*:""",
        r"""\.([A-Za-z_][A-Za-z0-9_]{2,40})""",
    ]:
        names.update(re.findall(pattern, text))
    return sorted(name for name in names if any(term.lower() in name.lower() for term in TERMS))[:500]


def main() -> int:
    result: dict[str, object] = {"files": {}, "summary": {"api_paths": [], "route_paths": [], "fields": []}}
    all_api_paths: set[str] = set()
    all_routes: set[str] = set()
    all_fields: set[str] = set()
    for path in sorted(ASSET_DIR.glob("*.js")):
        text = path.read_text(encoding="utf-8", errors="replace")
        file_api_paths = api_paths(text)
        file_routes = route_paths(text)
        file_fields = field_names(text)
        all_api_paths.update(file_api_paths)
        all_routes.update(file_routes)
        all_fields.update(file_fields)
        file_result = {
            "size": len(text),
            "terms": {term: snippets(text, term) for term in TERMS if term.lower() in text.lower()},
            "calls": call_like_strings(text),
            "api_paths": file_api_paths,
            "route_paths": file_routes,
            "fields": file_fields,
        }
        result["files"][path.name] = file_result
    result["summary"] = {
        "api_paths": sorted(all_api_paths),
        "route_paths": sorted(all_routes),
        "fields": sorted(all_fields),
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(OUT), "files": len(result["files"])}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
