# External evaluation protocol

Status: pre-outcome protocol for a separate, unpublished supplement. The v1.0.0 release and manuscript candidate remain unchanged.

## Dataset and decision

The selected source is Mendeley Data's *Bank Transactions Dataset* (MoneyData), version 1, DOI `10.17632/dnxtg6n4rv.1`. The repository lists CC BY 4.0. The source is an anonymized retail-bank transaction stream with a description and a `Category` field. Its companion paper distinguishes a bank-supplied transaction-type code from author-assigned spending categories. It describes the latter as manually inspected and explicitly says the taxonomy is arbitrary. We therefore treat these as external curator labels, not adjudicated or universally correct ground truth.

The data are suitable for a **narrow text-only external evaluation**: descriptions, manual category labels, sufficient category variety, and an explicit publication-compatible attribution license are available. They are not suitable for testing the structured-metadata advantage or conflict behavior because no merchant ID/MCC or independent structured spending-category signal is provided. The label column is reserved exclusively for scoring and is never passed as metadata to a classifier.

## Frozen mapping and eligibility

The crosswalk follows the source's own category descriptions. It is fixed before running any policy and does not depend on predictions:

| Source `Category` | Prototype gold |
|---|---|
| `Groceries` | groceries |
| `Dine Out` | dining |
| `Travel` | transport |
| `Amazon`, `Other Shopping`, `Clothes`, `Home Improvement` | shopping |
| `Bills` | utilities |

The source defines `Travel` as flight/train/bus tickets, `Bills` as gas/electricity/council tax/water, and the shopping labels as Amazon, clothes, gifts/shoes, and home essentials. These are defensible broad mappings but do not make the source taxonomy equivalent to the prototype taxonomy. All remaining labels are out of scope and excluded; no label is invented for them.

Only rows with both a nonempty description and source category enter preparation. Rows whose description matches any of the 36 original synthetic merchant-case names are excluded from the evaluation. Matching uses case-insensitive Unicode normalization and merchant phrase boundaries. The case catalog is read from the original public artifact; the script exports only overlap counts, not source descriptions or matched rows.

## Unchanged policies and input contract

The harness compiles byte-identical copies of the four existing policy implementations: metadata-only, token-only, metadata-first combined, and conflict-abstention. It supplies the original transaction description and sets both `merchantID` and `structuredCategory` to `nil`. All other transaction fields are fixed placeholders and are unused by classification. In particular, `Category` is held outside the `Transaction` value. No rule, alias, threshold, or mapping is tuned on this evaluation set.

With these inputs, metadata-only is expected to abstain throughout, while combined and conflict-aware reduce to the token fallback. Their equality is a protocol consequence, not an independent win. This dataset cannot test ranking: it has no offer candidates, eligibility decisions, or relevance judgments.

## Measures and units

Primary unit: eligible transaction rows, retaining repeated descriptions because the source represents transaction frequency. Secondary unit: one record per normalized description string after excluding descriptions whose source rows map to more than one prototype category. Normalization is Unicode NFKC, case folding, and whitespace collapse; punctuation is retained. Conflicting repeated descriptions remain in row-level analysis and are excluded only from the secondary case-level analysis.

All-record accuracy uses every eligible row as denominator; unknown predictions count as incorrect. Coverage is the fraction predicted as one of the five known classes; abstention rate is its complement. Classified-only accuracy uses known predictions only. Per-class precision, recall, and F1 use one-vs-rest counts over the five mapped gold classes; zero denominators yield zero. Macro-F1 is the unweighted arithmetic mean of the five class F1 values, not F1 of mean precision and recall. Confusion matrices include five gold classes by five predicted classes plus `unknown`.

No timing, ranking, customer outcome, or production metric is collected.

## Reproducibility and privacy

Dataset version and file digest are recorded in `Results/dataset-summary.json`. Swift policy source hashes are recorded in `Results/source-digests.json`. The input spreadsheet and prepared row text are kept outside this artifact directory; the reproduction script uses a temporary directory and deletes it on exit. Only aggregate confusion counts and metrics are retained. Do not publish the source spreadsheet or per-row descriptions/predictions with this supplement. Attribution and CC BY 4.0 terms must accompany any publication of derived results; the source license also cautions that third-party content may require separate permission.
