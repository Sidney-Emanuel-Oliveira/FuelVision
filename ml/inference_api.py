"""FastAPI boundary for the locally persisted FuelVision estimator."""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path
from threading import Lock
from typing import TYPE_CHECKING, Optional

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from ml.inference import ModelPredictor

DEFAULT_MODEL_PATH = Path("ml/artifacts/fuel-price-baseline-v1.joblib")


def _to_camel(name: str) -> str:
    first, *remaining = name.split("_")
    return first + "".join(part.capitalize() for part in remaining)


class ApiModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=_to_camel,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class PredictionRequest(ApiModel):
    product: str = Field(min_length=1, max_length=40)
    collection_date: date


class PredictionResponse(ApiModel):
    product: str
    collection_date: date
    estimated_price: float
    unit: str
    model_version: str
    model_type: str
    trained_through: date
    evaluation_mae: float
    warning: str


class ModelInfoResponse(ApiModel):
    model_version: str
    model_type: str
    unit: str
    supported_products: list[str]
    training_rows: int
    training_start: date
    training_end: date
    prediction_start: date
    prediction_end: date
    evaluation_mae: float
    ridge_evaluation_mae: float
    ridge_beats_baseline: bool
    selection_reason: str
    warning: str


def create_app(artifact_path: Optional[Path] = None) -> FastAPI:
    application = FastAPI(
        title="FuelVision Prediction Service",
        version="1.0.0",
        description="Internal service for documented experimental estimates.",
    )
    application.state.artifact_path = artifact_path or Path(
        os.environ.get("FUELVISION_MODEL_PATH", DEFAULT_MODEL_PATH)
    )
    application.state.predictor = None
    application.state.predictor_lock = Lock()

    @application.get("/model-info", response_model=ModelInfoResponse)
    def model_info(request: Request) -> dict[str, object]:
        predictor = _get_predictor(request)
        return predictor.model_info()

    @application.post("/predict", response_model=PredictionResponse)
    def predict(payload: PredictionRequest, request: Request) -> dict[str, object]:
        from ml.inference import PredictionInputError

        predictor = _get_predictor(request)
        try:
            return predictor.predict(payload.product, payload.collection_date)
        except PredictionInputError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    return application


def _get_predictor(request: Request) -> ModelPredictor:
    predictor = request.app.state.predictor
    if predictor is not None:
        return predictor

    with request.app.state.predictor_lock:
        predictor = request.app.state.predictor
        if predictor is None:
            from ml.inference import ModelPredictor

            predictor = ModelPredictor.from_path(request.app.state.artifact_path)
            request.app.state.predictor = predictor
        return predictor


app = create_app()
