from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from ml.baseline import ProductMeanBaseline
from ml.data import (
    DataValidationError,
    load_liquid_observations,
    temporal_train_test_split,
)
from ml.evaluation import regression_metrics
from ml.train_evaluate import main, run_experiment


class DataPreparationTests(unittest.TestCase):
    def test_load_excludes_non_liter_rows_and_creates_collection_day(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "processed.csv"
            _write_dataset(path, include_gnv=True)

            loaded = load_liquid_observations(path)

        self.assertEqual(loaded.total_rows, 7)
        self.assertEqual(loaded.excluded_non_liter_rows, 1)
        self.assertEqual(len(loaded.observations), 6)
        self.assertEqual(set(loaded.observations["unit"]), {"BRL/liter"})
        self.assertIn("collection_day", loaded.observations.columns)

    def test_load_rejects_missing_file(self) -> None:
        with self.assertRaisesRegex(DataValidationError, "not found"):
            load_liquid_observations(Path("does-not-exist.csv"))

    def test_load_rejects_missing_required_column(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "processed.csv"
            frame = _sample_frame().drop(columns=["brand"])
            frame.to_csv(path, sep=";", index=False)

            with self.assertRaisesRegex(DataValidationError, "brand"):
                load_liquid_observations(path)

    def test_load_rejects_invalid_price(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "processed.csv"
            frame = _sample_frame()
            frame.loc[0, "sale_price"] = "invalid"
            frame.to_csv(path, sep=";", index=False)

            with self.assertRaisesRegex(DataValidationError, "sale_price"):
                load_liquid_observations(path)

    def test_load_rejects_unexpected_unit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "processed.csv"
            frame = _sample_frame()
            frame.loc[0, "unit"] = "USD/gallon"
            frame.to_csv(path, sep=";", index=False)

            with self.assertRaisesRegex(DataValidationError, "Unexpected units"):
                load_liquid_observations(path)

    def test_temporal_split_keeps_complete_dates_separate(self) -> None:
        observations = _loaded_observations()

        split = temporal_train_test_split(observations, test_fraction=0.34)

        self.assertLess(split.train_end, split.test_start)
        self.assertTrue(
            set(split.train["collection_date"]).isdisjoint(
                set(split.test["collection_date"])
            )
        )
        self.assertEqual(len(split.train), 2)
        self.assertEqual(len(split.test), 4)

    def test_temporal_split_rejects_invalid_fraction(self) -> None:
        observations = _loaded_observations()

        for fraction in (0, 1, -0.1, 1.1):
            with (
                self.subTest(fraction=fraction),
                self.assertRaisesRegex(DataValidationError, "between 0 and 1"),
            ):
                temporal_train_test_split(observations, fraction)


class BaselineAndMetricsTests(unittest.TestCase):
    def test_baseline_uses_product_mean_and_global_fallback(self) -> None:
        features = pd.DataFrame({"product": ["A", "A", "B"]})
        target = pd.Series([4.0, 6.0, 10.0])
        baseline = ProductMeanBaseline().fit(features, target)

        predictions = baseline.predict(pd.DataFrame({"product": ["A", "B", "unseen"]}))

        np.testing.assert_allclose(predictions, [5.0, 10.0, 20 / 3])

    def test_baseline_requires_fit_before_predict(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "fitted"):
            ProductMeanBaseline().predict(pd.DataFrame({"product": ["A"]}))

    def test_regression_metrics_calculates_mae_and_rmse(self) -> None:
        metrics = regression_metrics([1.0, 3.0], [2.0, 5.0])

        self.assertAlmostEqual(metrics.mae, 1.5)
        self.assertAlmostEqual(metrics.rmse, np.sqrt(2.5))


class ExperimentTests(unittest.TestCase):
    def test_experiment_reports_temporal_comparison_without_saving_model(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "processed.csv"
            _write_dataset(path)

            report = run_experiment(path, test_fraction=0.34)
            generated_files = sorted(item.name for item in Path(directory).iterdir())

        self.assertEqual(report["data"]["train_rows"], 2)
        self.assertEqual(report["data"]["test_rows"], 4)
        self.assertLess(report["data"]["train_end"], report["data"]["test_start"])
        self.assertIn("mae", report["baseline"]["test"])
        self.assertIn("rmse", report["model"]["test"])
        self.assertIn("model_beats_baseline_mae", report["comparison"])
        self.assertEqual(generated_files, ["processed.csv"])

    def test_experiment_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "processed.csv"
            _write_dataset(path)

            first = run_experiment(path, test_fraction=0.34)
            second = run_experiment(path, test_fraction=0.34)

        self.assertEqual(first, second)

    def test_cli_returns_error_for_missing_input(self) -> None:
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            exit_code = main(["--input", "missing.csv"])

        self.assertEqual(exit_code, 1)
        self.assertIn("not found", stderr.getvalue())


def _loaded_observations() -> pd.DataFrame:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "processed.csv"
        _write_dataset(path)
        return load_liquid_observations(path).observations


def _write_dataset(path: Path, include_gnv: bool = False) -> None:
    frame = _sample_frame()
    if include_gnv:
        frame.loc[len(frame)] = {
            "region_code": "SE",
            "state_code": "RJ",
            "product": "GNV",
            "collection_date": "2026-01-03",
            "sale_price": "4.50",
            "unit": "BRL/m3",
            "brand": "BRAND C",
        }
    frame.to_csv(path, sep=";", index=False)


def _sample_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["SE", "SP", "GASOLINA", "2026-01-01", "6.00", "BRL/liter", "A"],
            ["S", "PR", "ETANOL", "2026-01-01", "4.00", "BRL/liter", "B"],
            ["SE", "SP", "GASOLINA", "2026-01-02", "6.20", "BRL/liter", "A"],
            ["S", "PR", "ETANOL", "2026-01-02", "4.10", "BRL/liter", "B"],
            ["SE", "RJ", "GASOLINA", "2026-01-03", "6.40", "BRL/liter", "C"],
            ["S", "SC", "ETANOL", "2026-01-03", "4.20", "BRL/liter", "D"],
        ],
        columns=[
            "region_code",
            "state_code",
            "product",
            "collection_date",
            "sale_price",
            "unit",
            "brand",
        ],
    )


if __name__ == "__main__":
    unittest.main()
