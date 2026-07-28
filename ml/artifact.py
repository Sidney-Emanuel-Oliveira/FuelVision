"""Train, validate and persist the estimator selected for application use."""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import tempfile
from collections.abc import Sequence
from datetime import timedelta
from pathlib import Path
from typing import Any, Optional

import joblib
import numpy as np
import pandas as pd
import sklearn

from ml.baseline import ProductMeanBaseline
from ml.data import DataValidationError, features_and_target, load_liquid_observations
from ml.train_evaluate import run_experiment

ARTIFACT_FORMAT_VERSION = 1
MODEL_VERSION = "product-mean-baseline-v1"
MODEL_TYPE = "ProductMeanBaseline"
PREDICTION_HORIZON_DAYS = 30
DEFAULT_ARTIFACT_PATH = Path("ml/artifacts/fuel-price-baseline-v1.joblib")
SELECTION_REASON = (
    "Selecionado porque obteve MAE temporal de teste menor que o Ridge no Módulo 8."
)
ESTIMATE_WARNING = (
    "Estimativa experimental baseada em uma amostra pequena e não representativa; "
    "não deve ser tratada como preço garantido."
)


class ArtifactError(ValueError):
    """Raised when a model artifact cannot be safely created or validated."""


def train_artifact(input_path: Path) -> dict[str, Any]:
    """Fit the approved baseline on all eligible rows and package its metadata."""
    evaluation = run_experiment(input_path)
    loaded = load_liquid_observations(input_path)
    features, target = features_and_target(loaded.observations)
    estimator = ProductMeanBaseline().fit(features, target)

    training_start = loaded.observations["collection_date"].min()
    training_end = loaded.observations["collection_date"].max()
    prediction_start = training_end + timedelta(days=1)
    prediction_end = training_end + timedelta(days=PREDICTION_HORIZON_DAYS)

    metadata = {
        "artifact_format_version": ARTIFACT_FORMAT_VERSION,
        "model_version": MODEL_VERSION,
        "model_type": MODEL_TYPE,
        "target": "sale_price",
        "unit": "BRL/liter",
        "required_inputs": ["product", "collection_date"],
        "supported_products": sorted(
            loaded.observations["product"].drop_duplicates().tolist()
        ),
        "training_rows": len(loaded.observations),
        "training_start": _date_text(training_start),
        "training_end": _date_text(training_end),
        "prediction_start": _date_text(prediction_start),
        "prediction_end": _date_text(prediction_end),
        "prediction_horizon_days": PREDICTION_HORIZON_DAYS,
        "selection_metric": "temporal_test_mae",
        "selection_reason": SELECTION_REASON,
        "evaluation": {
            "baseline_test_mae": evaluation["baseline"]["test"]["mae"],
            "baseline_test_rmse": evaluation["baseline"]["test"]["rmse"],
            "ridge_test_mae": evaluation["model"]["test"]["mae"],
            "ridge_test_rmse": evaluation["model"]["test"]["rmse"],
            "ridge_beats_baseline_mae": evaluation["comparison"][
                "model_beats_baseline_mae"
            ],
        },
        "library_versions": {
            "python": platform.python_version(),
            "joblib": joblib.__version__,
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
        },
        "warning": ESTIMATE_WARNING,
    }
    return {"metadata": metadata, "estimator": estimator}


