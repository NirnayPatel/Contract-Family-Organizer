#!/usr/bin/env python3
"""
Text extraction CLI for contract files (PDF, DOCX, TXT and more).

Usage:
    python organizer/extract.py <dir> [--cache-dir .cfo_cache] [--output results.json]

Outputs a JSON array:
    [{path, filename, text, extraction_status, char_count}]

extraction_status values:
    "ok"           – text extracted successfully
    "ocr"          – digital extraction failed, OCR used
    "ocr_failed"   – OCR attempted but produced < 20 chars
    "failed"       – extraction failed entirely
    "empty"        – file is empty or has no readable text
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Optional imports — degrade gracefully
try:
    import pypdf
    _PYPDF = True
except ImportError:
    _PYPDF = False

try:
    from docx import Document as DocxDocument
    _DOCX = True
except ImportError:
    _DOCX = False

try:
    from pdf2image import convert_from_path
    import pytesseract
    _OCR = True
except ImportError:
    _OCR = False

from organizer import cache as cache_mod

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md", ".rtf", ".odt"}


def extract_pdf(path: str) -> tuple[str, str]:
    """Returns (text, status). Status: 'ok', 'ocr', 'ocr_failed', 'failed'."""
    if not _PYPDF:
        return "", "failed"
    try:
        reader = pypdf.PdfReader(path)
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        text = "\n".join(pages).strip()
        if len(text) >= 100:
            return text, "ok"
    except Exception:
        pass

    # Fall back to OCR
    if not _OCR:
        return "", "failed"
    try:
        images = convert_from_path(path, dpi=200)
        ocr_pages = [pytesseract.image_to_string(img) for img in images]
        text = "\n".join(ocr_pages).strip()
        if len(text) >= 20:
            return text, "ocr"
        return text, "ocr_failed"
    except Exception:
        return "", "failed"


def extract_docx(path: str) -> tuple[str, str]:
    if not _DOCX:
        return "", "failed"
    try:
        doc = DocxDocument(path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        # Also grab table cells
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        paragraphs.append(cell.text.strip())
        text = "\n".join(paragraphs).strip()
        return (text, "ok") if text else ("", "empty")
    except Exception:
        return "", "failed"


def extract_text_file(path: str) -> tuple[str, str]:
    for encoding in ("utf-8", "latin-1", "cp1252"):
        try:
            text = Path(path).read_text(encoding=encoding).strip()
            return (text, "ok") if text else ("", "empty")
        except (UnicodeDecodeError, OSError):
            continue
    return "", "failed"


def extract_file(path: str) -> tuple[str, str]:
    ext = Path(path).suffix.lower()
    if ext == ".pdf":
        return extract_pdf(path)
    elif ext in (".docx", ".doc"):
        return extract_docx(path)
    elif ext in (".txt", ".md", ".rtf", ".odt"):
        return extract_text_file(path)
    else:
        # Try as plain text
        text, status = extract_text_file(path)
        if status == "ok":
            return text, "ok"
        return "", "failed"


def discover_files(directory: str) -> list[str]:
    results = []
    for root, dirs, files in os.walk(directory):
        # Skip hidden dirs and cache dirs
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
        for fname in files:
            if fname.startswith("."):
                continue
            ext = Path(fname).suffix.lower()
            if ext in SUPPORTED_EXTENSIONS:
                results.append(os.path.join(root, fname))
    return sorted(results)


def process_directory(directory: str, cache_dir: str) -> list[dict]:
    files = discover_files(directory)
    results = []
    for path in files:
        cached = cache_mod.load(path, cache_dir)
        if cached:
            results.append(cached)
            continue

        text, status = extract_file(path)
        record = {
            "path": path,
            "filename": Path(path).name,
            "text": text,
            "extraction_status": status,
            "char_count": len(text),
        }
        cache_mod.save(path, cache_dir, record)
        results.append(record)
    return results


def main():
    parser = argparse.ArgumentParser(description="Extract text from contract files.")
    parser.add_argument("directory", help="Path to contracts directory")
    parser.add_argument("--cache-dir", default=".cfo_cache", help="Cache directory")
    parser.add_argument("--output", default="-", help="Output file path (- for stdout)")
    parser.add_argument("--no-cache", action="store_true", help="Disable cache")
    args = parser.parse_args()

    cache_dir = os.path.join(args.directory, args.cache_dir) if not os.path.isabs(args.cache_dir) else args.cache_dir
    if args.no_cache:
        cache_dir = None

    results = process_directory(args.directory, cache_dir or "/tmp/.cfo_nocache")
    output = json.dumps(results, ensure_ascii=False, indent=2)

    if args.output == "-":
        print(output)
    else:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Wrote {len(results)} records to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
