import os
from pathlib import Path
from PyPDF2 import PdfMerger

# Set working directory
workdir = Path(".")
input_dir = workdir / "input"
output_dir = workdir / "output"
output_dir.mkdir(exist_ok=True)

def is_leaf_dir(directory: Path) -> bool:
    """Return True if the directory contains PDFs but no subdirectories."""
    has_pdfs = any(f.suffix.lower() == ".pdf" for f in directory.iterdir() if f.is_file())
    has_subdirs = any(sub.is_dir() for sub in directory.iterdir())
    return has_pdfs and not has_subdirs

# Find all leaf directories under input/
leaf_dirs = [d for d in input_dir.rglob("*") if d.is_dir() and is_leaf_dir(d)]

for d in leaf_dirs:
    pdf_files = sorted(d.glob("*.pdf"), key=lambda p: p.name.lower())
    if not pdf_files:
        continue

    # Create output folder preserving structure up to parent of leaf dir
    rel_parent = d.relative_to(input_dir).parent
    out_parent = output_dir / rel_parent
    out_parent.mkdir(parents=True, exist_ok=True)

    # Merged PDF filename = leaf dir name
    out_file = out_parent / f"{d.name}.pdf"

    # Merge PDFs
    merger = PdfMerger()
    for pdf in pdf_files:
        merger.append(str(pdf))
    merger.write(out_file)
    merger.close()

    print(f"✅ Merged {len(pdf_files)} PDFs from {d} → {out_file}")

print("🎉 All PDFs merged successfully!")