def save_artifact(
    artifact: dict[str, Any], output_path: Path, overwrite: bool = False
) -> None:
    """Atomically save a trusted local artifact without accidental overwrite."""
    _validate_payload(artifact)
    if output_path.suffix != ".joblib":
        raise ArtifactError("Artifact output must use the .joblib extension")
    if output_path.exists() and not overwrite:
        raise ArtifactError(f"Artifact already exists: {output_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Optional[Path] = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix=f".{output_path.stem}-",
            suffix=".tmp",
            dir=output_path.parent,
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
        joblib.dump(artifact, temporary_path, compress=3)
        os.replace(temporary_path, output_path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def load_artifact(artifact_path: Path) -> dict[str, Any]:
    """Load an artifact produced locally by FuelVision and validate its contract."""
    if not artifact_path.is_file():
        raise ArtifactError(f"Model artifact not found: {artifact_path}")

    try:
        artifact = joblib.load(artifact_path)
    except Exception as error:
        raise ArtifactError(f"Could not load model artifact: {error}") from error

    _validate_payload(artifact)
    return artifact


def _validate_payload(artifact: Any) -> None:
    if not isinstance(artifact, dict):
        raise ArtifactError("Model artifact must be a dictionary")
    metadata = artifact.get("metadata")
    estimator = artifact.get("estimator")
    if not isinstance(metadata, dict):
        raise ArtifactError("Model artifact metadata is missing or invalid")
    if not isinstance(estimator, ProductMeanBaseline):
        raise ArtifactError("Model artifact estimator has an unexpected type")

    required_metadata = {
        "artifact_format_version",
        "model_version",
        "model_type",
        "unit",
        "supported_products",
        "training_rows",
        "training_start",
        "training_end",
        "prediction_start",
        "prediction_end",
        "evaluation",
        "library_versions",
        "selection_reason",
        "warning",
    }
    missing = sorted(required_metadata.difference(metadata))
    if missing:
        raise ArtifactError("Model artifact metadata is missing: " + ", ".join(missing))
    if metadata["artifact_format_version"] != ARTIFACT_FORMAT_VERSION:
        raise ArtifactError("Unsupported model artifact format version")
    if metadata["model_version"] != MODEL_VERSION:
        raise ArtifactError("Unexpected model version")
    if metadata["model_type"] != MODEL_TYPE:
        raise ArtifactError("Unexpected model type")

    versions = metadata["library_versions"]
    if (
        not isinstance(versions, dict)
        or versions.get("scikit_learn") != sklearn.__version__
    ):
        raise ArtifactError(
            "Artifact scikit-learn version differs from the runtime version"
        )
    products = metadata["supported_products"]
    if (
        not isinstance(products, list)
        or not products
        or not all(isinstance(product, str) and product for product in products)
    ):
        raise ArtifactError("Artifact supported products are invalid")

    evaluation = metadata["evaluation"]
    required_metrics = {
        "baseline_test_mae",
        "baseline_test_rmse",
        "ridge_test_mae",
        "ridge_test_rmse",
        "ridge_beats_baseline_mae",
    }
    if not isinstance(evaluation, dict) or required_metrics.difference(evaluation):
        raise ArtifactError("Artifact evaluation metadata is invalid")
    if not isinstance(metadata["training_rows"], int) or metadata["training_rows"] <= 0:
        raise ArtifactError("Artifact training row count is invalid")

    try:
        training_start = pd.Timestamp(metadata["training_start"])
        training_end = pd.Timestamp(metadata["training_end"])
        prediction_start = pd.Timestamp(metadata["prediction_start"])
        prediction_end = pd.Timestamp(metadata["prediction_end"])
    except (TypeError, ValueError) as error:
        raise ArtifactError("Artifact date metadata is invalid") from error
    if not training_start <= training_end < prediction_start <= prediction_end:
        raise ArtifactError("Artifact date ranges are inconsistent")


def _date_text(value: Any) -> str:
    return value.strftime("%Y-%m-%d")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Train and persist the FuelVision application estimator."
    )
    parser.add_argument("--input", required=True, type=Path, help="Processed CSV path")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_ARTIFACT_PATH,
        help="Ignored local .joblib output path",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace an existing artifact at the exact output path",
    )
    return parser


def main(arguments: Optional[Sequence[str]] = None) -> int:
    args = _build_parser().parse_args(arguments)
    try:
        artifact = train_artifact(args.input)
        save_artifact(artifact, args.output, overwrite=args.overwrite)
    except (ArtifactError, DataValidationError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    report = {"artifact": str(args.output), **artifact["metadata"]}
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
