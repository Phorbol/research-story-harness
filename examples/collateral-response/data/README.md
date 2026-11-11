# Data used in this example

`collateral.csv` preserves 900 values from S1 Data, worksheet Figure1, B7:BI21. Each selecting drug has four independent evolved populations, with one single-colony isolate per population. Testing equals selecting identifies 60 direct responses; excluding them leaves 840 collateral values and 210 directed drug pairs.

`pairs.csv` describes the four source signs per directed pair. The five counts (25, 37, 51, 90, 7) are a descriptive reclassification for this visualization, not these statistics quoted verbatim from the original paper. `source-map.json` records exact workbook cells, drug names, source zero definition and transformation scope.

Zero is the source threshold: the absolute IC50 difference did not exceed three ancestral standard errors. It is not missing data, and does not prove absence of biological change. The other values are log2(IC50_mutant / IC50_ancestor). No additional significance test, error bar, future probability or clinical claim is introduced.

The full 15-drug map uses the s017 workbook order; column order from another supplementary table must not be substituted. See the normal figure captions and source attribution.
