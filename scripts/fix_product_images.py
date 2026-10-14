#!/usr/bin/env python3
"""Fix Hro Market product imagery without touching prices, UI or checkout."""
from pathlib import Path
import csv
import html
import io
import json
import os
import re
import time
import urllib.request

ROOT = Path(".")
BUNDLE = ROOT / "bundle.js"
ASSETS = ROOT / "product-images"
ASSETS.mkdir(exist_ok=True)

# Reviewed Unsplash photographs (free under Unsplash License); CC0 lavash from Commons.
PHOTOS = {
    "green-apple": ("1719024651951-614f7c51bc7e", "https://unsplash.com/photos/a-pile-of-green-apples-sitting-next-to-each-other-cNRD2Cdqnfo"),
    "peach": ("1503790267910-b4e2b1e34e3f", "https://unsplash.com/photos/peach-fruits-OmQ8NkHW5B4"),
    "eggplant": ("1683543122945-513029986574", "https://unsplash.com/photos/a-pile-of-purple-eggplant-with-green-stems-d6I1ZNZJcNo"),
    "cabbage": ("1772881382620-04ee08835ef9", "https://unsplash.com/photos/close-up-of-a-fresh-green-cabbage-with-large-leaves-0tGRa2pq4ac"),
    "dill": ("1779173932688-2bc0e3ecb95e", "https://unsplash.com/photos/a-pile-of-fresh-green-herbs-including-parsley-and-dill-Zz2prRbsgsk"),
    "parsley": ("1758055660473-a61e426ade6e", "https://unsplash.com/photos/fresh-green-parsley-bunches-piled-high-UzaIeuLilnM"),
    "sugar": ("1769259397222-33e425659c43", "https://unsplash.com/photos/a-glass-jar-filled-with-white-granular-sugar-AQv1UhsnkqE"),
    "salt": ("1646722670581-974d084e0ec0", "https://unsplash.com/photos/a-salt-shaker-sitting-on-top-of-a-table-i3wFM-9MvAs"),
    "flour": ("1738667763800-2c212591684b", "https://unsplash.com/photos/a-bowl-of-flour-sitting-on-a-counter-ZfRsumYbvDM"),
    "redbull": ("1613208602577-50fd21015cca", "https://unsplash.com/photos/red-bull-energy-drink-can-UIwnggHrTnI"),
    "sprite": ("1628210473497-92b600c4007b", "https://unsplash.com/photos/sprite-plastic-bottle-beside-orange-soda-can-8ijrazWfchQ"),
}
COMMONS_PHOTOS = {
    "coke-zero": ("https://commons.wikimedia.org/wiki/Special:FilePath/CocaColaZero.jpg?width=800", "https://commons.wikimedia.org/wiki/File:CocaColaZero.jpg", "Public domain"),
    "kitkat": ("https://commons.wikimedia.org/wiki/Special:FilePath/KitKat%2C_wafer_chocolate.jpg?width=800", "https://commons.wikimedia.org/wiki/File:KitKat,_wafer_chocolate.jpg", "CC0 1.0"),
    "lavash": ("https://commons.wikimedia.org/wiki/Special:FilePath/Lavash_arm%C3%A9nien.jpg?width=800", "https://commons.wikimedia.org/wiki/File:Lavash_arm%C3%A9nien.jpg", "CC0 1.0"),
}

# Correct a few obvious cross-product mismatches using images that are already locally hosted.
REUSE = {
    "coke": "assets/photo-1554866585-cd94860890b7.jpg",     # Coca-Cola can, not Pepsi
    "pepsi": "assets/photo-1629203851122-3726ecdf080e.jpg", # Pepsi can, not Coca-Cola
    "chanakh": "assets/photo-1628088062854-d1870b4553da.jpg",  # white cheese, not blue cheese
    "matzoon": "assets/photo-1571212515416-fef01fc43637.jpg",  # plain cultured dairy, not strawberry dessert
    "noyan": "assets/photo-1600271886742-f049cd451bba.jpg", # fruit juice rather than unrelated category
}
# A brand's exact packshot isn't verified. Use an accurate, clearly labelled illustration
# instead of falsely depicting another brand, model, or product.
ILLUSTRATE = {
    "oil", "basturma",
    "grand-milk", "grand-dark", "grand-pistachio", "krispy",
    "wafer", "rolls", "rollo", "truffle", "parvana", "golden",
    "rahat", "kolos", "snickers", "bounty", "mars", "kitkat", "kinder",
    "coke-zero", "jermuk", "noy", "sandora", "rauch",
    "ariel-small", "ariel-large", "fairy", "domestos",
    "paper-towel", "sponge", "trash-bags",
}

