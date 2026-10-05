"""Descarga nombres y precios de Star Wars: Unlimited desde tcgcsv.com (espejo diario de TCGplayer)
y genera site/data/cards.json para la app.

Formato de salida:
{
  "updated": "2026-10-05T20:01:51Z",       # cuándo tcgcsv publicó los precios
  "generated": "...",                       # cuándo corrió este script
  "sets": [[groupId, nombre, abreviatura, fechaPublicación], ...]   (más nuevo primero)
  "cards": [[nombre, groupId, número, rareza, productId, precioNormal, precioFoil], ...]
}
"""
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

CATEGORY = 79  # Star Wars: Unlimited en TCGplayer
BASE = "https://tcgcsv.com/tcgplayer"
UA = "swu-trade-machine/1.0 (+https://github.com)"
OUT = os.path.join(os.path.dirname(__file__), "..", "site", "data", "cards.json")


def get(url):
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                body = json.loads(r.read().decode("utf-8"))
                return body, r.headers.get("Last-Modified")
        except Exception as e:  # noqa: BLE001
            if attempt == 3:
                raise
            print(f"retry {url}: {e}", file=sys.stderr)
            time.sleep(2 + attempt * 3)


def money(x):
    return None if x is None else round(float(x), 2)


def main():
    groups, _ = get(f"{BASE}/{CATEGORY}/groups")
    groups = groups["results"]
    sets, cards, newest = [], [], None

    for g in groups:
        gid = g["groupId"]
        products, _ = get(f"{BASE}/{CATEGORY}/{gid}/products")
        prices, lm = get(f"{BASE}/{CATEGORY}/{gid}/prices")
        time.sleep(0.25)
        if lm:
            try:
                d = parsedate_to_datetime(lm)
                newest = d if newest is None or d > newest else newest
            except Exception:  # noqa: BLE001
                pass

        info = {}
        for p in products["results"]:
            ext = {e["name"]: e["value"] for e in (p.get("extendedData") or [])}
            if not ext.get("Number"):  # sin número = sellado (sobres, cajas, mazos)
                continue
            info[p["productId"]] = {
                "name": " ".join(p["name"].split()),
                "num": str(ext.get("Number", "")).split("/")[0].strip(),
                "rar": (ext.get("Rarity") or "?")[:1],
            }

        merged = {}
        for q in prices["results"]:
            pid = q["productId"]
            if pid not in info:
                continue
            price = q.get("marketPrice")
            if price is None:
                price = q.get("midPrice")
            if price is None:
                continue
            m = merged.setdefault(pid, {"N": None, "F": None})
            if q.get("subTypeName") == "Foil":
                m["F"] = money(price)
            else:
                m["N"] = money(price)

        for pid, m in merged.items():
            i = info[pid]
            cards.append([i["name"], gid, i["num"], i["rar"], pid, m["N"], m["F"]])

        if merged:
            sets.append([gid, g["name"], g.get("abbreviation") or "", (g.get("publishedOn") or "")[:10]])
        print(f"{g['name']}: {len(merged)} cartas")

    sets.sort(key=lambda s: s[3], reverse=True)
    out = {
        "updated": (newest or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sets": sets,
        "cards": cards,
    }
    if len(cards) < int(os.environ.get("MIN_CARDS", "500")):
        sys.exit(f"Solo {len(cards)} cartas: algo falló, no se publica.")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print(f"OK: {len(cards)} cartas en {len(sets)} expansiones → {OUT}")


if __name__ == "__main__":
    main()
