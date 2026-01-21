import os
import qrcode
from urllib.parse import quote

BASE_URL = "https://lucy-eng123.github.io/shop-library/"

HERE = os.path.dirname(os.path.abspath(__file__))

count = 0

for name in os.listdir(HERE):
    full = os.path.join(HERE, name)

    if not os.path.isdir(full):
        continue

    if name.startswith("_"):
        continue

    url = BASE_URL + quote(name) + "/"
    out_path = os.path.join(full, f"QR_{name}.png")

    img = qrcode.make(url)
    img.save(out_path)

    print(f"Made: {out_path} -> {url}")
    count += 1

print(f"\nDone. Generated {count} QR codes.")
