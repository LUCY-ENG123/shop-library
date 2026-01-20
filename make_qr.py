import os
import re
import qrcode

# ✅ CHANGE THIS ONCE (your GitHub Pages base)
BASE_URL = "https://lucy-eng123.github.io/shop-library/"

# Looks for folders like PN-1047, PN-TEST, PN-2048, etc.
PN_FOLDER_RE = re.compile(r"^PN-[A-Za-z0-9_-]+$")

HERE = os.path.dirname(os.path.abspath(__file__))

count = 0

for name in os.listdir(HERE):
    full = os.path.join(HERE, name)
    if os.path.isdir(full) and PN_FOLDER_RE.match(name):
        url = BASE_URL + name + "/"
        out_path = os.path.join(full, f"QR_{name}.png")

        img = qrcode.make(url)
        img.save(out_path)

        print(f"Made: {out_path}  ->  {url}")
        count += 1

print(f"\nDone. Generated {count} QR codes.")
