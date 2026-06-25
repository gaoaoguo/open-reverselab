#!/usr/bin/env python3
"""
TikTok Shop 商品批量爬虫 - 通过 ScrapeCreators API
支持: 单个URL、多个URL、含product_id的txt文件、关键词搜索批量
"""

import requests, json, argparse, sys, re, time, csv
from urllib.parse import urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed

API_KEY = "BQU1bte7xcOgiGIpcfH27L6EWOq2"
BASE = "https://api.scrapecreators.com/v1/tiktok"
MAX_WORKERS = 3  # 免费API限速
DELAY = 1.0


def extract_product_id(url: str) -> str:
    """从TikTok商品链接提取product_id"""
    if url.strip().isdigit():
        return url.strip()
    m = re.search(r"/product/(\d+)", url)
    if m:
        return m.group(1)
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    return params.get("product_id", [None])[0]


def search_products(query: str, amount: int = 50):
    """搜索商品，返回product_id列表"""
    print(f"  搜索: {query}")
    r = requests.get(
        f"{BASE}/shop/search",
        headers={"x-api-key": API_KEY},
        params={"query": query, "amount": amount},
        timeout=30,
    )
    d = r.json()
    products = d.get("products", [])
    ids = [p["product_id"] for p in products if "product_id" in p]
    print(f"  找到 {len(ids)} 个商品")
    return ids


def get_product_detail(product_id: str):
    """获取单个商品详情"""
    r = requests.get(
        f"{BASE}/product",
        headers={"x-api-key": API_KEY},
        params={"product_id": product_id},
        timeout=30,
    )
    d = r.json()
    if not d.get("success"):
        raise Exception(f"API失败: {d.get('message', 'unknown')}")
    return d


def parse_product(data: dict) -> dict:
    """解析商品数据为结构化字段"""
    pb = data.get("product_base", {})

    # 描述
    desc = ""
    desc3 = pb.get("desc_detailv3", "")
    if isinstance(desc3, list):
        for item in desc3:
            if isinstance(item, dict):
                for block in item.get("ec_rich_blocks", []):
                    img_url = ""
                    for t in block.get("xl_ec_rich_text", {}).get("ec_rich_texts", []):
                        tmpl = t.get("template", "")
                        for k, v in t.get("arguments", {}).items():
                            txt = v.get("text_attribute", {}).get("text", "")
                            tmpl = tmpl.replace(k, txt)
                        desc += tmpl + " "
                    if block.get("rich_block_type") == 2:
                        urls = block.get("ec_rich_image", {}).get("image", {}).get("url_list", [])
                        if urls:
                            desc += f"[IMG:{urls[0]}] "

    # 图片
    images = []
    for img in pb.get("images", []):
        urls = img.get("url_list", [])
        if urls:
            images.append(urls[0])

    # 规格图
    spec_images = {}
    for sp in data.get("sale_props", []):
        for pv in sp.get("sale_prop_values", []):
            urls = pv.get("image", {}).get("url_list", pv.get("image", {}).get("thumb_url_list", []))
            if urls:
                spec_images[pv.get("prop_value", "")] = urls[0]

    # SKU
    skus = []
    for sku in data.get("skus", []):
        price = sku.get("price", {}).get("real_price", {})
        props = sku.get("sku_sale_props", [])
        skus.append({
            "sku_id": sku["sku_id"],
            "price": price.get("price_str", "?"),
            "currency": price.get("currency", "USD"),
            "stock": sku["stock"],
            "specs": {p["prop_name"]: p["prop_value"] for p in props},
        })

    # 规格列表
    specs = []
    for sp in data.get("sale_props", []):
        specs.append({
            "name": sp.get("prop_name", ""),
            "values": [v.get("prop_value", "") for v in sp.get("sale_prop_values", [])],
            "has_image": sp.get("has_image", False),
        })

    # 属性
    attributes = {}
    for s in pb.get("specifications", []):
        attributes[s.get("name", "")] = s.get("value", "")

    return {
        "product_id": data.get("product_id"),
        "title": pb.get("title", ""),
        "description": desc.strip(),
        "price_min": pb.get("min_price", {}).get("price_prefix", ""),
        "category": pb.get("category_name", ""),
        "brand": attributes.get("Brand", ""),
        "sold_count": pb.get("sold_count", 0),
        "seller": data.get("seller", {}).get("name", ""),
        "seller_rating": data.get("seller", {}).get("rating", ""),
        "main_image": images[0] if images else "",
        "images": images[1:],
        "spec_images": spec_images,
        "specs": specs,
        "attributes": attributes,
        "skus": skus,
    }


