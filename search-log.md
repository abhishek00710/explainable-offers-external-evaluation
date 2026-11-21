# Dataset search log

Search performed for public transaction-description classification datasets with explicit licenses, category provenance, and sufficient descriptions for external evaluation. The chosen dataset and decision are documented in `report.md` and `protocol.md`.

| Source | License/access evidence | Data and label evidence | Decision |
|---|---|---|---|
| [MoneyData v1, Mendeley Data](https://data.mendeley.com/datasets/dnxtg6n4rv/1), DOI 10.17632/dnxtg6n4rv.1 | Public download; listing says CC BY 4.0 | Anonymized bank transaction descriptions and 29 category labels; related paper describes labels as manually inspected and taxonomy as arbitrary | Selected for narrow text-only evaluation; no structured merchant metadata, and no reported inter-annotator reliability. |
| [US Bank Transaction Categories v1, Hugging Face](https://huggingface.co/datasets/DoDataThings/us-bank-transaction-categories) | Dataset card lists MIT | 16,000 descriptions and 16 categories, explicitly marked synthetic | Rejected: generated synthetic labels do not meet the independent external-label requirement. |
| [Categorising Noisy Bank Transactions, GitHub](https://github.com/gbadedata/transaction-classification) | Repository has MIT license | README claims real transaction descriptions and labels, but separate data rights/provenance are not established by the code license | Rejected: insufficient verified data-license and label-provenance basis for publication use. |

## Category mapping assessment

MoneyData maps reasonably but imperfectly to the five prototype classes: Groceries→groceries, Dine Out→dining, Travel→transport, grouped retail labels→shopping, and Bills→utilities. The crosswalk is frozen in `protocol.md` and reflects source category descriptions, not classifier output. Other source labels were out of scope. The broad `Travel` and `Bills` mappings and multiple shopping source labels limit construct validity.

The selected data supports a publishable derived evaluation under the listed CC BY 4.0 terms, with attribution and indication of changes. It does not authorize redistribution of the source workbook here. Because the source is real transaction data, anonymized records should continue to be handled conservatively, and any third-party rights caveat must be retained.
