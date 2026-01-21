import os
import re
import io
import sys
import time
import shutil
import webbrowser
from urllib.parse import quote

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

# ============================
# EDIT THESE ONCE
# ============================
BASE_URL = "https://lucy-eng123.github.io/shop-library/"
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))  # this script lives in shop-library
TEMPLATE_DIR = "_TEMPLATE"
TEMPLATE_FILE = "index.html"

# QR placement (tweak once)
QR_SIZE_INCHES = 1.25
TITLEBLOCK_LEFT_X = 11.75 * inch
TITLEBLOCK_BOTTOM_Y = 0.40 * inch
GAP = 0.10 * inch

AUTODESK_UPLOAD_URL = "https://viewer.autodesk.com/"

import subprocess

def run_git(repo_dir, args):
    return subprocess.check_output(["git"] + args, cwd=repo_dir, text=True, stderr=subprocess.STDOUT).strip()

def has_uncommitted_changes(repo_dir):
    # returns True if working tree not clean
    out = run_git(repo_dir, ["status", "--porcelain"])
    return bool(out)

def has_unpushed_commits(repo_dir):
    # fetch to update remote info
    subprocess.call(["git", "fetch"], cwd=repo_dir)
    # check if HEAD is ahead of upstream
    try:
        out = run_git(repo_dir, ["status", "-sb"])
        # Example: "## main...origin/main [ahead 1]"
        return "[ahead" in out
    except Exception:
        return False

def prompt_push(repo_dir):
    ans = input("Unpushed commits detected. Push to GitHub now? (y/n): ").strip().lower()
    if ans == "y":
        subprocess.check_call(["git", "push"], cwd=repo_dir)
        print("✅ Pushed to GitHub.")
    else:
        print("OK — not pushing yet.")
def open_github_desktop_if_needed():
    try:
        needs_attention = (
            has_uncommitted_changes(REPO_ROOT)
            or has_unpushed_commits(REPO_ROOT)
        )

        if not needs_attention:
            return

        tasklist = subprocess.check_output("tasklist", shell=True, text=True)
        if "GitHubDesktop.exe" in tasklist:
            print("GitHub Desktop already running.")
            return

        possible_paths = [
            rf"C:\Users\{os.getlogin()}\AppData\Local\GitHubDesktop\GitHubDesktop.exe",
            r"C:\Program Files\GitHub Desktop\GitHubDesktop.exe",
            r"C:\Program Files (x86)\GitHub Desktop\GitHubDesktop.exe",
        ]

        for path in possible_paths:
            if os.path.exists(path):
                subprocess.Popen([path])
                print("Opened GitHub Desktop.")
                return

        print("⚠ GitHub Desktop not found. Open it manually.")

    except Exception as e:
        print("⚠ Could not open GitHub Desktop:", e)


# ============================
# Helpers
# ============================
def find_publish_dir(start_dir: str) -> str:
    """
    Prefer a 'QR' subfolder if it exists and contains a PDF.
    Otherwise publish from start_dir.
    """
    qr_dir = os.path.join(start_dir, "QR")
    if os.path.isdir(qr_dir):
        for f in os.listdir(qr_dir):
            if f.lower().endswith(".pdf"):
                return qr_dir
    return start_dir

def newest_file(folder: str, is_ok) -> str | None:
    candidates = []
    for name in os.listdir(folder):
        full = os.path.join(folder, name)
        if os.path.isfile(full) and is_ok(name):
            candidates.append((os.path.getmtime(full), full))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]

def pick_pdf(src_dir: str) -> str | None:
    return newest_file(
        src_dir,
        lambda f: f.lower().endswith(".pdf") and not f.lower().endswith("_qr.pdf"),
    )

def pick_step(src_dir: str) -> str | None:
    return newest_file(
        src_dir,
        lambda f: f.lower().endswith(".step") or f.lower().endswith(".stp"),
    )