def fetch_one(pid: str, idx: int, total: int):
    """爬取单个商品(线程安全)"""
    try:
        print(f"  [{idx}/{total}] {pid} ...")
        data = get_product_detail(pid)
        product = parse_product(data)
        print(f"  [{idx}/{total}] {pid} ✓ {product['title'][:40]} ({len(product['skus'])}SKU)")
        return product
    except Exception as e:
        print(f"  [{idx}/{total}] {pid} ✗ {e}")
        return {"product_id": pid, "error": str(e)}


def batch_fetch(product_ids: list, output: str):
    """批量爬取"""
    total = len(product_ids)
    print(f"\n批量爬取 {total} 个商品...\n")
    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(fetch_one, pid, i + 1, total): pid for i, pid in enumerate(product_ids)}
        for f in as_completed(futures):
            results.append(f.result())
            time.sleep(DELAY)

    # 按输入顺序排序
    order = {pid: i for i, pid in enumerate(product_ids)}
    results.sort(key=lambda r: order.get(r.get("product_id", ""), 9999))

    # 保存JSON
    with open(output, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 也保存CSV摘要
    csv_file = output.replace(".json", ".csv")
    with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["product_id", "title", "price", "stock", "seller", "sold_count", "category"])
        for r in results:
            skus = r.get("skus", [])
            prices = [s["price"] for s in skus if s.get("price")]
            stocks = sum(s.get("stock", 0) for s in skus)
            writer.writerow([
                r.get("product_id"), r.get("title"),
                "/".join(prices) if prices else "?",
                stocks,
                r.get("seller"), r.get("sold_count"), r.get("category"),
            ])

    success = sum(1 for r in results if "error" not in r)
    print(f"\n完成: {success}/{total} 成功")
    print(f"JSON: {output}")
    print(f"CSV:  {csv_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TikTok Shop商品批量爬虫")
    parser.add_argument("inputs", nargs="*", help="商品链接/ID，多个空格分隔")
    parser.add_argument("-f", "--file", help="从文件读取URL/ID (每行一个)")
    parser.add_argument("-s", "--search", help="关键词搜索并批量获取")
    parser.add_argument("-n", "--num", type=int, default=50, help="搜索结果数量")
    parser.add_argument("-o", "--output", default="tiktok_batch_output.json", help="输出文件")
    args = parser.parse_args()

    product_ids = []

    # 命令行参数
    for inp in args.inputs:
        pid = extract_product_id(inp)
        if pid:
            product_ids.append(pid)
        else:
            print(f"警告: 无法解析 '{inp}'")

    # 文件输入
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    pid = extract_product_id(line)
                    if pid:
                        product_ids.append(pid)

    # 搜索
    if args.search:
        ids = search_products(args.search, args.num)
        product_ids.extend(ids)

    if not product_ids:
        print("用法:")
        print("  单个: python tiktok_scraper.py 1729445131259252744")
        print("  多个: python tiktok_scraper.py id1 id2 id3")
        print("  文件: python tiktok_scraper.py -f urls.txt")
        print("  搜索: python tiktok_scraper.py -s 'POP MART blind box' -n 20")
        sys.exit(1)

    # 去重
    product_ids = list(dict.fromkeys(product_ids))
    batch_fetch(product_ids, args.output)
