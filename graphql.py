import time
import os
import json
import random
import uuid
from datetime import datetime, timezone
from urllib.parse import quote

import httpcloak
import requests

WEBHOOK = ""
RETRY_DELAY = 10
WALMART_ONLY = True
CONFIRM_CHECKS = 3
MAX_CHECKS_PER_POLL = 2
RECHECK_DELAY = 60
RECHECK_OK = 300
NEW_LISTING_PINGS = True
QUEUE_ALERTS = True
QUEUE_HITS = 3
QUEUE_WINDOW = 120
QUEUE_CLEAR = 300

BASE = "https://www.walmart.ca"
OFFERS_HASH = "c6e2530e3fe0b78b46be3c528c11b89d9958f3a36d1ae5698a26a77dbd917ddd"
PROXIES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proxies.txt")
QUEUE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "queue_418.html")
PAGE_URL = f"{BASE}/en/browse/toys/trading-cards/pokemon-cards/10011_31745_6000204969672?facet=retailer_type%3AWalmart"
API_URL = "https://www.walmart.ca/orchestra/snb/graphql/Browse/10f2aaf0af572967cf3912cc27206dcef59757e05a77a2b4ff9e5d5b58d4187f/browse?variables=%7B%22id%22%3A%22%22%2C%22dealsId%22%3A%22%22%2C%22query%22%3A%22%22%2C%22nudgeContext%22%3A%22%22%2C%22page%22%3A1%2C%22prg%22%3A%22desktop%22%2C%22catId%22%3A%2210011_31745_6000204969672%22%2C%22facet%22%3A%22retailer_type%3AWalmart%22%2C%22sort%22%3A%22best_match%22%2C%22rawFacet%22%3A%22retailer_type%3AWalmart%22%2C%22seoPath%22%3A%22%22%2C%22ps%22%3A40%2C%22limit%22%3A40%2C%22ptss%22%3A%22%22%2C%22trsp%22%3A%22%22%2C%22beShelfId%22%3A%22%22%2C%22recall_set%22%3A%22%22%2C%22module_search%22%3A%22%22%2C%22min_price%22%3A%22%22%2C%22max_price%22%3A%22%22%2C%22storeSlotBooked%22%3A%22%22%2C%22additionalQueryParams%22%3A%7B%22hidden_facet%22%3Anull%2C%22translation%22%3Anull%2C%22isMoreOptionsTileEnabled%22%3Atrue%2C%22rootDimension%22%3A%22%22%2C%22altQuery%22%3A%22%22%2C%22selectedFilter%22%3A%22%22%2C%22neuralSearchSeeAll%22%3Afalse%2C%22enableGenericItemTileOptions%22%3Afalse%2C%22isLMPBrowsePage%22%3Afalse%7D%2C%22searchArgs%22%3A%7B%22query%22%3A%22%22%2C%22cat_id%22%3A%2210011_31745_6000204969672%22%2C%22prg%22%3A%22desktop%22%2C%22facet%22%3A%22retailer_type%3AWalmart%22%7D%2C%22enableCopyBlock%22%3Afalse%2C%22enableVariantCount%22%3Atrue%2C%22enableSlaBadgeV2%22%3Afalse%2C%22enableUnifiedProductFragment%22%3Afalse%2C%22enableESSCarousel%22%3Afalse%2C%22fitmentFieldParams%22%3A%7B%22powerSportEnabled%22%3Atrue%2C%22dynamicFitmentEnabled%22%3Atrue%2C%22extendedAttributesEnabled%22%3Afalse%2C%22extendedAttributesV2Enabled%22%3Afalse%2C%22fuelTypeEnabled%22%3Afalse%7D%2C%22fitmentSearchParams%22%3A%7B%22id%22%3A%22%22%2C%22dealsId%22%3A%22%22%2C%22query%22%3A%22%22%2C%22nudgeContext%22%3A%22%22%2C%22page%22%3A1%2C%22prg%22%3A%22desktop%22%2C%22catId%22%3A%2210011_31745_6000204969672%22%2C%22facet%22%3A%22retailer_type%3AWalmart%22%2C%22sort%22%3A%22best_match%22%2C%22rawFacet%22%3A%22retailer_type%3AWalmart%22%2C%22seoPath%22%3A%22%22%2C%22ps%22%3A40%2C%22limit%22%3A40%2C%22ptss%22%3A%22%22%2C%22trsp%22%3A%22%22%2C%22beShelfId%22%3A%22%22%2C%22recall_set%22%3A%22%22%2C%22module_search%22%3A%22%22%2C%22min_price%22%3A%22%22%2C%22max_price%22%3A%22%22%2C%22storeSlotBooked%22%3A%22%22%2C%22additionalQueryParams%22%3A%7B%22hidden_facet%22%3Anull%2C%22translation%22%3Anull%2C%22isMoreOptionsTileEnabled%22%3Atrue%2C%22rootDimension%22%3A%22%22%2C%22altQuery%22%3A%22%22%2C%22selectedFilter%22%3A%22%22%2C%22neuralSearchSeeAll%22%3Afalse%2C%22enableGenericItemTileOptions%22%3Afalse%2C%22isLMPBrowsePage%22%3Afalse%7D%2C%22searchArgs%22%3A%7B%22query%22%3A%22%22%2C%22cat_id%22%3A%2210011_31745_6000204969672%22%2C%22prg%22%3A%22desktop%22%2C%22facet%22%3A%22retailer_type%3AWalmart%22%7D%2C%22enableCopyBlock%22%3Afalse%2C%22enableVariantCount%22%3Afalse%2C%22enableSlaBadgeV2%22%3Afalse%2C%22enableUnifiedProductFragment%22%3Afalse%2C%22enableESSCarousel%22%3Afalse%2C%22cat_id%22%3A%2210011_31745_6000204969672%22%2C%22_be_shelf_id%22%3A%22%22%7D%2C%22searchParams%22%3A%7B%22id%22%3A%22%22%2C%22dealsId%22%3A%22%22%2C%22query%22%3A%22%22%2C%22nudgeContext%22%3A%22%22%2C%22page%22%3A1%2C%22prg%22%3A%22desktop%22%2C%22catId%22%3A%2210011_31745_6000204969672%22%2C%22facet%22%3A%22retailer_type%3AWalmart%22%2C%22sort%22%3A%22best_match%22%2C%22rawFacet%22%3A%22retailer_type%3AWalmart%22%2C%22seoPath%22%3A%22%22%2C%22ps%22%3A40%2C%22limit%22%3A40%2C%22ptss%22%3A%22%22%2C%22trsp%22%3A%22%22%2C%22beShelfId%22%3A%22%22%2C%22recall_set%22%3A%22%22%2C%22module_search%22%3A%22%22%2C%22min_price%22%3A%22%22%2C%22max_price%22%3A%22%22%2C%22storeSlotBooked%22%3A%22%22%2C%22additionalQueryParams%22%3A%7B%22hidden_facet%22%3Anull%2C%22translation%22%3Anull%2C%22isMoreOptionsTileEnabled%22%3Atrue%2C%22rootDimension%22%3A%22%22%2C%22altQuery%22%3A%22%22%2C%22selectedFilter%22%3A%22%22%2C%22neuralSearchSeeAll%22%3Afalse%2C%22enableGenericItemTileOptions%22%3Afalse%2C%22isLMPBrowsePage%22%3Afalse%7D%2C%22searchArgs%22%3A%7B%22query%22%3A%22%22%2C%22cat_id%22%3A%2210011_31745_6000204969672%22%2C%22prg%22%3A%22desktop%22%2C%22facet%22%3A%22retailer_type%3AWalmart%22%7D%2C%22enableCopyBlock%22%3Afalse%2C%22enableVariantCount%22%3Afalse%2C%22enableSlaBadgeV2%22%3Afalse%2C%22enableUnifiedProductFragment%22%3Afalse%2C%22enableESSCarousel%22%3Afalse%2C%22cat_id%22%3A%2210011_31745_6000204969672%22%2C%22_be_shelf_id%22%3A%22%22%7D%2C%22enableFashionTopNav%22%3Afalse%2C%22fetchMarquee%22%3Atrue%2C%22fetchSkyline%22%3Atrue%2C%22fetchSbaTop%22%3Atrue%2C%22fetchDataV1%22%3Afalse%2C%22fetchDataV2%22%3Afalse%2C%22fungibilityEnabled%22%3Afalse%2C%22fetchGallery%22%3Afalse%2C%22fetchDac%22%3Afalse%2C%22enablePortableFacets%22%3Atrue%2C%22tenant%22%3A%22CA_GLASS%22%2C%22pageType%22%3A%22BrowsePage%22%2C%22enableFacetCount%22%3Atrue%2C%22marketSpecificParams%22%3A%22%7B%5C%22pageType%5C%22%3A%5C%22browse%5C%22%7D%22%2C%22enableMultiSave%22%3Atrue%2C%22enableInStoreShelfMessage%22%3Afalse%2C%22fSeo%22%3Atrue%2C%22enableSellerType%22%3Atrue%2C%22enableItemRank%22%3Atrue%2C%22enableOptimisticWeightUpdate%22%3Afalse%2C%22enableFulfillmentTagsEnhacements%22%3Afalse%2C%22enableRxDrugScheduleModal%22%3Atrue%2C%22enablePromoData%22%3Afalse%2C%22enableAdsPromoData%22%3Atrue%2C%22enableSeoLangUrl%22%3Atrue%2C%22enableImageBannerCarousel%22%3Afalse%2C%22enableHero4%22%3Atrue%2C%22enableSeoBrowseMetaDataShortDesc%22%3Atrue%2C%22enableCanAddToList%22%3Afalse%2C%22enablePromotionMessages%22%3Afalse%2C%22enableDebugAnalyticsTags%22%3Afalse%2C%22enableSignInToSeePrice%22%3Afalse%2C%22enableSimpleEmailSignUp%22%3Afalse%2C%22enableModuleReposition%22%3Afalse%2C%22enableUnifiedSchema%22%3Afalse%2C%22version%22%3A%22v1%22%2C%22postProcessingVersion%22%3A1%2C%22enableAdsUnifiedProductTile%22%3Afalse%7D"
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


