import os
from pathlib import Path
import tempfile
from PyPDF2 import PdfMerger
from pdf2image import convert_from_path
from PIL import Image
import pytesseract

# === CONFIG ===
workdir = Path(".")
input_dir = workdir / "input"
output_dir = workdir / "output"
output_dir.mkdir(exist_ok=True)

def is_leaf_dir(directory: Path) -> bool:
    """Return True if directory contains PDFs but no subdirectories."""
    has_pdfs = any(f.suffix.lower() == ".pdf" for f in directory.iterdir() if f.is_file())
    has_subdirs = any(sub.is_dir() for sub in directory.iterdir())
    return has_pdfs and not has_subdirs

def detect_image_rotation(img: Image.Image) -> int:
    """Detect page rotation in degrees using Tesseract."""
    try:
        osd = pytesseract.image_to_osd(img)
        for line in osd.splitlines():
            if "Orientation in degrees" in line:
                return int(line.split(":")[-1].strip())
    except Exception as e:
        print(f"⚠️ Rotation detection failed: {e}")
    return 0

def ocr_page_to_pdf(img: Image.Image, output_pdf: Path):
    """Run Tesseract OCR on the image and output a searchable PDF page."""
    pdf_bytes = pytesseract.image_to_pdf_or_hocr(img, extension='pdf', config='--dpi 300')
    with open(output_pdf, "wb") as f:
        f.write(pdf_bytes)


def process_pdf_to_searchable(pdf_path: Path, tmp_dir: Path) -> Path:
    """Convert a PDF to a rotation-corrected, OCR-searchable PDF."""
    fixed_pdf_path = tmp_dir / pdf_path.name

    with tempfile.TemporaryDirectory() as pagedir:
        pages = convert_from_path(pdf_path, dpi=300, output_folder=pagedir)
        page_pdfs = []

        for i, img in enumerate(pages, start=1):
            rotation = detect_image_rotation(img)
            if rotation != 0:
                img = img.rotate(rotation, expand=True)
                print(f"↩️ Rotated page {i} of {pdf_path.name} by {-rotation}°")

            page_pdf = tmp_dir / f"page_{i}.pdf"
            ocr_page_to_pdf(img, page_pdf)
            page_pdfs.append(page_pdf)

        # Merge all OCR page PDFs into one
        merger = PdfMerger()
        for p in page_pdfs:
            merger.append(str(p))
        merger.write(fixed_pdf_path)
        merger.close()

    return fixed_pdf_path

import subprocess

def compress_pdf(input_pdf: Path, output_pdf: Path, quality: str = "screen"):
    """
    Compress PDF using Ghostscript.
    quality: "screen", "ebook", "printer", "prepress", "default"
    """
    qualities = {
        "screen": "/screen",      # lowest file size, 72 dpi
        "ebook": "/ebook",        # good quality, 150 dpi
        "printer": "/printer",    # high quality, 300 dpi
        "prepress": "/prepress",  # highest quality
        "default": "/default"
    }
    q = qualities.get(quality, "/screen")

    try:
        cmd = [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS={q}",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={output_pdf}",
            str(input_pdf)
        ]
        subprocess.run(cmd, check=True)
        print(f"🗜️ Compressed {input_pdf.name} → {output_pdf.name} ({quality})")
    except FileNotFoundError:
        print("⚠️ Ghostscript not found. Please install it to enable compression.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Compression failed for {input_pdf.name}: {e}")

# === MAIN ===
leaf_dirs = [d for d in input_dir.rglob("*") if d.is_dir() and is_leaf_dir(d)]

for d in leaf_dirs:
    pdf_files = sorted(d.glob("*.pdf"), key=lambda p: p.name.lower())
    if not pdf_files:
        continue

    rel_parent = d.relative_to(input_dir).parent
    out_parent = output_dir / rel_parent
    out_parent.mkdir(parents=True, exist_ok=True)
    out_file = out_parent / f"{d.name}.pdf"

    with tempfile.TemporaryDirectory() as tmpmerge:
        tmpmerge_dir = Path(tmpmerge)
        merged = PdfMerger()
        for pdf in pdf_files:
            searchable_pdf = process_pdf_to_searchable(pdf, tmpmerge_dir)
            merged.append(str(searchable_pdf))

        merged.write(out_file)
        merged.close()

    print(f"✅ Merged, auto-rotated, and OCR’d {len(pdf_files)} PDFs from {d} → {out_file}")

print("🎉 All PDFs processed into searchable, correctly oriented files!")

