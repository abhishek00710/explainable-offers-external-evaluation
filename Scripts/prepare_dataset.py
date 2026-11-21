#!/usr/bin/env python3
"""Prepare a privacy-minimizing, temporary input for the fixed Swift policies."""
import argparse, base64, hashlib, json, re, unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from openpyxl import load_workbook

# Frozen semantic crosswalk based only on the dataset's own category definitions.
CROSSWALK = {
    "groceries": "groceries",
    "dine out": "dining",
    "travel": "transport",
    "amazon": "shopping",
    "other shopping": "shopping",
    "clothes": "shopping",
    "home improvement": "shopping",
    "bills": "utilities",
}

def norm(text):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text).casefold()).strip()

def phrase_norm(text):
    text = unicodedata.normalize("NFKC", text).casefold()
    return re.sub(r"[^\w]+", " ", text, flags=re.UNICODE).strip()

def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", required=True, type=Path)
    ap.add_argument("--catalog", required=True, type=Path)
    ap.add_argument("--records-out", required=True, type=Path)
    ap.add_argument("--summary-out", required=True, type=Path)
    args = ap.parse_args()

    workbook_bytes = args.xlsx.read_bytes()
    workbook = load_workbook(args.xlsx, read_only=True, data_only=True)
    sheet_name = "Anonymized Original with Catego"
    if sheet_name not in workbook.sheetnames:
        raise SystemExit(f"Expected worksheet missing: {sheet_name}")
    ws = workbook[sheet_name]
    rows = ws.iter_rows(values_only=True)
    header = next(rows)
    positions = {str(value).strip(): i for i, value in enumerate(header) if value is not None}
    required = ["Transaction Description", "Category"]
    if any(name not in positions for name in required):
        raise SystemExit("Required description/category columns are missing")

    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    if not isinstance(catalog, list):
        raise SystemExit("Original merchant catalog must be a JSON list")
    case_phrases = []
    for case in catalog:
        value = case.get("description")
        if value:
            normalized = phrase_norm(str(value))
            if normalized:
                case_phrases.append((str(case.get("caseID", "")), normalized))
    if len(case_phrases) != 36:
        raise SystemExit(f"Expected 36 original authored cases; found {len(case_phrases)}")

    all_valid = []
    raw_label_counts = Counter()
    missing_label_or_text = 0
    for row in rows:
        description = row[positions["Transaction Description"]]
        raw_label = row[positions["Category"]]
        if description is None or raw_label is None or not str(raw_label).strip():
            missing_label_or_text += 1
            continue
        description = str(description).strip()
        label = str(raw_label).strip()
        raw_label_counts[label] += 1
        all_valid.append((description, label))

    mapped, overlap = [], []
    unmapped_counts = Counter()
    overlap_case_ids = set()
    for description, label in all_valid:
        gold = CROSSWALK.get(label.casefold())
        if gold is None:
            unmapped_counts[label] += 1
            continue
        normalized_words = phrase_norm(description)
        matching = [(case_id, phrase) for case_id, phrase in case_phrases
                    if re.search(r"(?:^| )" + re.escape(phrase) + r"(?: |$)", normalized_words)]
        if matching:
            overlap.append((description, gold, label))
            overlap_case_ids.update(case_id for case_id, _ in matching)
        else:
            mapped.append((description, gold, label))

    # Labels remain separate from the Transaction sent to Swift.
    args.records_out.parent.mkdir(parents=True, exist_ok=True)
    case_groups = defaultdict(set)
    normalized_rows = Counter()
    with args.records_out.open("w", encoding="utf-8", newline="") as out:
        for description, gold, _ in mapped:
            normalized = norm(description)
            case_hash = sha(normalized)
            case_groups[case_hash].add(gold)
            normalized_rows[case_hash] += 1
            encoded = base64.b64encode(description.encode("utf-8")).decode("ascii")
            out.write(f"{case_hash}\t{gold}\t{encoded}\n")

    ambiguous_hashes = {key for key, values in case_groups.items() if len(values) > 1}
    unanimous_hashes = set(case_groups) - ambiguous_hashes
    summary = {
        "dataset": "Bank Transactions Dataset (MoneyData), Mendeley Data v1",
        "doi": "10.17632/dnxtg6n4rv.1",
        "license": "CC BY 4.0",
        "source_file_sha256": hashlib.sha256(workbook_bytes).hexdigest(),
        "worksheet": sheet_name,
        "worksheet_data_rows": ws.max_row - 1,
        "rows_with_description_and_category": len(all_valid),
        "rows_missing_description_or_category": missing_label_or_text,
        "authored_case_count": len(case_phrases),
        "overlap_authored_case_count": len(overlap_case_ids),
        "overlap_rows_excluded": len(overlap),
        "mapped_rows_after_overlap_exclusion": len(mapped),
        "mapped_gold_counts": dict(sorted(Counter(gold for _, gold, _ in mapped).items())),
        "mapped_raw_label_counts_before_overlap_exclusion": {
            label: raw_label_counts[label] for label in sorted(raw_label_counts)
            if label.casefold() in CROSSWALK
        },
        "out_of_scope_label_counts": dict(sorted(unmapped_counts.items())),
        "mapped_unique_normalized_descriptions": len(case_groups),
        "mapped_unanimous_description_cases": len(unanimous_hashes),
        "mapped_ambiguous_description_cases_excluded_from_case_level": len(ambiguous_hashes),
        "rows_in_ambiguous_description_cases": sum(normalized_rows[key] for key in ambiguous_hashes),
        "normalization": "Unicode NFKC, casefold, collapse whitespace; punctuation retained",
        "crosswalk": CROSSWALK,
        "overlap_case_ids_not_exported": True,
        "row_level_text_exported": False,
        "mapped_input_contains_only_description_and_gold": True,
        "raw_text_intermediate_transient_and_not_in_results": True,
    }
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    args.summary_out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("Prepared mapped external evaluation input.")
    for key in ("rows_with_description_and_category", "rows_missing_description_or_category",
                "overlap_authored_case_count", "overlap_rows_excluded",
                "mapped_rows_after_overlap_exclusion", "mapped_unique_normalized_descriptions",
                "mapped_unanimous_description_cases", "mapped_ambiguous_description_cases_excluded_from_case_level"):
        print(f"{key}={summary[key]}")
    print("mapped_gold_counts=" + json.dumps(summary["mapped_gold_counts"], sort_keys=True))

if __name__ == "__main__":
    main()
