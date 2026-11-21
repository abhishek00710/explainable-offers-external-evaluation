#!/usr/bin/env python3
"""Independent Python recomputation of classification metrics from Swift CSVs."""
import argparse, csv, json, math
from collections import defaultdict
from pathlib import Path

GOLD = ["groceries", "dining", "transport", "shopping", "utilities"]
PRED = GOLD + ["unknown"]
POLICIES = ["metadata", "tokens", "combined", "conflict_abstain"]
UNITS = ["transactions", "unique_descriptions"]

def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def near(a, b, tol=1e-12):
    return math.isclose(float(a), float(b), rel_tol=0, abs_tol=tol)

def audit(results_dir, dataset_summary):
    results_dir = Path(results_dir)
    summary_meta = json.loads(Path(dataset_summary).read_text(encoding="utf-8"))
    confusion_rows = read_csv(results_dir / "confusion.csv")
    summaries = read_csv(results_dir / "summary.csv")
    class_rows = read_csv(results_dir / "per-class.csv")
    assert len(confusion_rows) == len(POLICIES)*len(UNITS)*len(GOLD)*len(PRED), len(confusion_rows)
    C = defaultdict(lambda: defaultdict(int))
    for row in confusion_rows:
        n=int(row["count"])
        assert n >= 0
        C[(row["policy"],row["unit"])][(row["gold"],row["predicted"])] += n
    S = {(r["policy"],r["unit"]): r for r in summaries}
    assert len(S) == len(POLICIES)*len(UNITS)
    expected_primary_n = int(summary_meta["mapped_rows_after_overlap_exclusion"])
    expected_case_n = int(summary_meta["mapped_unanimous_description_cases"])
    for policy in POLICIES:
      for unit in UNITS:
        key=(policy,unit); m=C[key]; s=S[key]
        n=sum(m[(g,p)] for g in GOLD for p in PRED)
        expected_n=expected_primary_n if unit=="transactions" else expected_case_n
        assert n == expected_n, (key,n,expected_n)
        correct=sum(m[(g,g)] for g in GOLD)
        covered=sum(m[(g,p)] for g in GOLD for p in GOLD)
        abstained=sum(m[(g,"unknown")] for g in GOLD)
        classified_correct=correct
        accuracy=correct/n if n else 0
        coverage=covered/n if n else 0
        classified_only=classified_correct/covered if covered else 0
        f1s=[]
        for cat in GOLD:
            tp=m[(cat,cat)]
            fp=sum(m[(g,cat)] for g in GOLD if g != cat)
            fn=sum(m[(cat,p)] for p in PRED if p != cat)
            support=sum(m[(cat,p)] for p in PRED)
            precision=tp/(tp+fp) if tp+fp else 0
            recall=tp/support if support else 0
            f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0
            f1s.append(f1)
            cr=[r for r in class_rows if (r["policy"],r["unit"],r["class"])==(policy,unit,cat)]
            assert len(cr)==1
            cr=cr[0]
            for field, value in [("tp",tp),("fp",fp),("fn",fn),("support",support)]: assert int(cr[field])==value,(key,cat,field,cr[field],value)
            for field,value in [("precision",precision),("recall",recall),("f1",f1)]: assert near(cr[field],value),(key,cat,field,cr[field],value)
        macro=sum(f1s)/len(GOLD)
        for field,value in [("n",n),("correct",correct),("covered",covered),("abstained",abstained),
                            ("classified_correct",classified_correct),("classified_n",covered)]:
            assert int(s[field])==value,(key,field,s[field],value)
        for field,value in [("accuracy",accuracy),("coverage",coverage),
                            ("abstention_rate",abstained/n if n else 0),("macro_f1",macro)]:
            assert near(s[field],value),(key,field,s[field],value)
        if covered == 0:
            assert s["classified_only_accuracy"] == "NA", (key,s["classified_only_accuracy"])
        else:
            assert near(s["classified_only_accuracy"],classified_only),(key,"classified_only_accuracy",s["classified_only_accuracy"],classified_only)
    # With metadata intentionally unavailable, only token evidence can influence combined/conflict policies.
    for unit in UNITS:
        for policy in ["combined","conflict_abstain"]:
            assert C[(policy,unit)] == C[("tokens",unit)], (policy,unit,"expected text-only fallback identity")
        assert sum(C[("metadata",unit)][(g,"unknown")] for g in GOLD) == (expected_primary_n if unit=="transactions" else expected_case_n)
        assert all(C[("metadata",unit)][(g,p)] == 0 for g in GOLD for p in GOLD)
    return len(confusion_rows), len(summaries), len(class_rows)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--results",required=True)
    ap.add_argument("--dataset-summary",required=True)
    ap.add_argument("--log",required=True)
    a=ap.parse_args()
    counts=audit(a.results,a.dataset_summary)
    lines=["Independent audit: PASS",
           "Recomputed confusion totals and all-record accuracy from exported counts.",
           "Recomputed per-class TP/FP/FN, precision, recall, F1, support and arithmetic macro-F1.",
           "Verified coverage, abstention, classified-only accuracy and denominators; zero-classification conditional accuracy is NA.",
           "Verified metadata-only is unknown for all records when metadata is absent.",
           "Verified combined and conflict-abstention equal token-only under this metadata-free input.",
           f"Rows checked: confusion={counts[0]}, summaries={counts[1]}, per-class={counts[2]}.",
           "No per-transaction descriptions or predictions are exported."]
    Path(a.log).write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("\n".join(lines))
if __name__=="__main__": main()
