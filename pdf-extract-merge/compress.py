import subprocess
from pathlib import Path

# === CONFIG ===
input_dir = Path("output")         # folder tempat PDF hasil merge/OCR
compress_dir = Path("compress")    # folder untuk menyimpan hasil kompres
compress_dir.mkdir(exist_ok=True)
quality = "ebook"                  # pilihan: screen, ebook, printer, prepress, default

# === Fungsi kompresi ===
def compress_pdf(input_pdf: Path, output_pdf: Path, quality: str = "ebook"):
    """Compress PDF using Ghostscript."""
    qualities = {
        "screen": "/screen",
        "ebook": "/ebook",
        "printer": "/printer",
        "prepress": "/prepress",
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
        print(f"🗜️ Compressed {input_pdf} → {output_pdf} ({quality})")
    except FileNotFoundError:
        print("⚠️ Ghostscript not found. Install Ghostscript to enable compression.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Compression failed for {input_pdf}: {e}")

# === Proses semua PDF di folder input secara rekursif ===
pdf_files = list(input_dir.rglob("*.pdf"))

for pdf in pdf_files:
    # Buat struktur folder yang sama di compress_dir
    rel_path = pdf.relative_to(input_dir)
    out_file = compress_dir / rel_path
    out_file.parent.mkdir(parents=True, exist_ok=True)

    # Nama file tetap sama
    compress_pdf(pdf, out_file, quality=quality)

