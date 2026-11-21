# Publication readiness report

**Candidate:** `explainable-offers-external-evaluation`, intended GitHub owner `abhishek00710`  
**Report scope:** snapshot immediately before public-release approval  
**Visibility:** private GitHub repository created empty; publication approval is pending  
**Current release state:** local-only source commit and annotated `v1.0.0` tag; no push or GitHub release publication has occurred  
**Related original release:** `abhishek00710/explainable-offers-research`, tag `v1.0.0`, source commit `ca33e4c59510dd632482b8a5bfa2512af67e3d3f`

## Post-approval publication status

This addendum records the later publication outcome; the pre-approval audit snapshot below is retained as historical evidence. After the author's explicit approval, the repository was made public and the prepared `main` branch and annotated `v1.0.0` tag were pushed.

- Public repository: <https://github.com/abhishek00710/explainable-offers-external-evaluation>
- Initial public-release commit (also the `v1.0.0` target): `0c4554c91928891b9e0f6a0274b1a83901bdda79`
- `v1.0.0` points to that same commit: `0c4554c91928891b9e0f6a0274b1a83901bdda79`
- Tag message: “External MoneyData evaluation supplement; reproducible aggregate results and negative findings.”
- No GitHub Release page was created; the versioned Git tag is available at <https://github.com/abhishek00710/explainable-offers-external-evaluation/tree/v1.0.0>.
- The original `abhishek00710/explainable-offers-research` repository and its `v1.0.0` tag were not modified.

The checks and measurements in this report describe the frozen supplement package. The publication action changed repository visibility and uploaded the prepared commit/tag; it did not rerun or alter the evaluation.


## Completed checks

| Check | Result | Evidence |
|---|---|---|
| Separate supplement contents | Pass | Swift evaluation runner, four unchanged policy copies, Python preparation/audit/scanning scripts, fixed protocol and crosswalk, report, search log, manuscript table, aggregate CSVs, license/notice, provenance and attribution docs. |
| Original policy provenance | Pass | Fresh clone at the official original tag identified the expected commit; `Scripts/reproduce.sh` byte-compared all six policy files successfully. Source SHA-256 values are in `Results/source-digests.json`. |
| Original v1.0.0 preservation | Pass | Original repository result manifests verified 46/46 and 62/62; see `Results/preservation-check.txt`. No changes were made to that repository or tag. |
| Frozen measurements | Pass | Reproduction from the official dataset download and original release tag exactly matched all three frozen metric CSVs (`confusion.csv`, `summary.csv`, `per-class.csv`). |
| Metric audit | Pass | Independent Python recalculation passed for confusion totals, denominators, all-record and classified-only accuracy, coverage, abstention, per-class precision/recall/F1, and arithmetic five-class macro-F1; see `Results/audit.log`. |
| macOS reproduction | Pass | Swift 6.4.2 release build and run completed on macOS 27.2.1 arm64 with Python 3.9.6, openpyxl 3.1.5, and et-xmlfile 2.0.0. The final fresh-tag-checkout run reported 10.11 seconds to build; this is build time only, not a runtime benchmark. Full output is `Results/publication-reproduction.log`; environment is in `Results/publication-environment.txt`. |
| Disclosure scan | Pass, pattern-based | `Scripts/publication_scan.py` scanned 36 files and found no personal home paths, credential-like patterns, email addresses, unreviewed URLs, or workbook/raw row-export file extensions; see `Results/publication-audit.txt`. Manual review found only author identity and approved public source URLs. |
| Raw data handling | Pass | Workbook and temporary mapped TSV are absent from the candidate. The evaluation runner exports aggregates only; temporary row text is removed on exit. |
| Third-party notices | Pass with residual caveat | MoneyData v1 DOI and CC BY 4.0 attribution/changes notice, source-paper DOI, third-party-rights caveat, and Apple SDK boundary are documented in `docs/THIRD_PARTY.md`. No third-party code package is vendored. |
| XCTest status | Not applicable to this harness | This supplement package has no XCTest target. The checks above are the executed build, fresh reproduction, and independent aggregate-metric audit; no XCTest result is claimed. |

## Dataset and findings to disclose

MoneyData v1 (DOI `10.17632/dnxtg6n4rv.1`) is the only selected external dataset. Its provider lists CC BY 4.0. The source paper (DOI `10.2312/evs.20231052`) describes anonymization, manual category assignment, and an arbitrary taxonomy. Attribute the source, link the license, identify the crosswalk/exclusion/derived results as changes, and retain the warning that the provider's license does not settle all possible third-party rights in underlying transaction strings. The workbook is excluded from the repository.

The frozen results cover 3,224 rows and 563 unanimous unique descriptions. Token rules classified 149/3,224 transaction rows correctly (4.62% all-row accuracy and coverage), abstained on 95.38%, and had macro-F1 0.128. Shopping recall was zero. Metadata-only coverage is zero because independent structured metadata is absent; combined and conflict-aware equal token-only for this text-only input. The report retains these unfavorable results and makes no production, iOS, customer-outcome, or IEEE-acceptance claims.

## Reproduction commands

From a fresh macOS checkout after the candidate repository is made available:

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

The original classifier was cloned from its official public GitHub tag, and the dataset was downloaded from Mendeley. The final supplement package was checked out from its local annotated `v1.0.0` tag into a clean directory because the newly created GitHub repository remains empty and private pending approval. From that clean checkout, the six-file source guard, Swift build/evaluation, independent audit, and aggregate CSV comparisons passed. The command that clones the supplement from GitHub itself cannot be exercised until the author approves a push and public visibility. The new console log is retained separately so the earlier evaluation log and measurements remain untouched.

## Remaining risks and publication conditions

1. **Dataset rights/privacy:** MoneyData is anonymized real financial data. Public access and CC BY 4.0 are documented by the provider, but third-party content or privacy rights may still apply. Do not add workbook rows, row-level predictions, or description-bearing temporary files.
2. **Label validity:** source categories are manually curated, described as arbitrary, and have no reported independent adjudication/inter-rater agreement. The frozen crosswalk is broad and may create semantic label noise.
3. **Scope:** this is one text-only dataset, not an evaluation of metadata-first behavior, ranking, iOS, production deployment, or customer outcomes.
4. **Reproduction environment:** recorded timing is limited to the specific macOS 27.2.1 arm64 machine and reports build time only.
5. **Release boundary:** public visibility and pushing the local commit/tag are deliberately uncompleted until explicit author approval.

## Proposed publication steps (not executed)

After the author explicitly approves public release:

1. In GitHub, open **Settings → General → Danger Zone → Change repository visibility → Public** for `abhishek00710/explainable-offers-external-evaluation`.
2. From this prepared local repository, push the branch and release tag:

```sh
git push --set-upstream origin main
git push origin refs/tags/v1.0.0
```

The GitHub CLI is not installed in this environment, so visibility would be changed in the repository settings UI. These visibility and push steps are deliberately unexecuted. The current candidate remains private and empty on GitHub; the local commit and tag are not pushed. No GitHub release page has been created.
