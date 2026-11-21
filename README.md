# Explainable Offers external dataset evaluation

This is a separate external-evaluation supplement to the Explainable Offers v1.0.0 research artifact. It does not change that release or the submitted manuscript candidate. Repository and approval status are recorded in [the publication-readiness report](publication-readiness.md).

The supplement evaluates the existing four deterministic policies against the manually categorized `Category` values in Mendeley Data's anonymized *Bank Transactions Dataset* (MoneyData), version 1 (DOI: `10.17632/dnxtg6n4rv.1`). It is a narrow text-only evaluation: the workbook has no independent merchant ID/MCC or structured spending-category field that can be given to metadata policies without leaking the target labels. Thus it assesses token rules and their no-metadata fallbacks, not the benefit of metadata-first classification. This dataset has no offer/ranking judgments, so ranking is not evaluated.

The source is CC BY 4.0. Cite the dataset and its accompanying paper and identify changes. We do not redistribute the workbook, row descriptions, or row-level predictions. The source paper reports anonymization but notes that this is real transaction data; use the temporary-input workflow and do not add raw rows to a public repository.

## Measured outcome

After a frozen category crosswalk and overlap exclusion, the evaluation contains 3,224 transaction rows and 563 unanimous unique descriptions across five mapped categories. On transaction rows, token rules classified 149/3,224 correctly (4.62% all-row accuracy and coverage), abstained on 95.38%, and had five-class macro-F1 0.128. Its 100% classified-only accuracy is conditional on only those 149 covered rows. Shopping recall was zero. Metadata-only coverage was zero because no independent metadata was supplied; combined and conflict-aware matched token-only as expected under the text-only input contract. These findings challenge broad claims about text-only alias coverage and do not measure the metadata-first benefit.

See [the external evaluation report](report.md), [the frozen protocol](protocol.md), [the manuscript-ready table](paper-table.md), and [dataset search log](search-log.md). These external results are reported separately and do not amend v1.0.0 or the submitted manuscript candidate.

## Frozen category crosswalk

| MoneyData `Category` | Prototype class | Note |
|---|---|---|
| Groceries | groceries | Source definition: supermarkets |
| Dine Out | dining | Restaurants and online food ordering |
| Travel | transport | Source includes flights, trains, and buses; broader than prototype transport |
| Amazon, Other Shopping, Clothes, Home Improvement | shopping | Retail and home goods grouped broadly |
| Bills | utilities | Source includes gas, electricity, council tax, and water |

Other source categories are out of scope. The mapping and all exclusions are frozen in [protocol.md](protocol.md).

## Reproduction

Requirements: macOS 13 or later, Git, Swift 6, Python 3, `unzip`, and the pinned packages in `requirements.txt`. Use the original research repository's immutable `v1.0.0` tag. The reproduction script checks the exact tag and refuses to run if any of the six copied classifier files differ from that release.

```sh
git clone --branch v1.0.0 \
  https://github.com/abhishek00710/explainable-offers-external-evaluation.git \
  /tmp/explainable-offers-external-evaluation
cd /tmp/explainable-offers-external-evaluation
git clone --depth 1 --branch v1.0.0 \
  https://github.com/abhishek00710/explainable-offers-research.git \
  /tmp/explainable-offers-research-v1.0.0
curl -L 'https://data.mendeley.com/public-api/zip/dnxtg6n4rv/download/1' -o /tmp/moneydata-v1.zip
unzip -o /tmp/moneydata-v1.zip -d /tmp/moneydata-v1
python3 -m venv /tmp/eo-venv
. /tmp/eo-venv/bin/activate
python -m pip install -r requirements.txt
Scripts/reproduce.sh \
  '/tmp/moneydata-v1/Bank Transactions Dataset/laramee26openBankTransactionData.xlsx' \
  '/tmp/explainable-offers-research-v1.0.0' \
  '/tmp/explainable-offers-external-results'
diff -u Results/confusion.csv /tmp/explainable-offers-external-results/confusion.csv
diff -u Results/summary.csv /tmp/explainable-offers-external-results/summary.csv
diff -u Results/per-class.csv /tmp/explainable-offers-external-results/per-class.csv
deactivate
```

The commands above download MoneyData only from the official Mendeley Data provider. The script creates a temporary mapped TSV containing descriptions and labels, sends only descriptions to the unchanged Swift classifier sources, scores against labels in the runner, then deletes the TSV. It writes new aggregate outputs and logs to the separate `/tmp/explainable-offers-external-results` directory, leaving the tracked CSV evidence untouched. Do not store the workbook or temporary TSV in a synchronized or public directory. Dataset citation, CC BY 4.0 attribution, and data-rights caveats are in [THIRD_PARTY.md](docs/THIRD_PARTY.md).

## Outputs

- `Results/dataset-summary.json`: source file hash, row/case counts, fixed crosswalk counts, exclusions, and no raw descriptions.
- `Results/confusion.csv`: aggregate counts by policy, analysis unit, gold class, and prediction.
- `Results/summary.csv`: denominators, all-record and classified-only accuracy, coverage, abstention, macro-F1.
- `Results/per-class.csv`: one-vs-rest class metrics.
- `Results/audit.log`: independent Python recalculation checks.
- `Results/reproduction.log`: successful full build, evaluation, and audit console output.
- `Results/publication-reproduction.log`: fresh-checkout reproduction using the official original v1.0.0 Git tag and Mendeley download, retained separately from the original evaluation log.
- `Results/publication-environment.txt`: toolchain record for the fresh-checkout run.
- `Results/preservation-check.txt`: integrity checks for the original release manifests and copied classifier files.
- `Results/environment.txt`: Swift, macOS, architecture, Python, and openpyxl versions for this run.
- `Results/publication-audit.txt`: disclosure, licensing, provenance, and artifact-inventory checks for this supplement.

## Scope and caveats

MoneyData is a single anonymized retail-bank stream with repeated descriptions, not a representative sample of institutions or customers. Its authors describe the spending taxonomy as arbitrary and do not report independent multi-annotator agreement. The five-class crosswalk is broad and may introduce semantic label noise. One original authored merchant case overlaps the external descriptions; the matching rows are excluded. Category imbalance is retained, not rebalanced. The dataset has no structured category or merchant ID, so metadata-only is an all-unknown baseline and the three fallback-capable policies collapse to the same text-only behavior. Results are descriptive external evidence for this rule set and dataset only; they are not evidence of customer benefit, banking-population accuracy, iOS behavior, or production performance.

See [protocol.md](protocol.md) and [report.md](report.md) for the full evaluation framing and findings.

## Provenance and licenses

The separate classifier copies are byte-identical to `artifact/Validation/Sources/OfferCore` in the original repository's `v1.0.0` release tag. The fresh reproduction command verifies this before classifying. See [provenance](docs/PROVENANCE.md), [third-party terms and attribution](docs/THIRD_PARTY.md), and the [publication-readiness report](publication-readiness.md). This repository has not been pushed; its release candidate is local and unpublished pending the author's explicit approval.