def api_headers():
    cid = uuid.uuid4().hex[:32]
    return {
        "accept": "application/json",
        "accept-language": "en-CA",
        "content-type": "application/json",
        "downlink": "10",
        "dpr": "1",
        "priority": "u=1, i",
        "referer": PAGE_URL,
        "sec-ch-ua": SEC_CH_UA,
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "tenant-id": "qxjed8",
        "user-agent": UA,
        "wm_mp": "true",
        "wm_page_url": PAGE_URL,
        "wm_qos.correlation_id": cid,
        "x-apollo-operation-name": "Browse",
        "x-enable-server-timing": "1",
        "x-latency-trace": "1",
        "x-o-bu": "WALMART-CA",
        "x-o-ccm": "server",
        "x-o-correlation-id": cid,
        "x-o-gql-query": "query Browse",
        "x-o-mart": "B2C",
        "x-o-platform": "rweb",
        "x-o-platform-version": "caweb-1.176.0-0c9742e30918adcbaf5d8d579c39db2216f7a38d-9150011r",
        "x-o-segment": "oaoh",
    }


def new_session():
    proxy = pick_proxy()
    session = httpcloak.Session(preset="chrome-latest-windows", timeout=30, proxy=proxy)
    r = session.get(PAGE_URL, headers=NAV_HEADERS)
    if r.status_code != 200:
        if r.status_code == 418:
            save_418(r.text)
        raise RuntimeError(f"warm-up page HTTP {r.status_code} on {proxy_label(proxy)}")
    log(f"session warmed on {proxy_label(proxy)}")
    return session


