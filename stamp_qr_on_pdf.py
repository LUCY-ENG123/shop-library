import os
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import io

ROOT = os.path.dirname(os.path.abspath(__file__))

QR_SIZE_INCHES = 1.25
MARGIN_INCHES = 0.4

for folder in os.listdir(ROOT):
    part_dir = os.path.join(ROOT, folder)
    if not os.path.isdir(part_dir) or folder.startswith("_"):
        continue

    pdf_path = os.path.join(part_dir, f"{folder}.pdf")
    qr_path = os.path.join(part_dir, f"QR_{folder}.png")
    out_pdf = os.path.join(part_dir, f"{folder}_QR.pdf")

    if not os.path.exists(pdf_path) or not os.path.exists(qr_path):
        continue

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    first_page = reader.pages[0]
    width = float(first_page.mediabox.width)
    height = float(first_page.mediabox.height)

    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(width, height))

    qr_size = QR_SIZE_INCHES * inch
    margin = MARGIN_INCHES * inch

    x = width - qr_size - margin
    y = margin

    c.drawImage(qr_path, x, y, qr_size, qr_size, mask='auto')
    c.save()

    packet.seek(0)
    overlay = PdfReader(packet)

    first_page.merge_page(overlay.pages[0])
    writer.add_page(first_page)

    for page in reader.pages[1:]:
        writer.add_page(page)

    with open(out_pdf, "wb") as f:
        writer.write(f)

    print(f"Stamped QR onto: {out_pdf}")

print("All done.")
