#!/usr/bin/env python3
"""Scan the supplement tree for common release disclosures and raw-data files."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
# Assemble path prefixes so the scanner does not match its own rule text.
HOME_PATH = re.compile(r"(?:/" + "Us" + r"ers/[^/\s]+|/" + "ho" + r"me/[^/\s]+|[A-Za-z]:\\" + "Us" + r"ers\\[^\\\s]+)")
SECRET = re.compile(
    r"(?i)(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
    r"AKIA[0-9A-Z]{16}|(?:api[_-]?key|access[_-]?token|client[_-]?secret)\s*[:=]\s*['\"]?[^\s'\"]{12,}|"
    r"bearer\s+[A-Za-z0-9._-]{16,})"
)
EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
FORBIDDEN_EXT = {".xlsx", ".xls", ".tsv", ".zip", ".parquet"}
ALLOWED_URL_PREFIXES = (
    "https://github.com/",
    "https://data.mendeley.com/",
    "https://doi.org/",
    "https://creativecommons.org/",
    "https://huggingface.co/",
    "https://www.apache.org/",
    "http://www.apache.org/",
)
URL = re.compile(r"https?://[^\s)\]>]+")

def main() -> int:
    files = sorted(p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts)
    issues: list[str] = []
    text_files = 0
    for path in files:
        rel = path.relative_to(ROOT)
        if path.suffix.lower() in FORBIDDEN_EXT:
            issues.append(f"source-data or row-export file present: {rel}")
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        text_files += 1
        for label, pattern in (("personal absolute path", HOME_PATH), ("credential-like value", SECRET), ("email address", EMAIL)):
            if pattern.search(content):
                issues.append(f"{label} pattern found: {rel}")
        for url in URL.findall(content):
            if not url.startswith(ALLOWED_URL_PREFIXES):
                issues.append(f"unreviewed URL: {rel}: {url}")

    lines = [
        "Publication disclosure scan",
        f"Files inventoried: {len(files)}",
        f"UTF-8 text files scanned: {text_files}",
        "Checks: personal home paths, credential-like patterns, email addresses, unreviewed URLs, and raw dataset/row-export file extensions.",
    ]
    if issues:
        lines += ["Status: FAIL", *[f"- {item}" for item in issues]]
    else:
        lines.append("Status: PASS; no matching disclosure patterns or source-data/row-export files found.")
    output = "\n".join(lines) + "\n"
    print(output, end="")
    (ROOT / "Results" / "publication-audit.txt").write_text(output, encoding="utf-8")
    return 1 if issues else 0

if __name__ == "__main__":
    sys.exit(main())