COLOR = {
    "produce": ("#edfbe9", "#d2f3cf", "#237442"),
    "dairy": ("#eaf8ff", "#cce9fa", "#176188"),
    "sweets": ("#faf0ff", "#ebd7fa", "#75379c"),
    "drinks": ("#fff5e5", "#ffe0b5", "#a9541e"),
    "home": ("#edf9ff", "#d4ecf5", "#176f80"),
}
EMOJI_OVERRIDE = {
    "oil":"🫙", "basturma":"🥩", "grand-pistachio":"🍫",
    "krispy":"🍫", "wafer":"🧇", "rolls":"🧇", "rollo":"🍬",
    "truffle":"🍫", "parvana":"🍫", "golden":"🍫",
    "rahat":"🍬", "kolos":"🍪", "coke-zero":"🥤",
    "jermuk":"💧", "noy":"💧", "sandora":"🧃",
    "rauch":"🧃", "ariel-small":"🧺", "ariel-large":"🧺",
    "fairy":"🧽", "domestos":"🧴",
    "paper-towel":"🧻", "sponge":"🧽", "trash-bags":"🗑️",
}

def wrapped(text, max_len=22):
    words = text.split()
    lines, line = [], ""
    for word in words:
        if line and len(line) + len(word) + 1 > max_len:
            lines.append(line)
            line = word
        else:
            line = (line + " " + word).strip()
    if line:
        lines.append(line)
    return lines[:3]

