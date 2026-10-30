# Failure analysis

Validation predictions join exactly to actual labels (verifier). Errors: 6/40; see errors.csv. Exploratory slices around the data-generating boundary: [{"slice": "near-boundary", "n": 8, "errors": 3, "error_rate": 0.375}, {"slice": "far-boundary", "n": 32, "errors": 3, "error_rate": 0.09375}]. This slice was selected from knowledge of the synthetic generator and is not a confirmatory subgroup finding. Groups contain correlated observations; row-wise confidence intervals would overstate independence.

Inspect both correct and incorrect points in data.csv with predictions.csv. Generator noise offers a plausible explanation for boundary errors, but observed error concentration alone cannot distinguish label noise from an inadequate model. Annotation problems in real data would require review; none are inferred here from synthetic labels. Next: independently vary label noise and boundary nonlinearity, holding groups and evaluation fixed.
