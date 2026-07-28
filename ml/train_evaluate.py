"""Train and evaluate the Module 8 baseline experiment without saving a model."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Optional

from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from ml.baseline import ProductMeanBaseline
from ml.data import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    DataValidationError,
    features_and_target,
    load_liquid_observations,
    temporal_train_test_split,
)
from ml.evaluation import RegressionMetrics, regression_metrics

DEFAULT_TEST_FRACTION = 0.2


def build_ridge_pipeline() -> Pipeline:
    """Build an understandable preprocessing and regularized linear model."""
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_FEATURES,
            ),
            ("numeric", StandardScaler(), NUMERIC_FEATURES),
        ]
    )
    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", Ridge(alpha=1.0, solver="lsqr")),
        ]
    )


def run_experiment(
    input_path: Path, test_fraction: float = DEFAULT_TEST_FRACTION
) -> dict[str, Any]:
    """Run a deterministic temporal experiment and return a serializable report."""
    loaded = load_liquid_observations(input_path)
    split = temporal_train_test_split(loaded.observations, test_fraction)
    train_features, train_target = features_and_target(split.train)
    test_features, test_target = features_and_target(split.test)

    baseline = ProductMeanBaseline().fit(train_features, train_target)
    model = build_ridge_pipeline()
    model.fit(train_features, train_target)

    baseline_train = regression_metrics(train_target, baseline.predict(train_features))
    baseline_test = regression_metrics(test_target, baseline.predict(test_features))
    model_train = regression_metrics(train_target, model.predict(train_features))
    model_test = regression_metrics(test_target, model.predict(test_features))

    return {
        "experiment": "fuel-price-baseline-v1",
        "problem": {
            "target": "sale_price",
            "unit": "BRL/liter",
            "features": CATEGORICAL_FEATURES + NUMERIC_FEATURES,
            "prediction_scope": "individual later fuel-price observations",
        },
        "data": {
            "input": str(input_path),
            "total_rows": loaded.total_rows,
            "eligible_rows": len(loaded.observations),
            "excluded_non_liter_rows": loaded.excluded_non_liter_rows,
            "test_fraction_by_dates": test_fraction,
            "train_rows": len(split.train),
            "test_rows": len(split.test),
            "train_start": _date_text(split.train_start),
            "train_end": _date_text(split.train_end),
            "test_start": _date_text(split.test_start),
            "test_end": _date_text(split.test_end),
        },
        "baseline": {
            "name": "training product mean",
            "train": baseline_train.as_dict(),
            "test": baseline_test.as_dict(),
        },
        "model": {
            "name": "Ridge regression",
            "alpha": 1.0,
            "solver": "lsqr",
            "train": model_train.as_dict(),
            "test": model_test.as_dict(),
        },
        "comparison": _comparison(baseline_test, model_test),
        "limitations": [
            "The sample is small and does not represent the complete ANP history.",
            "Only complete dates are split, leaving very few distinct dates.",
            "GNV rows are excluded because their unit differs from BRL/liter.",
            "This experiment does not save or serve the trained model.",
        ],
    }


def _comparison(
    baseline: RegressionMetrics, model: RegressionMetrics
) -> dict[str, Any]:
    return {
        "model_beats_baseline_mae": model.mae < baseline.mae,
        "model_beats_baseline_rmse": model.rmse < baseline.rmse,
        "mae_reduction_percent": _reduction_percent(baseline.mae, model.mae),
        "rmse_reduction_percent": _reduction_percent(baseline.rmse, model.rmse),
    }


def _reduction_percent(reference: float, candidate: float) -> Optional[float]:
    if reference == 0:
        return None
    return float((reference - candidate) / reference * 100)


def _date_text(value: Any) -> str:
    return value.strftime("%Y-%m-%d")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Train and evaluate the FuelVision Module 8 baseline experiment."
    )
    parser.add_argument("--input", required=True, type=Path, help="Processed CSV path")
    parser.add_argument(
        "--test-fraction",
        type=float,
        default=DEFAULT_TEST_FRACTION,
        help="Fraction of distinct dates reserved for temporal testing",
    )
    return parser


def main(arguments: Optional[Sequence[str]] = None) -> int:
    args = _build_parser().parse_args(arguments)
    try:
        report = run_experiment(args.input, args.test_fraction)
    except (DataValidationError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
