import os
import io
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

ROOT = os.path.dirname(os.path.abspath(__file__))

QR_SIZE_INCHES = 1.25
MARGIN_INCHES = 0.4

def pick_pdf(folder_path, folder_name):
    """Prefer '<folder>.pdf'. Otherwise pick the newest PDF in the folder."""
    preferred = os.path.join(folder_path, f"{folder_name}.pdf")
    if os.path.exists(preferred):
        return preferred

    pdfs = []
    for f in os.listdir(folder_path):
        if f.lower().endswith(".pdf") and not f.lower().endswith("_qr.pdf"):
            full = os.path.join(folder_path, f)
            pdfs.append((os.path.getmtime(full), full))

    if not pdfs:
        return None

    pdfs.sort(reverse=True)  # newest first
    return pdfs[0][1]

def pick_qr(folder_path, folder_name):
    """Prefer 'QR_<folder>.png'. Otherwise pick the newest PNG that looks like a QR."""
    preferred = os.path.join(folder_path, f"QR_{folder_name}.png")
    if os.path.exists(preferred):
        return preferred

    # fallback: any PNG with 'qr' in the name, else any PNG
    pngs_qr = []
    pngs_any = []

    for f in os.listdir(folder_path):
        if f.lower().endswith(".png"):
            full = os.path.join(folder_path, f)
            t = os.path.getmtime(full)
            if "qr" in f.lower():
                pngs_qr.append((t, full))
            else:
                pngs_any.append((t, full))

    if pngs_qr:
        pngs_qr.sort(reverse=True)
        return pngs_qr[0][1]

    if pngs_any:
        pngs_any.sort(reverse=True)
        return pngs_any[0][1]

    return None

stamped = 0
skipped = 0

for folder in os.listdir(ROOT):
    part_dir = os.path.join(ROOT, folder)

    if not os.path.isdir(part_dir):
        continue

    # skip template/admin folders
    if folder.startswith("_"):
        continue

    pdf_path = pick_pdf(part_dir, folder)
    qr_path = pick_qr(part_dir, folder)

    if not pdf_path or not qr_path:
        skipped += 1
        print(f"SKIP: {folder}")
        if not pdf_path:
            print("  ⛔ No PDF found")
        if not qr_path:
            print("  ⛔ No PNG/QR found")
        continue

    out_pdf = os.path.join(part_dir, f"{os.path.splitext(os.path.basename(pdf_path))[0]}_QR.pdf")

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    first_page = reader.pages[0]
    width = float(first_page.mediabox.width)
    height = float(first_page.mediabox.height)

    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(width, height))

    qr_size = QR_SIZE_INCHES * inch
    margin = MARGIN_INCHES * inch

    TITLEBLOCK_LEFT_X = 10.0 * inch      # left edge of title block
    TITLEBLOCK_BOTTOM_Y = 0.45 * inch    # move QR up
    GAP = 0.05 * inch                    # tighter to title block

    x = TITLEBLOCK_LEFT_X - qr_size - GAP
    y = TITLEBLOCK_BOTTOM_Y

    c.drawImage(qr_path, x, y, qr_size, qr_size, mask="auto")
    c.save()

    packet.seek(0)
    overlay = PdfReader(packet)

    first_page.merge_page(overlay.pages[0])
    writer.add_page(first_page)

    for page in reader.pages[1:]:
        writer.add_page(page)

    with open(out_pdf, "wb") as f:
        writer.write(f)

    stamped += 1
    print(f"Stamped QR onto: {out_pdf}")
    print(f"  PDF used: {pdf_path}")
    print(f"  QR used : {qr_path}")

print(f"\nAll done. Stamped: {stamped} | Skipped: {skipped}")

