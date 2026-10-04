import json
import os
import random
import time
import uuid
from datetime import datetime, timezone
from urllib.parse import quote

import httpcloak
import requests

WEBHOOK = ""
RETRY_DELAY = 5
REPING_COOLDOWN = 60
SOLD_OUT_PINGS = True
ITEMS = [
    {"name": "PlayStation 5 Pro console", "item_id": "1SZQHN3LOSE0", "offer_id": "522E8F769E743495A36796D336BB4300"},
]

BASE = "https://www.walmart.ca"
OFFER_HASH = "52fdbf05cef8279aa9d288434e114c3b7998e33e5b387e27377c0863e5c70ac0"
PROXIES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proxies.txt")
WARM_URL = f"{BASE}/en/browse/toys/trading-cards/pokemon-cards/10011_31745_6000204969672?facet=retailer_type%3AWalmart"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36"
SEC_CH_UA = '"Chromium";v="152", "Not?A_Brand";v="24", "Google Chrome";v="152"'
NAV_HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "accept-language": "en-CA,en;q=0.9",
    "sec-ch-ua": SEC_CH_UA,
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "user-agent": UA,
}


def log(msg):
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


def proxy_url(line):
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    if "://" in line:
        return line
    if "@" in line:
        return "http://" + line
    parts = line.split(":")
    if len(parts) == 4:
        return f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
    if len(parts) == 2:
        return f"http://{line}"
    return None


def pick_proxy():
    try:
        with open(PROXIES_FILE, encoding="utf-8") as f:
            proxies = [u for u in (proxy_url(line) for line in f) if u]
    except OSError:
        proxies = []
    return random.choice(proxies) if proxies else None


def proxy_label(proxy):
    return proxy.rsplit("@", 1)[-1] if proxy else "localhost"


def new_session():
    proxy = pick_proxy()
    session = httpcloak.Session(preset="chrome-latest-windows", timeout=30, proxy=proxy)
    r = session.get(WARM_URL, headers=NAV_HEADERS)
    if r.status_code != 200:
        raise RuntimeError(f"warm-up page HTTP {r.status_code} on {proxy_label(proxy)}")
    log(f"session warmed on {proxy_label(proxy)}")
    return session


def offer_headers(item):
    cid = uuid.uuid4().hex[:32]
    referer = f"{BASE}/en/ip/{item['item_id']}"
    return {
        "accept": "application/json",
        "accept-language": "en-CA",
        "content-type": "application/json",
        "downlink": "10",
        "dpr": "1",
        "priority": "u=1, i",
        "referer": referer,
        "sec-ch-ua": SEC_CH_UA,
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "tenant-id": "qxjed8",
        "user-agent": UA,
        "wm_mp": "true",
        "wm_page_url": referer,
        "wm_qos.correlation_id": cid,
        "x-apollo-operation-name": "OfferById",
        "x-enable-server-timing": "1",
        "x-latency-trace": "1",
        "x-o-bu": "WALMART-CA",
        "x-o-ccm": "server",
        "x-o-correlation-id": cid,
        "x-o-gql-query": "query OfferById",
        "x-o-mart": "B2C",
        "x-o-platform": "rweb",
        "x-o-platform-version": "caweb-1.176.0-0c9742e30918adcbaf5d8d579c39db2216f7a38d-9150011r",
        "x-o-segment": "oaoh",
    }


def check(session, item):
    variables = {"itemId": item["item_id"], "offerId": item.get("offer_id") or "", "selected": False, "fIlc": True}
    url = f"{BASE}/orchestra/home/graphql/OfferById/{OFFER_HASH}?variables=" + quote(json.dumps(variables, separators=(",", ":")))
    r = session.get(url, headers=offer_headers(item))
    if r.status_code != 200:
        return None, f"HTTP {r.status_code}"
    try:
        product = (r.json().get("data") or {}).get("product")
    except ValueError:
        return None, "non-JSON response (blocked?)"
    if not product:
        return None, "no product in response"
    options = [o for o in product.get("fulfillmentOptions") or [] if isinstance(o, dict)]
    quantities = [o["availableQuantity"] for o in options if isinstance(o.get("availableQuantity"), int)]
    limits = [o.get("orderLimit") or o.get("maxOrderQuantity") for o in options if o.get("orderLimit") or o.get("maxOrderQuantity")]
    status = product.get("availabilityStatus") or ""
    available = status == "IN_STOCK" or any(o.get("availabilityStatus") == "AVAILABLE" for o in options)
    return {
        "in_stock": available and (not quantities or max(quantities) > 0),
        "status": status or "UNKNOWN",
        "qty": max(quantities) if quantities else None,
        "limit": limits[0] if limits else None,
        "price": ((product.get("priceInfo") or {}).get("currentPrice") or {}).get("priceString"),
        "seller": (product.get("sellerName") or product.get("sellerDisplayName") or "").strip(),
        "options": ", ".join(f"{o.get('type', '?').lower()} {o.get('availabilityStatus', '?')}" for o in options),
    }, ""


def send(item, state, kind):
    if not WEBHOOK:
        log(f"(no WEBHOOK set) would ping {kind}: {item['name']}")
        return
    fields = [
        {"name": "Type", "value": kind, "inline": True},
        {"name": "Status", "value": state["status"], "inline": True},
        {"name": "Stock", "value": str(state["qty"]) if state["qty"] is not None else "Unknown", "inline": True},
        {"name": "Price", "value": state["price"] or "Unknown", "inline": True},
        {"name": "Seller", "value": state["seller"] or "Unknown", "inline": True},
        {"name": "Item ID", "value": item["item_id"], "inline": True},
        {"name": "Offer ID", "value": item.get("offer_id") or "Default", "inline": True},
    ]
    if state["limit"]:
        fields.append({"name": "Cart Limit", "value": str(state["limit"]), "inline": True})
    embed = {
        "title": item["name"][:256],
        "url": f"{BASE}/en/ip/{item['item_id']}",
        "color": 0x2ECC71 if kind == "In Stock" else 0x95A5A6,
        "fields": fields,
        "footer": {"text": "Walmart CA · item"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    try:
        requests.post(WEBHOOK, json={"embeds": [embed]}, timeout=10)
    except Exception as e:
        log(f"webhook failed: {e}")


def main():
    last = {}
    pinged_at = {}
    announced = set()
    session = None
    while True:
        failed = None
        for item in ITEMS:
            key = item["item_id"]
            try:
                if session is None:
                    session = new_session()
                state, err = check(session, item)
            except Exception as e:
                state, err = None, str(e)[:200]
            if state is None:
                failed = err
                break
            prev = last.get(key)
            last[key] = state["in_stock"]
            now = time.time()
            if state["in_stock"] and prev is not True and now - pinged_at.get(key, 0) >= REPING_COOLDOWN:
                pinged_at[key] = now
                announced.add(key)
                send(item, state, "In Stock")
            elif not state["in_stock"] and key in announced:
                announced.discard(key)
                if SOLD_OUT_PINGS:
                    send(item, state, "Sold Out")
            if prev != state["in_stock"]:
                log(f"{item['name']}: {state['status']}, stock {state['qty']}, {state['seller'] or 'unknown seller'} ({state['options']})")
        if failed:
            log(f"failed: {failed} — new session")
            session = None
        time.sleep(RETRY_DELAY)


if __name__ == "__main__":
    main()
