# Contract Family Organizer

This project provides a Claude Code skill to organize legal contracts into contract families.

## Quick Start

Type `/organize-contracts` to launch the skill. It will ask you a few questions and then analyze your contracts.

## Available Skills

- `/organize-contracts` — Analyze a folder of legal contracts. Groups them into families (parent agreements, amendments, addendums, schedules, SOWs), extracts counterparties, identifies key clauses, flags legal-ops risks, and outputs a JSON + Markdown report. Optionally reorganizes files into family folders.

## Python Utilities

The `organizer/` package provides standalone text extraction:

```bash
# Extract text from all contracts in a directory
python organizer/extract.py /path/to/contracts --output results.json
```

Supports: PDF (with OCR fallback for scanned docs), DOCX, TXT, MD. Results are cached in `.cfo_cache/` to avoid re-processing.

## Environment

Dependencies are auto-installed on session start (claude.ai/code). For local use:

```bash
pip install -e .
```