def part_name_from_pdf(pdf_path: str) -> str:
    # Use the PDF filename as the part number (recommended for ASAP/QR folders)
    return os.path.splitext(os.path.basename(pdf_path))[0]

def ensure_qr_png(dst_dir: str, part_name: str) -> str:
    qr_path = os.path.join(dst_dir, f"QR_{part_name}.png")
    if os.path.exists(qr_path):
        return qr_path

    import qrcode
    url = BASE_URL.rstrip("/") + "/" + quote(part_name) + "/"
    img = qrcode.make(url)
    img.save(qr_path)
    print(f"Made QR: {os.path.basename(qr_path)} -> {url}")
    return qr_path

def stamp_pdf_overwrite(pdf_in: str, qr_png: str, dst_dir: str, part_name: str) -> str:
    out_pdf = os.path.join(dst_dir, f"{part_name}.pdf")

    reader = PdfReader(pdf_in)
    writer = PdfWriter()

    first_page = reader.pages[0]
    width = float(first_page.mediabox.width)
    height = float(first_page.mediabox.height)

    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(width, height))

    qr_size = QR_SIZE_INCHES * inch
    x = TITLEBLOCK_LEFT_X - qr_size - GAP
    y = TITLEBLOCK_BOTTOM_Y

    c.drawImage(qr_png, x, y, qr_size, qr_size, mask="auto")
    c.save()

    packet.seek(0)
    overlay = PdfReader(packet)

    first_page.merge_page(overlay.pages[0])
    writer.add_page(first_page)
    for page in reader.pages[1:]:
        writer.add_page(page)

    with open(out_pdf, "wb") as f:
        writer.write(f)

    print(f"Stamped & saved: {os.path.basename(out_pdf)}")
    return out_pdf

def load_autodesk_link(dst_dir: str) -> str | None:
    p = os.path.join(dst_dir, "autodesk.txt")
    if not os.path.exists(p):
        return None
    link = open(p, "r", encoding="utf-8").read().strip()
    return link or None

def save_autodesk_link(dst_dir: str, link: str):
    p = os.path.join(dst_dir, "autodesk.txt")
    with open(p, "w", encoding="utf-8") as f:
        f.write(link.strip() + "\n")
    print("Saved autodesk.txt")

def try_get_clipboard_autodesk_link() -> str | None:
    try:
        import pyperclip
        text = (pyperclip.paste() or "").strip()
        if text.startswith("https://autode.sk/") or text.startswith("http://autode.sk/"):
            return text
        return None
    except Exception:
        return None

