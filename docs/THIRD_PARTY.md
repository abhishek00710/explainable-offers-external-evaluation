# Third-party materials, licensing, and attribution

## Research code

The original classifier source copies, evaluation harness authored for this supplement, scripts, protocol, and documentation authored by Abhishek Gang Deb are provided under Apache License 2.0; see the repository `LICENSE` and `NOTICE`. The original classifier source is also available in the original research repository's Apache-2.0 `v1.0.0` release. This license does not grant rights to Apple SDKs or frameworks, trademarks, or third-party materials.

## MoneyData v1

Source: Robert S. Laramee, *Bank Transactions Dataset*, Mendeley Data, version 1, DOI [10.17632/dnxtg6n4rv.1](https://doi.org/10.17632/dnxtg6n4rv.1). The provider lists the dataset under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).

Attribution for derived evaluation results:

> Laramee, Robert S. *Bank Transactions Dataset*, Mendeley Data, v1, 2026, https://doi.org/10.17632/dnxtg6n4rv.1. Licensed under CC BY 4.0. The category crosswalk, exclusions, and aggregate evaluation results are changes made for this supplement.

The workbook is not redistributed. This repository includes only aggregate counts and metrics derived from the dataset, not transaction descriptions or row-level predictions. The source license states that third-party content embedded in a dataset may require separate permissions. CC BY 4.0 is the provider's stated license; it is not a representation that every string in the underlying anonymized financial records is free of other rights or privacy restrictions. The source dataset is real transaction data described by its authors as anonymized. Do not add raw rows or row-level outputs to this repository.

## Related source paper

Elif E. Firat, Dharmateja Vytla, Navya Vasudeva Singh, Zhuoqun Jiang, and Robert S. Laramee, “MoneyVis: Open Bank Transaction Data for Visualization and Beyond,” *Eurographics Visualization and Visual Analytics (EuroVis) Short Papers*, 2023, DOI [10.2312/evs.20231052](https://doi.org/10.2312/evs.20231052). Cite this paper for the dataset's anonymization and category-provenance discussion. Its authors say their manual category assignment is arbitrary and other taxonomies are possible; the report therefore treats those labels as external curator labels rather than definitive truth.

## Apple frameworks

The prototype uses Apple's NaturalLanguage framework and other SDK-provided APIs available in the macOS toolchain. No Apple framework implementation or SDK is included in this repository. Apple's terms, framework availability, and supported-platform behavior remain governed by Apple; this repository's Apache license does not apply to them. No iOS performance claim is made.

## Reproduction-only Python dependencies

`requirements.txt` pins `openpyxl==3.1.5` and its `et-xmlfile==2.0.0` dependency for reading the source workbook. Both installed package metadata records identify the MIT License. Neither dependency is vendored in this repository; they are installed into the user's Python environment during reproduction and remain subject to their respective upstream MIT license notices. The metric auditor and publication scan use the Python standard library.