def parse_item(x):
    price = x.get("priceInfo") or {}
    stock = (x.get("availabilityStatusV2") or {}).get("value") or ""
    seller_type = x.get("sellerType") or ""
    return {
        "id": x.get("usItemId") or x.get("id") or "",
        "name": (x.get("name") or "").strip(),
        "url": BASE + (x.get("canonicalUrl") or "").split("?")[0],
        "price": price.get("linePrice") or (price.get("currentPrice") or {}).get("priceString") or "Unknown",
        "stock": stock,
        "seller": (x.get("sellerName") or "").strip(),
        "image": (x.get("imageInfo") or {}).get("thumbnailUrl") or "",
        "offer_id": x.get("offerId") or "",
        "cart_limit": x.get("orderLimit"),
        "available": stock == "IN_STOCK",
        "walmart_listed": seller_type == "INTERNAL",
    }


def fetch(session):
    r = session.get(API_URL, headers=api_headers())
    if r.status_code != 200:
        if r.status_code == 418:
            save_418(r.text)
        return None, f"HTTP {r.status_code}"
    try:
        body = r.json()
    except ValueError:
        return None, "non-JSON response (blocked?)"
    result = ((body.get("data") or {}).get("search") or {}).get("searchResult") or {}
    stacks = result.get("itemStacks")
    if stacks is None:
        return None, "no searchResult in response: " + str(body.get("errors") or "")[:120]
    items = [x for stack in stacks for x in stack.get("itemsV2") or stack.get("items") or []]
    return [parse_item(x) for x in items if x.get("__typename") == "Product"], ""


