import os
from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter

# Set working directory
workdir = Path(".")
input_dir = workdir / "input"
output_dir = workdir / "output"

# Create output directory
output_dir.mkdir(exist_ok=True)

# Walk through input directory recursively
for pdf_path in input_dir.rglob("*.pdf"):
    # Relative path from input/
    rel_path = pdf_path.relative_to(input_dir)
    
    # Output directory for this PDF
    pdf_output_dir = output_dir / rel_path.with_suffix("")  # remove .pdf
    pdf_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Read PDF
    reader = PdfReader(str(pdf_path))
    
    # Split each page into a new file
    for i, page in enumerate(reader.pages, start=1):
        writer = PdfWriter()
        writer.add_page(page)
        out_path = pdf_output_dir / f"{i}.pdf"
        with open(out_path, "wb") as f:
            writer.write(f)
    
    print(f"✅ Split {pdf_path} → {pdf_output_dir}/")

print("🎉 All PDFs processed successfully!")

