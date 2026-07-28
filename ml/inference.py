"""Validated predictions using a loaded FuelVision model artifact."""

from __future__ import annotations

import math
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from ml.artifact import load_artifact


class PredictionInputError(ValueError):
    """Raised when an input is outside the documented model contract."""


class ModelPredictor:
    """Keep one trusted estimator in memory and validate every prediction."""

    def __init__(self, artifact: dict[str, Any]) -> None:
        self._metadata = artifact["metadata"]
        self._estimator = artifact["estimator"]

    @classmethod
    def from_path(cls, artifact_path: Path) -> ModelPredictor:
        return cls(load_artifact(artifact_path))

    def model_info(self) -> dict[str, Any]:
        evaluation = self._metadata["evaluation"]
        return {
            "model_version": self._metadata["model_version"],
            "model_type": self._metadata["model_type"],
            "unit": self._metadata["unit"],
            "supported_products": self._metadata["supported_products"],
            "training_rows": self._metadata["training_rows"],
            "training_start": self._metadata["training_start"],
            "training_end": self._metadata["training_end"],
            "prediction_start": self._metadata["prediction_start"],
            "prediction_end": self._metadata["prediction_end"],
            "evaluation_mae": evaluation["baseline_test_mae"],
            "ridge_evaluation_mae": evaluation["ridge_test_mae"],
            "ridge_beats_baseline": evaluation["ridge_beats_baseline_mae"],
            "selection_reason": self._metadata["selection_reason"],
            "warning": self._metadata["warning"],
        }

    def predict(self, product: str, collection_date: date) -> dict[str, Any]:
        normalized_product = product.strip().upper()
        supported_products = self._metadata["supported_products"]
        if normalized_product not in supported_products:
            raise PredictionInputError(
                "Product is not supported by this model version: " + normalized_product
            )

        prediction_start = date.fromisoformat(self._metadata["prediction_start"])
        prediction_end = date.fromisoformat(self._metadata["prediction_end"])
        if collection_date < prediction_start or collection_date > prediction_end:
            raise PredictionInputError(
                "collectionDate must be between "
                f"{prediction_start.isoformat()} and {prediction_end.isoformat()}"
            )

        features = pd.DataFrame({"product": [normalized_product]})
        estimated_price = float(self._estimator.predict(features)[0])
        if not math.isfinite(estimated_price) or estimated_price <= 0:
            raise RuntimeError("Model produced an invalid estimated price")

        evaluation = self._metadata["evaluation"]
        return {
            "product": normalized_product,
            "collection_date": collection_date.isoformat(),
            "estimated_price": round(estimated_price, 3),
            "unit": self._metadata["unit"],
            "model_version": self._metadata["model_version"],
            "model_type": self._metadata["model_type"],
            "trained_through": self._metadata["training_end"],
            "evaluation_mae": evaluation["baseline_test_mae"],
            "warning": self._metadata["warning"],
        }
