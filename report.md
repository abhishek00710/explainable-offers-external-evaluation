# Independent external evaluation report

**Status:** separate supplement accompanying the v1.0.0 research artifact. This report does not amend the original release or the submitted-manuscript candidate. Repository visibility and approval status are time-sensitive and recorded in `publication-readiness.md`.

## Research question and decision

Can the four existing deterministic classification policies classify real bank transaction descriptions into the prototype's five spending categories when evaluated against externally supplied labels, without changing the policies or using the labels as input?

**Decision:** a narrow external text-only evaluation was feasible using MoneyData, an anonymized bank-transaction dataset deposited on Mendeley Data under CC BY 4.0. The data has manually assigned category labels, but the accompanying paper calls its taxonomy arbitrary and reports no independent multi-annotator adjudication. We therefore call them *external curator labels*, not objective ground truth. The dataset is suitable to expose failure modes of the text rules; it does not test structured metadata, offers, ranking, or production generalization.

## Dataset search and selection

MoneyData v1 (DOI [10.17632/dnxtg6n4rv.1](https://data.mendeley.com/datasets/dnxtg6n4rv/1)) was selected. The repository describes an anonymized, seven-year retail-bank dataset with over 6,500 transactions and a `Category` field, and lists CC BY 4.0. The related paper is [MoneyVis: Open Bank Transaction Data for Visualization and Beyond](https://doi.org/10.2312/evs.20231052). It distinguishes the bank-added transaction type from manually inspected spending categories and describes the category taxonomy as arbitrary. Attribution and license terms must accompany any publication of derived results. The workbook is not redistributed here; the source license notes that third-party content can have separate rights.

Other candidates were not used:

| Candidate | Public/license signal | Why not selected |
|---|---|---|
| [US Bank Transaction Categories v1](https://huggingface.co/datasets/DoDataThings/us-bank-transaction-categories) | Dataset card lists MIT and 16,000 rows | Explicitly synthetic; its generated labels are not independent external annotations, so it cannot answer this evaluation question. |
| [Categorising Noisy Bank Transactions](https://github.com/gbadedata/transaction-classification) | Repository displays an MIT license | Although its README describes real transaction data and labels, the repository-level code license does not clearly establish redistribution/publication rights for the embedded transaction data or independent label provenance. It was excluded on rights/provenance grounds. |

The selection favors a source with an explicit dataset license and a published account of how categories were assigned, while keeping the important label-quality caveat visible. The public deposit does not establish that every underlying third-party string is free of separate rights or privacy concerns. This supplement therefore retains only aggregate results.

## Provenance, filtering, and unique cases

The source workbook is MoneyData v1. Its downloaded workbook SHA-256 is recorded in `Results/dataset-summary.json`; the workbook and raw descriptions are not included. It contained 8,314 worksheet data rows: 6,543 with both a description and category, and 1,771 missing at least one. The source category field contains 29 distinct labels in the usable rows. Eight source labels were mapped to the five prototype categories; all other labels were excluded as out of scope rather than force-mapped.

The fixed crosswalk is documented in `protocol.md`: `Groceries → groceries`; `Dine Out → dining`; `Travel → transport`; `Amazon`, `Other Shopping`, `Clothes`, and `Home Improvement → shopping`; `Bills → utilities`. This is a deliberately broad, imperfect mapping. In particular, the source's `Travel` definition includes air, rail, and bus travel, and `Bills` includes several household utilities. `Food Shopping` was not mapped because the accompanying definition did not specify its meaning.

The original authored catalog contains 36 merchant cases. One case overlapped the external mapped descriptions; its two transaction rows were excluded before scoring. Matching used normalized merchant phrase boundaries. The matching case and row text are not disclosed. After crosswalk and overlap filtering, the transaction evaluation contains **3,224 rows**: dining 446, groceries 492, shopping 1,566, transport 246, and utilities 474.

For the secondary description-level analysis, strings were normalized using Unicode NFKC, case folding, and whitespace collapse, retaining punctuation. The rows yield **564 unique normalized descriptions**. One description had inconsistent mapped labels across 13 rows; it remains in transaction-level scoring but is omitted from the description-level analysis. Thus the secondary denominator is **563 unanimous unique descriptions**. These counts describe records in this source, not independent merchant identities.

## Evaluation procedure

The four policies—metadata-only, token-only, metadata-first combined, and conflict-aware abstention—were copied from the public v1.0.0 evaluation source and compiled unchanged. SHA-256 comparison confirms all six copied `OfferCore` files match their source counterparts; see `Results/source-digests.json`. No aliases, rules, thresholds, or labels were tuned.

Each classifier received the transaction description and `nil` for both merchant ID and structured category. The source `Category` label was held outside the classifier input and used only for scoring. Thus this tests text behavior only. Metadata-only abstains on every case. Since there is no structured metadata, combined and conflict-aware policies reduce to the token fallback. Their identical numbers are expected from the input contract, not evidence that they are equivalent when metadata exists.

Primary analysis counts transaction rows, retaining repeated descriptions as observed. Secondary analysis gives each unanimous normalized description equal weight. Unknown predictions count as incorrect in all-record accuracy. Coverage is the fraction assigned to one of the five known classes; abstention is its complement. Classified-only accuracy is computed among covered cases; it is `NA` when coverage is zero. Per-class metrics use one-vs-rest counts over the five mapped labels; undefined ratios are set to zero. Macro-F1 is the unweighted arithmetic mean of the five class F1 scores. The independent Python audit recomputes confusion totals, denominators, per-class metrics, macro-F1, coverage, abstention, and classified-only accuracy from exported aggregate CSVs.

No offer/ranking evaluation was possible because this dataset contains no offer set, eligibility decisions, or independently specified relevance judgments. No time, memory, customer outcome, or production metric was collected.

## Results

The full policy-level and class-level outputs are in `Results/summary.csv`, `Results/per-class.csv`, and `Results/confusion.csv`. The independent audit passed; details and console record are in `Results/audit.log` and `Results/reproduction.log`.

On 3,224 transaction rows, token rules classified 149 rows correctly (**4.62% all-row accuracy and coverage**) and abstained on 3,075 (**95.38%**). Conditional accuracy among the 149 classified rows was 100%, but this high conditional value applies to a small selected subset and must be read alongside the severe abstention. Five-class macro-F1 was **0.1283**. Shopping had 1,566 examples and no token-rule predictions; shopping F1 was zero. Utilities had the highest recall (78/474, 16.46%).

On 563 unanimous unique descriptions, token rules correctly classified 20 (**3.55% all-description accuracy and coverage**) and abstained on 543 (**96.45%**); macro-F1 was **0.0901**. Again, conditional accuracy was 20/20 among covered cases. The metadata-only method had zero coverage, so its classified-only accuracy is undefined (`NA`), not zero. The combined and conflict-aware policies exactly matched token-only on both units under the no-metadata input.

These are measured results from the stated macOS environment and this one labeled dataset. They are not estimates of performance on an institution's full transaction population.

## Interpretation for the manuscript

This supplement **challenges any broad reading that explicit token aliases alone provide useful coverage on varied real-world transaction descriptions**. Their high conditional precision is purchased through very heavy abstention, and the shopping category is a clear failure case. On this dataset, the text-only run does not demonstrate a benefit from metadata-first or conflict-aware design because the required independent metadata is absent.

The results do not invalidate the core *engineering* claims about authoritative eligibility, validity checks, account scoping, explainability, or safe abstention. Those were not exercised by this dataset. At most, the findings strengthen the manuscript's case for explicit unknown/fallback behavior and for evaluating metadata availability; they do not support efficacy claims. If included in the manuscript, the evidence should be framed as a negative, narrow external evaluation, with the denominator and 95%+ abstention shown beside conditional accuracy.

## Limitations and threats to validity

1. **Label quality:** one curator's manually inspected categories, with no reported inter-annotator agreement or adjudication. The labels are not universal truth.
2. **Crosswalk:** category mapping is semantic and broad. It may cause label mismatch, especially for `Travel`, household `Bills`, and grouped shopping labels. Mapping was fixed from source definitions, before predictions; it was not tuned to improve scores.
3. **Source and population:** one anonymized retail-bank stream, one country/context, repeated recurring descriptions, and strong category imbalance. Rows are not independent observations and do not represent multiple banks or customers.
4. **Text-only input:** no independent merchant ID/MCC/category metadata. Metadata-only's zero coverage reflects absent input, not an intrinsic failure of structured metadata. Combined/conflict equality is not a comparative test of their metadata behavior.
5. **Overlap/exclusions:** two rows matching one authored merchant case were removed. Rows missing text or labels and all out-of-scope labels were excluded. Description-level results omit one conflicting normalized description.
6. **Scope:** no ranking, offer eligibility, explanation comprehension, time/memory benchmark, iOS framework behavior, customer outcomes, or production deployment was tested.
7. **Privacy/licensing:** source is publicly accessible under CC BY 4.0, but is real anonymized financial data and the license does not itself prove separate rights for every embedded third-party string. Raw inputs and row-level outputs are excluded; use attribution and retain the source's rights caveat.

## Reproducibility and preservation

Run from a fresh macOS checkout with Swift 6, Python 3, and `openpyxl==3.1.5`:

```sh
curl -L 'https://data.mendeley.com/public-api/zip/dnxtg6n4rv/download/1' -o /tmp/moneydata-v1.zip
unzip -o /tmp/moneydata-v1.zip -d /tmp/moneydata-v1
python3 -m pip install openpyxl==3.1.5
Scripts/reproduce.sh \
  '/tmp/moneydata-v1/Bank Transactions Dataset/laramee26openBankTransactionData.xlsx' \
  '/path/to/ExplainableOffers-Public'
```

The checked run used Apple Swift 6.4.2, macOS 27.2.1, arm64, Python 3.12.14, and openpyxl 3.1.5. Swift release build completed in 9.96 seconds on the final run; this is a build duration only, not a classifier benchmark. The independent metric audit passed for 240 confusion rows, 8 summaries, and 40 per-class rows. No XCTest suite was added or claimed for this evaluation harness.

The original public release manifests remain intact and verified in `Results/preservation-check.txt`. This supplement is in a separate local directory. The v1.0.0 tag/release archive, original project, and submitted manuscript candidate were not changed. This directory is unpublished and must be reviewed before any external release.

## Attribution

Elif E. Firat, Dharmateja Vytla, Navya Vasudeva Singh, Zhuoqun Jiang, and Robert S. Laramee, “MoneyVis: Open Bank Transaction Data for Visualization and Beyond,” *Eurographics Visualization and Visual Analytics*, EuroVis Short Papers, 2023, DOI: [10.2312/evs.20231052](https://doi.org/10.2312/evs.20231052). Dataset: Robert Laramee, *Bank Transactions Dataset*, Mendeley Data v1, DOI: [10.17632/dnxtg6n4rv.1](https://doi.org/10.17632/dnxtg6n4rv.1), CC BY 4.0. Derived evaluation results and the category crosswalk are changes made for this supplement; source data are not redistributed.