def make_illustration(pid, name, category, emoji):
    a, b, accent = COLOR[category]
    emoji = EMOJI_OVERRIDE.get(pid, emoji)
    lines = wrapped(name)
    tspans = "\n".join(
        '<tspan x="320" dy="%d">%s</tspan>' % (0 if i == 0 else 36, html.escape(line))
        for i, line in enumerate(lines)
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="640" height="480" viewBox="0 0 640 480">
<defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>
<filter id="sh"><feDropShadow dx="0" dy="7" stdDeviation="12" flood-opacity=".10"/></filter></defs>
<rect width="640" height="480" fill="url(#bg)"/>
<circle cx="320" cy="176" r="125" fill="#fff" opacity=".84" filter="url(#sh)"/>
<circle cx="320" cy="176" r="102" fill="none" stroke="{accent}" opacity=".16" stroke-width="2"/>
<text x="320" y="221" font-size="118" text-anchor="middle" font-family="Apple Color Emoji, Segoe UI Emoji, Noto Color Emoji, sans-serif">{html.escape(emoji)}</text>
<text x="320" y="328" font-size="27" font-weight="700" fill="{accent}" text-anchor="middle" font-family="Arial,DejaVu Sans,sans-serif">{tspans}</text>
<text x="320" y="453" font-size="17" text-anchor="middle" fill="{accent}" opacity=".7" font-family="Arial,DejaVu Sans,sans-serif">Նկարազարդում · Hro Market</text>
</svg>'''
    dest = ASSETS / (pid + ".svg")
    dest.write_text(svg, encoding="utf-8")
    return dest.as_posix()

def download(url, dest):
    if dest.is_file() and dest.stat().st_size > 4000:
        return True
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 Hro Market Catalog", "Accept": "image/jpeg,image/*"})
            with urllib.request.urlopen(req, timeout=28) as response:
                data = response.read(7_000_000)
            if len(data) < 4000 or not (data.startswith(b"\xff\xd8\xff") or data.startswith(b"\x89PNG")):
                raise ValueError("response is not a valid image")
            dest.write_bytes(data)
            return True
        except Exception as exc:
            print("Image retry", dest.name, attempt + 1, str(exc)[:120], flush=True)
            time.sleep(1 + attempt)
    return False

text = BUNDLE.read_text(encoding="utf-8")
match = re.search(r"const productImages = \{\n.*?\n\};", text, flags=re.S)
if not match:
    raise RuntimeError("Unexpected bundle.js format: product image table not found")
image_pairs = re.findall(r'\s*(?:"([^"]+)"|([a-z][a-z0-9-]*)):\s*"([^"]+)"', match.group(0))
old = {a or b: c for a, b, c in image_pairs}
pstart = text.index("const products = [")
pend = text.index("];", pstart)
items = re.findall(r'p\("([^"]+)", "([^"]+)", "([^"]+)", [^,]+, "([^"]+)"\)', text[pstart:pend])
if len(items) < 80 or len({i[0] for i in items}) != len(items):
    raise RuntimeError("Product list changed unexpectedly; stopping to avoid corruption")
newmap = {}
credits = []
audit = []
for pid, name, category, emoji in items:
    origin = ""
    if pid in PHOTOS or pid in COMMONS_PHOTOS:
        if pid in PHOTOS:
            photo_id, origin = PHOTOS[pid]
            url = "https://images.unsplash.com/photo-" + photo_id + "?fit=crop&w=800&q=82&fm=jpg"
            license_name = "Unsplash License"
        else:
            url, origin, license_name = COMMONS_PHOTOS[pid]
        dest = ASSETS / (pid + ".jpg")
        if download(url, dest):
            chosen = dest.as_posix()
            kind = "licensed photo"
            credits.append((pid, origin, license_name))
        else:
            chosen = make_illustration(pid, name, category, emoji)
            kind = "illustration (photo unavailable)"
    elif pid in REUSE:
        chosen = REUSE[pid]
        kind = "existing relevant photo"
    elif pid in ILLUSTRATE or pid not in old or old[pid].startswith("https://") or not Path(old[pid]).is_file():
        chosen = make_illustration(pid, name, category, emoji)
        kind = "labelled illustration"
    else:
        chosen = old[pid]
        kind = "existing relevant photo"
    if not Path(chosen).is_file():
        raise RuntimeError("Missing image for " + pid + ": " + chosen)
    newmap[pid] = chosen
    audit.append((pid, name, kind, chosen, origin))

replacement = "const productImages = {\n" + ",\n".join(
    "  " + json.dumps(pid, ensure_ascii=False) + ": " + json.dumps(newmap[pid], ensure_ascii=False)
    for pid, *_ in items
) + "\n};"
new_text = text[:match.start()] + replacement + text[match.end():]
BUNDLE.write_text(new_text, encoding="utf-8")
with (ROOT / "PRODUCT_IMAGE_AUDIT.csv").open("w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["product_id", "product_name", "image_type", "local_path", "source"])
    writer.writerows(audit)
credits_text = [
    "# Hro Market — Product image sources",
    "",
    "All external Unsplash photographs are published under the Unsplash License.",
    "The Wikimedia Commons Armenian lavash photograph is CC0 1.0.",
    "Brand-name illustrations are generic representations, **not official product packaging**.",
    "Exact package photos should be replaced with verified images supplied by the store or authorized suppliers.",
    "",
    "| Product | Source | License |",
    "| --- | --- | --- |",
]
credits_text.extend(f"| {pid} | {source} | {lic} |" for pid, source, lic in credits)
(ROOT / "PRODUCT_IMAGE_SOURCES.md").write_text("\n".join(credits_text) + "\n", encoding="utf-8")
print("Updated", len(items), "products; licensed photos", len(credits),
      "illustrations", sum("illustration" in row[2] for row in audit),
      "existing photos", sum("existing" in row[2] for row in audit))
