# Contract Family Organizer

A Claude Code skill that organizes any folder of legal contracts into structured **contract families** — complete with hierarchy, counterparty relationships, key clause extraction, lifecycle status, and legal-ops risk flags.

Works with any contract repository you point it at. Handles PDF, DOCX, DOC, TXT, and mixed file collections.

---

## What It Does

Point it at a folder of contracts and it will:

- **Group** contracts into families anchored to a parent/master agreement
- **Build a hierarchy** within each family:
  - Root / Master Agreement
  - Amendments (sorted by sequence number)
  - Addendums & Exhibits
  - Schedules & Statements of Work (SOW)
  - Order Forms & Renewals
  - Related Documents (NDAs, DPAs, etc.)
- **Identify counterparties** and their roles (vendor, client, licensor, etc.) with fuzzy deduplication across name variations
- **Extract key clauses**: auto-renewal, governing law, arbitration, IP assignment, indemnification caps, limitation of liability, confidentiality, termination rights
- **Flag legal-ops risks**: expiring contracts, missing dates, amendments without parents, uncapped indemnification, auto-renewal risks
- **Set lifecycle status**: active, expired, pending, superseded, terminated
- **Flag uncertain contracts** with a confidence score (0–1) and ask you to resolve them interactively
- **Output** a `contract_families.json` + `report.md`, and optionally reorganize files into a family folder structure

---

## Installation

### 1. Clone this repository

```bash
git clone https://github.com/nirnaypatel/contract-family-organizer- ~/contract-family-organizer
cd ~/contract-family-organizer
```

### 2. Install Python dependencies

```bash
pip install -e .
```

For OCR support on scanned PDFs (optional), also install Tesseract:

```bash
# macOS
brew install tesseract

# Ubuntu / Debian
sudo apt install tesseract-ocr

# Windows
# Download installer from: https://github.com/tesseract-ocr/tesseract
```

### 3. Install the Claude Code skill

Copy the skill into your Claude Code skills directory:

```bash
# Project-level (recommended — only available in this project)
mkdir -p .claude/skills
cp ~/contract-family-organizer/.claude/skills/organize-contracts.md .claude/skills/

# OR global (available in all Claude Code sessions)
mkdir -p ~/.claude/skills
cp ~/contract-family-organizer/.claude/skills/organize-contracts.md ~/.claude/skills/
```

> The skill can be installed globally in `~/.claude/skills/` to work in any Claude Code session, or project-locally in `.claude/skills/` for a specific repo.

---

## Usage

Open Claude Code (CLI or claude.ai/code) in any directory, then type:

```
/organize-contracts
```

Claude will ask you three questions to get started:

1. **Directory path** — where are your contracts?
2. **Organization type** — helps with contract type classification
3. **Output preference** — analysis only, or reorganize files too?

Then it runs, pausing to ask you about any uncertain contracts, shows you the proposed family structure for your approval, and generates the output.

---

## Output

### `contract_families.json`

Machine-readable structured data:

```json
{
  "total_families": 8,
  "families": [
    {
      "family_key": "ACME_CORP_MSA_2022",
      "display_name": "Acme Corp Master Services Agreement (2022)",
      "counterparties": [
        { "canonical_name": "Acme Corp", "role": "vendor", "aliases": ["ACME CORPORATION"] }
      ],
      "hierarchy": {
        "root": { "filename": "Acme_MSA_2022.pdf", "confidence": 0.95, "lifecycle_status": "active" },
        "amendments": [ ... ],
        "schedules": [ ... ],
        "sows": [ ... ]
      },
      "legal_ops_flags": [
        { "flag": "auto_renewal_risk", "severity": "MEDIUM", "detail": "Auto-renewal clause found; notice deadline unknown" }
      ]
    }
  ],
  "review_needed": [ ... ],
  "unclassified": [ ... ]
}
```

### `report.md`

Human-readable report with:
- Legal ops flags table sorted by severity (HIGH → MEDIUM → LOW)
- ASCII hierarchy tree per contract family
- Counterparty table with roles
- Key dates (effective, expiration, auto-renewal notice deadlines)
- Documents needing review with uncertainty reasons
- Summary statistics

### Folder Reorganization (optional)

```
output/
  ACME_CORP_MSA_2022/
    root/
    amendments/
    schedules/
    addendums/
    sows/
    order_forms/
    review_needed/
  BETA_LLC_NDA_2021/
    root/
  _unclassified/
```

---

## Contract Types Recognized

30+ agreement types across: Commercial, Services, Employment, IP, Finance, Real Estate, Corporate/M&A, Regulatory, and Supply Chain.

See the full taxonomy in [`.claude/skills/organize-contracts.md`](.claude/skills/organize-contracts.md).

---

## Confidence Scores & Uncertainty

Every contract gets a confidence score (0.0–1.0):

| Score | Meaning |
|-------|---------|
| 0.85–1.0 | High confidence — clear classification from filename + content |
| 0.60–0.84 | Moderate — classified but some ambiguity |
| < 0.60 | Low — pauses and asks you to confirm (`review_needed: true`) |
| ≤ 0.30 | Very low — extraction failed or completely ambiguous |

---

## Supported File Types

| Extension | Method |
|-----------|--------|
| `.pdf` | `pypdf` for digital PDFs; `pytesseract` OCR fallback for scanned |
| `.docx` / `.doc` | `python-docx` |
| `.txt` / `.md` | Direct read |

---

## Requirements

- Python 3.11+
- Claude Code CLI or claude.ai/code
- Tesseract (optional, for scanned PDF OCR)

---

## License

MIT
