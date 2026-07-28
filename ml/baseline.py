"""Simple reference model used to judge the first ML model."""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd


class ProductMeanBaseline:
    """Predict the training mean for each product, with a global fallback."""

    def __init__(self) -> None:
        self.product_means_: Optional[dict[str, float]] = None
        self.global_mean_: Optional[float] = None

    def fit(self, features: pd.DataFrame, target: pd.Series) -> ProductMeanBaseline:
        """Learn product and global means using training observations only."""
        self._validate_inputs(features, target)

        training_values = pd.DataFrame(
            {
                "product": features["product"].reset_index(drop=True),
                "target": target.reset_index(drop=True),
            }
        )
        self.product_means_ = {
            str(product): float(mean)
            for product, mean in training_values.groupby("product")["target"]
            .mean()
            .items()
        }
        self.global_mean_ = float(training_values["target"].mean())
        return self

    def predict(self, features: pd.DataFrame) -> np.ndarray:
        """Return one prediction per row without learning from test data."""
        if self.product_means_ is None or self.global_mean_ is None:
            raise RuntimeError("ProductMeanBaseline must be fitted before prediction")
        if "product" not in features.columns:
            raise ValueError("features must contain the product column")

        predictions = features["product"].map(self.product_means_)
        return predictions.fillna(self.global_mean_).to_numpy(dtype=float)

    @staticmethod
    def _validate_inputs(features: pd.DataFrame, target: pd.Series) -> None:
        if "product" not in features.columns:
            raise ValueError("features must contain the product column")
        if features.empty or target.empty:
            raise ValueError("features and target must not be empty")
        if len(features) != len(target):
            raise ValueError("features and target must have the same number of rows")
        if not np.isfinite(target.to_numpy(dtype=float)).all():
            raise ValueError("target must contain only finite numeric values")
