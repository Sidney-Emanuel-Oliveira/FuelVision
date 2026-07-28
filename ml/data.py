"""Loading, validation and temporal splitting for the baseline experiment."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {
    "region_code",
    "state_code",
    "product",
    "collection_date",
    "sale_price",
    "unit",
    "brand",
}
EXPECTED_UNITS = {"BRL/liter", "BRL/m3"}
CATEGORICAL_FEATURES = ["product", "region_code", "brand"]
NUMERIC_FEATURES = ["collection_day"]
TARGET_COLUMN = "sale_price"


class DataValidationError(ValueError):
    """Raised when the processed dataset cannot support a valid experiment."""


@dataclass(frozen=True)
class LoadedDataset:
    observations: pd.DataFrame
    total_rows: int
    excluded_non_liter_rows: int


@dataclass(frozen=True)
class TemporalSplit:
    train: pd.DataFrame
    test: pd.DataFrame
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    test_start: pd.Timestamp
    test_end: pd.Timestamp


def load_liquid_observations(input_path: Path) -> LoadedDataset:
    """Load the processed CSV and retain observations measured in BRL/liter."""
    if not input_path.is_file():
        raise DataValidationError(f"Processed CSV not found: {input_path}")

    try:
        frame = pd.read_csv(input_path, sep=";", dtype=str)
    except (OSError, UnicodeError, pd.errors.ParserError) as error:
        raise DataValidationError(f"Could not read processed CSV: {error}") from error

    if frame.empty:
        raise DataValidationError("Processed CSV has no observations")

    missing_columns = sorted(REQUIRED_COLUMNS.difference(frame.columns))
    if missing_columns:
        raise DataValidationError(
            "Processed CSV is missing required columns: " + ", ".join(missing_columns)
        )

    _validate_required_values(frame)
    _convert_dates_and_prices(frame)
    _validate_units(frame)

    liquid_mask = frame["unit"].eq("BRL/liter")
    liquid_observations = frame.loc[liquid_mask].copy()
    excluded_rows = int((~liquid_mask).sum())

    if liquid_observations.empty:
        raise DataValidationError("No BRL/liter observations are available")

    liquid_observations["collection_day"] = liquid_observations["collection_date"].map(
        pd.Timestamp.toordinal
    )
    liquid_observations = liquid_observations.sort_values(
        ["collection_date", "product", "state_code", "brand"],
        kind="stable",
    ).reset_index(drop=True)

    if liquid_observations["collection_date"].nunique() < 2:
        raise DataValidationError(
            "At least two distinct collection dates are required for a temporal split"
        )

    return LoadedDataset(
        observations=liquid_observations,
        total_rows=len(frame),
        excluded_non_liter_rows=excluded_rows,
    )


def temporal_train_test_split(
    observations: pd.DataFrame, test_fraction: float = 0.2
) -> TemporalSplit:
    """Split complete dates so every training row predates every test row."""
    if not 0 < test_fraction < 1:
        raise DataValidationError("test_fraction must be between 0 and 1")

    dates = sorted(observations["collection_date"].drop_duplicates().tolist())
    if len(dates) < 2:
        raise DataValidationError(
            "At least two distinct collection dates are required for a temporal split"
        )

    test_date_count = max(1, math.ceil(len(dates) * test_fraction))
    if test_date_count >= len(dates):
        test_date_count = len(dates) - 1
    test_start = dates[-test_date_count]

    train = observations.loc[observations["collection_date"] < test_start].copy()
    test = observations.loc[observations["collection_date"] >= test_start].copy()

    if train.empty or test.empty:
        raise DataValidationError("Temporal split produced an empty train or test set")
    if train["collection_date"].max() >= test["collection_date"].min():
        raise DataValidationError("Temporal leakage detected between train and test")

    return TemporalSplit(
        train=train.reset_index(drop=True),
        test=test.reset_index(drop=True),
        train_start=train["collection_date"].min(),
        train_end=train["collection_date"].max(),
        test_start=test["collection_date"].min(),
        test_end=test["collection_date"].max(),
    )


def features_and_target(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Return only the approved features and the prediction target."""
    feature_columns = CATEGORICAL_FEATURES + NUMERIC_FEATURES
    return frame.loc[:, feature_columns].copy(), frame[TARGET_COLUMN].copy()


def _validate_required_values(frame: pd.DataFrame) -> None:
    required_values = [
        "region_code",
        "state_code",
        "product",
        "collection_date",
        "sale_price",
        "unit",
        "brand",
    ]
    missing_mask = frame[required_values].isna() | frame[required_values].eq("")
    if missing_mask.any(axis=None):
        invalid_columns = sorted(missing_mask.any()[missing_mask.any()].index.tolist())
        raise DataValidationError(
            "Required values are missing in columns: " + ", ".join(invalid_columns)
        )


def _convert_dates_and_prices(frame: pd.DataFrame) -> None:
    parsed_dates = pd.to_datetime(
        frame["collection_date"], format="%Y-%m-%d", errors="coerce"
    )
    if parsed_dates.isna().any():
        raise DataValidationError("collection_date contains invalid ISO dates")

    parsed_prices = pd.to_numeric(frame["sale_price"], errors="coerce")
    if parsed_prices.isna().any() or (parsed_prices <= 0).any():
        raise DataValidationError("sale_price must contain positive numeric values")

    frame["collection_date"] = parsed_dates
    frame["sale_price"] = parsed_prices.astype(float)


def _validate_units(frame: pd.DataFrame) -> None:
    unexpected_units = sorted(set(frame["unit"]).difference(EXPECTED_UNITS))
    if unexpected_units:
        raise DataValidationError("Unexpected units: " + ", ".join(unexpected_units))
