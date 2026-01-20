import os
import re
import qrcode
from urllib.parse import quote

# CHANGE THIS ONCE (your GitHub Pages base)
BASE_URL = "https://lucy-eng123.github.io/shop-library/"

# Allow spaces in folder names:
# PN-1047
# PN-TRUCK STEP 2 PIECE SHAFT COLLAR
if os.path.isdir(full) and not name.startswith("_"):


HERE = os.path.dirname(os.path.abspath(__file__))

count = 0

for name in os.listdir(HERE):
    full = os.path.join(HERE, name)
    if os.path.isdir(full) and PN_FOLDER_RE.match(name):
        url = BASE_URL + quote(name) + "/"
        out_path = os.path.join(full, f"QR_{name}.png")

        img = qrcode.make(url)
        img.save(out_path)

        print(f"Made: {out_path} -> {url}")
        count += 1

print(f"\nDone. Generated {count} QR codes.")