def update_index_html(dst_dir: str, part_name: str, autodesk_link: str | None, cache_bust: int):
    template_path = os.path.join(REPO_ROOT, TEMPLATE_DIR, TEMPLATE_FILE)
    if not os.path.exists(template_path):
        raise RuntimeError(f"Template not found: {template_path}")

    html = open(template_path, "r", encoding="utf-8").read()

    html = re.sub(r"<title>.*?</title>", f"<title>{part_name}</title>", html, flags=re.I | re.S)
    html = re.sub(r"<h1>.*?</h1>", f"<h1>{part_name}</h1>", html, flags=re.I | re.S)

    # Update the FIRST pdf href we find in the template
    pdf_href = f'{part_name}.pdf?v={cache_bust}'
    html = re.sub(r'href="[^"]+\.pdf[^"]*"', f'href="{pdf_href}"', html, count=1)

    # Update the FIRST autode.sk href we find in the template
    if autodesk_link:
        html = re.sub(r'href="https://autode\.sk/[^"]+"', f'href="{autodesk_link}"', html, count=1)

    out_path = os.path.join(dst_dir, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print("Updated index.html")

# ============================
# Main
# ============================
def main():
    # Run from any folder OR pass in a folder path
    start_dir = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.getcwd()
    src_dir = find_publish_dir(start_dir)

    pdf_src = pick_pdf(src_dir)
    if not pdf_src:
        raise RuntimeError(f"⛔ No PDF found in: {src_dir}")

    # IMPORTANT: part name comes from PDF file name (works great with ASAP/QR folders)
    part_name = part_name_from_pdf(pdf_src)

    dst_dir = os.path.join(REPO_ROOT, part_name)
    os.makedirs(dst_dir, exist_ok=True)

    print(f"\nSTART  : {start_dir}")
    print(f"SOURCE : {src_dir}")
    print(f"TARGET : {dst_dir}")
    print(f"PART   : {part_name}")

    step_src = pick_step(src_dir)

    # Copy PDF into repo folder (stable name)
    pdf_dst = os.path.join(dst_dir, f"{part_name}.pdf")
    shutil.copy2(pdf_src, pdf_dst)
    print(f"Copied PDF  -> {os.path.basename(pdf_dst)}")

    # Copy STEP if found (stable name)
    if step_src:
        ext = os.path.splitext(step_src)[1].lower()
        step_dst = os.path.join(dst_dir, f"{part_name}{ext}")
        shutil.copy2(step_src, step_dst)
        print(f"Copied STEP -> {os.path.basename(step_dst)}")
    else:
        print("⚠ No STEP found in SOURCE folder (ok if PDF-only).")

    # QR
    qr_png = ensure_qr_png(dst_dir, part_name)

    # Stamp QR onto the repo PDF (overwrite stable name)
    out_pdf = stamp_pdf_overwrite(pdf_src, qr_png, dst_dir, part_name)

   
    # ALSO copy stamped PDF + QR PNG back into the SOURCE folder (usually ...\ASAP\QR)
    os.makedirs(src_dir, exist_ok=True)

    shutil.copy2(out_pdf, os.path.join(src_dir, os.path.basename(out_pdf)))
    shutil.copy2(qr_png, os.path.join(src_dir, os.path.basename(qr_png)))

    print("Copied stamped PDF + QR back to SOURCE folder:", src_dir)


   # Autodesk link handling
autodesk_link = load_autodesk_link(dst_dir)

if step_src:
        ans = input("\nUpdate Autodesk link? (y/n, Enter = no): ").strip().lower()

        if ans == "y" or not autodesk_link:
        print("Opening Autodesk Viewer upload…")
        webbrowser.open(AUTODESK_UPLOAD_URL)

        input("After you COPY the autode.sk link, press ENTER here...")

        autodesk_link = try_get_clipboard_autodesk_link()
        if not autodesk_link:
            autodesk_link = input(
                "Paste the https://autode.sk/... link here: "
            ).strip()

        if autodesk_link.startswith(("https://autode.sk/", "http://autode.sk/")):
            save_autodesk_link(dst_dir, autodesk_link)
        else:
            print("⚠ Not a valid autode.sk link. Keeping previous link.")
            autodesk_link = load_autodesk_link(dst_dir)


    # Update index.html with cache-bust so phones don't show old PDFs
    cache_bust = int(time.time())
    update_index_html(dst_dir, part_name, autodesk_link, cache_bust)

    page_url = BASE_URL.rstrip("/") + "/" + quote(part_name) + "/"

    print("\nDONE ✅")
    print("Page URL   :", page_url)
    print("Repo folder:", dst_dir)

    # ---- Git checks (safe) ----
    try:
        if has_uncommitted_changes(REPO_ROOT):
            print("\n⚠ Git: You have uncommitted changes.")
            print("   Open GitHub Desktop, review, then COMMIT.")
        else:
            if has_unpushed_commits(REPO_ROOT):
                print("\n✅ Git: Clean working tree, but commits are not pushed yet.")
                prompt_push(REPO_ROOT)
            else:
                print("\n✅ Git: Everything is already pushed.")
    except Exception as e:
        print("\n⚠ Git check failed (not fatal):", e)
        print("   You can push manually in GitHub Desktop.")


if __name__ == "__main__":
    main()

  