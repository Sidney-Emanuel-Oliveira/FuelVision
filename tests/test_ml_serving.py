from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path

import joblib
import pandas as pd
from fastapi.testclient import TestClient

from ml.artifact import ArtifactError, load_artifact, save_artifact, train_artifact
from ml.inference import ModelPredictor, PredictionInputError
from ml.inference_api import create_app


class ArtifactTests(unittest.TestCase):
    def test_trains_and_reloads_versioned_baseline_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dataset = root / "processed.csv"
            artifact_path = root / "model.joblib"
            _write_dataset(dataset)

            artifact = train_artifact(dataset)
            save_artifact(artifact, artifact_path)
            reloaded = load_artifact(artifact_path)

        metadata = reloaded["metadata"]
        self.assertEqual(metadata["model_version"], "product-mean-baseline-v1")
        self.assertEqual(metadata["model_type"], "ProductMeanBaseline")
        self.assertEqual(metadata["training_rows"], 6)
        self.assertEqual(metadata["prediction_start"], "2026-01-04")
        self.assertEqual(len(metadata["supported_products"]), 2)
        self.assertFalse(metadata["evaluation"]["ridge_beats_baseline_mae"])

    def test_refuses_to_overwrite_existing_artifact_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dataset = root / "processed.csv"
            artifact_path = root / "model.joblib"
            _write_dataset(dataset)
            artifact = train_artifact(dataset)
            save_artifact(artifact, artifact_path)

            with self.assertRaisesRegex(ArtifactError, "already exists"):
                save_artifact(artifact, artifact_path)

    def test_rejects_artifact_from_incompatible_sklearn_version(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dataset = root / "processed.csv"
            artifact_path = root / "model.joblib"
            _write_dataset(dataset)
            artifact = train_artifact(dataset)
            artifact["metadata"]["library_versions"]["scikit_learn"] = "0.0"
            joblib.dump(artifact, artifact_path)

            with self.assertRaisesRegex(ArtifactError, "runtime version"):
                load_artifact(artifact_path)


class PredictorTests(unittest.TestCase):
    def test_predicts_all_data_product_mean_with_version_information(self) -> None:
        predictor = _build_predictor()

        result = predictor.predict(" gasolina ", date(2026, 1, 4))

        self.assertEqual(result["product"], "GASOLINA")
        self.assertAlmostEqual(result["estimated_price"], 6.2)
        self.assertEqual(result["unit"], "BRL/liter")
        self.assertEqual(result["model_version"], "product-mean-baseline-v1")
        self.assertIn("não deve ser tratada", result["warning"])

    def test_rejects_unsupported_product(self) -> None:
        predictor = _build_predictor()

        with self.assertRaisesRegex(PredictionInputError, "not supported"):
            predictor.predict("GNV", date(2026, 1, 4))

    def test_rejects_date_outside_documented_horizon(self) -> None:
        predictor = _build_predictor()

        for invalid_date in (date(2026, 1, 3), date(2026, 2, 3)):
            with (
                self.subTest(invalid_date=invalid_date),
                self.assertRaisesRegex(PredictionInputError, "must be between"),
            ):
                predictor.predict("GASOLINA", invalid_date)


class InferenceApiTests(unittest.TestCase):
    def test_defers_artifact_loading_until_first_model_request(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dataset = root / "processed.csv"
            artifact_path = root / "model.joblib"
            _write_dataset(dataset)
            save_artifact(train_artifact(dataset), artifact_path)
            application = create_app(artifact_path)

            self.assertIsNone(application.state.predictor)
            with TestClient(application) as client:
                self.assertIsNone(application.state.predictor)
                response = client.get("/model-info")

            self.assertEqual(response.status_code, 200)
            self.assertIsNotNone(application.state.predictor)

    def test_exposes_model_information_and_prediction(self) -> None:
        with _client_for_test_artifact() as client:
            model_response = client.get("/model-info")
            prediction_response = client.post(
                "/predict",
                json={"product": "GASOLINA", "collectionDate": "2026-01-04"},
            )

        self.assertEqual(model_response.status_code, 200)
        self.assertEqual(
            model_response.json()["modelVersion"], "product-mean-baseline-v1"
        )
        self.assertEqual(prediction_response.status_code, 200)
        self.assertEqual(prediction_response.json()["estimatedPrice"], 6.2)

    def test_rejects_missing_field_with_schema_error(self) -> None:
        with _client_for_test_artifact() as client:
            response = client.post("/predict", json={"product": "GASOLINA"})

        self.assertEqual(response.status_code, 422)

    def test_rejects_domain_input_with_safe_client_error(self) -> None:
        with _client_for_test_artifact() as client:
            response = client.post(
                "/predict",
                json={"product": "GNV", "collectionDate": "2026-01-04"},
            )

        self.assertEqual(response.status_code, 400)
        self.assertIn("not supported", response.json()["detail"])


def _build_predictor() -> ModelPredictor:
    with tempfile.TemporaryDirectory() as directory:
        dataset = Path(directory) / "processed.csv"
        _write_dataset(dataset)
        return ModelPredictor(train_artifact(dataset))


class _client_for_test_artifact:
    def __init__(self) -> None:
        self._directory = tempfile.TemporaryDirectory()
        root = Path(self._directory.name)
        dataset = root / "processed.csv"
        self._artifact_path = root / "model.joblib"
        _write_dataset(dataset)
        save_artifact(train_artifact(dataset), self._artifact_path)
        self._client = TestClient(create_app(self._artifact_path))

    def __enter__(self) -> TestClient:
        return self._client.__enter__()

    def __exit__(self, *args: object) -> None:
        self._client.__exit__(*args)
        self._directory.cleanup()


def _write_dataset(path: Path) -> None:
    frame = pd.DataFrame(
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
    frame.to_csv(path, sep=";", index=False)


if __name__ == "__main__":
    unittest.main()
