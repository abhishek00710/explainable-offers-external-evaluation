# Manuscript-ready external evaluation table

**Table X. External text-only evaluation on MoneyData v1.** The external curator labels are mapped to five prototype categories using the frozen crosswalk. The primary denominator is all eligible transaction rows; unique-description analysis is secondary. `Classified-only acc.` conditions on non-abstaining predictions and must be read with coverage. Macro-F1 is the arithmetic mean of the five one-vs-rest class F1 values. `NA` means no classified cases, so conditional accuracy is undefined.

| Policy | Unit | N | Correct / N (all-record accuracy) | Coverage | Abstention | Classified-only accuracy (n) | Macro-F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Metadata-only | Transactions | 3,224 | 0 / 3,224 (0.00%) | 0.00% | 100.00% | NA (0) | 0.000 |
| Token rules | Transactions | 3,224 | 149 / 3,224 (4.62%) | 4.62% | 95.38% | 100.00% (149) | 0.128 |
| Metadata-first combined | Transactions | 3,224 | 149 / 3,224 (4.62%) | 4.62% | 95.38% | 100.00% (149) | 0.128 |
| Conflict-aware abstention | Transactions | 3,224 | 149 / 3,224 (4.62%) | 4.62% | 95.38% | 100.00% (149) | 0.128 |
| Metadata-only | Unique descriptions | 563 | 0 / 563 (0.00%) | 0.00% | 100.00% | NA (0) | 0.000 |
| Token rules | Unique descriptions | 563 | 20 / 563 (3.55%) | 3.55% | 96.45% | 100.00% (20) | 0.090 |
| Metadata-first combined | Unique descriptions | 563 | 20 / 563 (3.55%) | 3.55% | 96.45% | 100.00% (20) | 0.090 |
| Conflict-aware abstention | Unique descriptions | 563 | 20 / 563 (3.55%) | 3.55% | 96.45% | 100.00% (20) | 0.090 |

Metadata is absent for every evaluated row, so the metadata-only policy's abstention and the equality of the other three policies are consequences of the input contract. This table does not compare their behavior when structured metadata is present. MoneyData's source labels are externally assigned but not independently adjudicated; the five-way crosswalk is broad. See `report.md` and `protocol.md` before interpreting these values.

## Per-class transaction results for token rules

| Prototype category | Support | Correct predictions (TP) | Recall | F1 |
|---|---:|---:|---:|---:|
| Groceries | 492 | 17 | 3.46% | 0.067 |
| Dining | 446 | 34 | 7.62% | 0.142 |
| Transport | 246 | 20 | 8.13% | 0.150 |
| Shopping | 1,566 | 0 | 0.00% | 0.000 |
| Utilities | 474 | 78 | 16.46% | 0.283 |

The rules' precision among the few known predictions was 100% in this sample. Coverage was only 4.62%; the conditional precision/accuracy must not be presented without that denominator. The full per-class precision, recall, F1, and confusion counts are in `Results/per-class.csv` and `Results/confusion.csv`.
