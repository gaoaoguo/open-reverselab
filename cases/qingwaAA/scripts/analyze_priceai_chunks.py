"""Extract external domains from PriceAI Next.js chunks"""
import sys, re, requests, urllib3
urllib3.disable_warnings()

BASE = "https://priceai.cc/_next/static/chunks"
DPL = "eb0326a7b50747d147491d9cbcb30711463d6605"
CHUNKS = [
    "938-70e02d99f40f355e.js",
    "2128-d8a82015776aafba.js",
    "6022-39258cc6942f4f16.js",
    "9972-7d59697d8ac5b330.js",
    "971-f1490218ef43a7d6.js",
]

SKIP = [
    "google", "facebook", "github", "cloudflare", "nextjs", "vercel",
    "youtube", "twitter", "linkedin", "stripe", "openai", "alipay",
    "qq.com", "baidu", "w3.org", "schema.org", "mozilla", "npmjs",
    "priceai.cc", "dimthink.com", "googletagmanager", "polyfill",
    "radix-ui", "lucide", "tailwindcss", "heroicons", "headlessui",
    "next-intl", "algolia", "mapbox", "typekit", "fontawesome",
    "bootstrap", "jquery", "axios", "sentry", "datadog", "hotjar",
    "clarity", "mixpanel", "upstash", "pusher", "gtag", "gtm",
]

all_domains = set()

for chunk in CHUNKS:
    url = f"{BASE}/{chunk}?dpl={DPL}"
    try:
        r = requests.get(url, verify=False, timeout=15)
        if r.status_code != 200:
            continue
        js = r.text
        # Find all domain patterns
        for m in re.finditer(r"https?://([a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}", js):
            domain = m.group(0)
            dn = domain.replace("https://", "").replace("http://", "").split("/")[0]
            if not any(s in dn.lower() for s in SKIP):
                all_domains.add(dn)
    except Exception as e:
        print(f"Error fetching {chunk}: {e}")

print(f"Found {len(all_domains)} external domains:")
for d in sorted(all_domains):
    print(f"  {d}")
