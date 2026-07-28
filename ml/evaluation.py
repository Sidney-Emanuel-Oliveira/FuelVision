"""Regression metrics shared by the baseline and Ridge model."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, dataclass

import numpy as np
from sklearn.metrics import mean_absolute_error, root_mean_squared_error


@dataclass(frozen=True)
class RegressionMetrics:
    mae: float
    rmse: float

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


def regression_metrics(
    expected: Sequence[float], predicted: Sequence[float]
) -> RegressionMetrics:
    """Calculate MAE and RMSE after checking both arrays."""
    expected_array = np.asarray(expected, dtype=float)
    predicted_array = np.asarray(predicted, dtype=float)

    if expected_array.size == 0:
        raise ValueError("expected and predicted values must not be empty")
    if expected_array.shape != predicted_array.shape:
        raise ValueError("expected and predicted values must have the same shape")
    if not np.isfinite(expected_array).all() or not np.isfinite(predicted_array).all():
        raise ValueError("expected and predicted values must be finite")

    return RegressionMetrics(
        mae=float(mean_absolute_error(expected_array, predicted_array)),
        rmse=float(root_mean_squared_error(expected_array, predicted_array)),
    )