def walmart_offer(session, item):
    variables = {"itemId": item["id"], "isSubscriptionEligible": False, "fSId": False, "enableMultiSave": False}
    url = f"{BASE}/orchestra/pdp/graphql/GetAllSellerOffers/{OFFERS_HASH}?variables=" + quote(json.dumps(variables, separators=(",", ":")))
    cid = uuid.uuid4().hex[:32]
    referer = f"{BASE}/en/ip/{item['id']}"
    headers = {
        "accept": "application/json",
        "accept-language": "en-CA",
        "content-type": "application/json",
        "downlink": "10",
        "dpr": "1",
        "priority": "u=1, i",
        "referer": referer,
        "sec-ch-ua": '"Chromium";v="152", "Not?A_Brand";v="24", "Google Chrome";v="152"',
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
        "x-apollo-operation-name": "GetAllSellerOffers",
        "x-enable-server-timing": "1",
        "x-latency-trace": "1",
        "x-o-bu": "WALMART-CA",
        "x-o-ccm": "server",
        "x-o-correlation-id": cid,
        "x-o-gql-query": "query GetAllSellerOffers",
        "x-o-mart": "B2C",
        "x-o-platform": "rweb",
        "x-o-platform-version": "caweb-1.176.0-0c9742e30918adcbaf5d8d579c39db2216f7a38d-9150011r",
        "x-o-segment": "oaoh",
    }
    r = session.get(url, headers=headers)
    if r.status_code != 200:
        return None, f"stock check HTTP {r.status_code}"
    offers = []
    stack = [r.json()]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            if node.get("offerId") and ("sellerName" in node or "sellerDisplayName" in node):
                offers.append(node)
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
    if not offers:
        return None, "stock check returned no offers"
    for offer in offers:
        seller = (offer.get("sellerDisplayName") or offer.get("sellerName") or "").strip()
        if seller.lower() != "walmart":
            continue
        options = [o for o in offer.get("fulfillmentOptions") or [] if isinstance(o, dict)]
        qty = max((o.get("availableQuantity") or 0 for o in options), default=0)
        limit = next((o.get("orderLimit") or o.get("maxOrderQuantity") for o in options if o.get("orderLimit") or o.get("maxOrderQuantity")), None)
        price = ((offer.get("priceInfo") or {}).get("currentPrice") or {}).get("priceString")
        return {"qty": qty, "limit": limit, "price": price, "offer_id": offer.get("offerId")}, ""
    return {"qty": 0, "limit": None, "price": None, "offer_id": None}, f"no Walmart offer ({len(offers)} resellers)"


def save_418(text):
    try:
        with open(QUEUE_FILE, "w", encoding="utf-8") as f:
            f.write(text or "")
    except OSError:
        pass


