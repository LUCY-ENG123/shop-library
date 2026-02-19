import os

REPO_ROOT = r"X:\ASAP_MAIN\ENGINEERING\CUSTOMER\GITHUB REPO\SHOP LIBRARY\shop-library"
TEMPLATE = os.path.join(REPO_ROOT, "_TEMPLATE", "index.html")

for folder in os.listdir(REPO_ROOT):
    part_dir = os.path.join(REPO_ROOT, folder)
    if not os.path.isdir(part_dir) or folder.startswith("_"):
        continue
    if not os.path.exists(os.path.join(part_dir, "index.html")):
        continue
    html = open(TEMPLATE, "r", encoding="utf-8").read()
    html = html.replace("{{PART}}", folder)
    with open(os.path.join(part_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ {folder}")

print("\nAll done!")