def send_status(title, description, color):
    log(f"{title}: {description}")
    if not WEBHOOK:
        return
    embed = {
        "title": title,
        "description": description,
        "url": PAGE_URL,
        "color": color,
        "footer": {"text": "Walmart CA · queue"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    try:
        requests.post(WEBHOOK, json={"embeds": [embed]}, timeout=10)
    except Exception as e:
        log(f"webhook failed: {e}")


def queue_event(queue, hit):
    if not QUEUE_ALERTS:
        return
    now = time.time()
    if hit:
        queue["hits"] = [t for t in queue["hits"] if now - t < QUEUE_WINDOW] + [now]
        queue["last_hit"] = now
        if not queue["up"] and len(queue["hits"]) >= QUEUE_HITS:
            queue["up"] = True
            queue["since"] = now
            send_status("Walmart CA queue is up", f"{len(queue['hits'])} HTTP 418 responses in the last {QUEUE_WINDOW // 60} min — drop protection is active, something may be dropping.", 0xF5A623)
    elif queue["up"] and now - queue["last_hit"] > QUEUE_CLEAR:
        queue["up"] = False
        queue["hits"] = []
        send_status("Walmart CA queue is down", f"No HTTP 418 for {QUEUE_CLEAR // 60} min. Queue lasted about {round((queue['last_hit'] - queue['since']) / 60)} min.", 0x2ECC71)


def send(item, kind):
    if not WEBHOOK:
        log(f"(no WEBHOOK set) would ping {kind}: {item['name']}")
        return
    embed = {
        "title": item["name"][:256],
        "url": item["url"],
        "color": 0x0071CE,
        "fields": [
            {"name": "Type", "value": kind, "inline": True},
            {"name": "Price", "value": item["price"], "inline": True},
            {"name": "Stock", "value": item["stock"] or "Unknown", "inline": True},
            {"name": "Seller", "value": item["seller"] or "Unknown", "inline": True},
            {"name": "Item ID", "value": item["id"] or "Unknown", "inline": True},
            {"name": "Offer ID", "value": item["offer_id"] or "Unknown", "inline": True},
        ] + ([{"name": "Cart Limit", "value": str(item["cart_limit"]), "inline": True}] if item["cart_limit"] else []),
        "thumbnail": {"url": item["image"]} if item["image"] else None,
        "footer": {"text": "Walmart CA · graphql"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    try:
        requests.post(WEBHOOK, json={"embeds": [{k: v for k, v in embed.items() if v is not None}]}, timeout=10)
    except Exception as e:
        log(f"webhook failed: {e}")


def main():
    seen = {}
    misses = {}
    next_check = {}
    baseline = set()
    announced = set()
    queue = {"hits": [], "up": False, "last_hit": 0, "since": 0}
    first = True
    session = None
    while True:
        try:
            if session is None:
                session = new_session()
            items, err = fetch(session)
        except Exception as e:
            items, err = None, str(e)[:200]
        if items is None:
            log(f"failed: {err} — new session")
            if "418" in err:
                queue_event(queue, True)
            session = None
            time.sleep(RETRY_DELAY)
            continue
        queue_event(queue, False)
        pinged = 0
        checks = 0
        now = time.time()
        candidates = []
        for item in items:
            key = item["id"]
            prev = seen.get(key)
            if first:
                baseline.add(key)
            fresh = prev is None and key not in baseline
            if fresh and key not in announced and NEW_LISTING_PINGS and item["walmart_listed"] and (WALMART_ONLY or not item["available"]):
                announced.add(key)
                send(item, "New Listing")
                pinged += 1
            if not item["available"]:
                misses[key] = misses.get(key, 0) + 1
                if prev is None or misses[key] >= CONFIRM_CHECKS:
                    seen[key] = False
                    next_check.pop(key, None)
                continue
            misses.pop(key, None)
            if not WALMART_ONLY:
                seen[key] = True
                if prev is not True and key not in baseline:
                    send(item, "New" if prev is None else "Restock")
                    pinged += 1
                continue
            urgent = key not in next_check and not (prev is None and key in baseline)
            candidates.append((0 if urgent else 1, item))
        candidates.sort(key=lambda c: c[0])
        for priority, item in candidates:
            key = item["id"]
            prev = seen.get(key)
            if now < next_check.get(key, 0):
                continue
            if priority and checks >= MAX_CHECKS_PER_POLL:
                continue
            if priority:
                checks += 1
            try:
                offer, why = walmart_offer(session, item)
            except Exception as e:
                offer, why = None, str(e)[:120]
            if offer is None:
                next_check[key] = now + RECHECK_DELAY
                if prev is not True and key not in baseline and key not in announced and item["walmart_listed"]:
                    seen[key] = True
                    log(f"{why} for {item['name'][:50]} — pinging without stock")
                    send(item, "New" if prev is None else "Restock")
                    pinged += 1
                continue
            if not offer["qty"]:
                if prev is not False:
                    log(f"no Walmart stock for {item['name'][:50]}: {why or 'Walmart offer has 0 stock'}")
                seen[key] = False
                next_check[key] = now + RECHECK_DELAY
                continue
            next_check[key] = now + RECHECK_OK
            item["stock"] = str(offer["qty"])
            item["seller"] = "Walmart"
            item["cart_limit"] = offer["limit"] or item.get("cart_limit")
            item["price"] = offer["price"] or item["price"]
            item["offer_id"] = offer["offer_id"] or item.get("offer_id", "")
            seen[key] = True
            if prev is True or (prev is None and key in baseline):
                continue
            send(item, "New" if prev is None else "Restock")
            pinged += 1
        confirmed = sum(1 for i in items if seen.get(i["id"]) is True)
        log(f"{len(items)} products, {confirmed} with {'Walmart ' if WALMART_ONLY else ''}stock, {pinged} pinged")
        first = False
        time.sleep(RETRY_DELAY)


if __name__ == "__main__":
    main()
