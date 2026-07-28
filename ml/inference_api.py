"""FastAPI boundary for the locally persisted FuelVision estimator."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from ml.artifact import DEFAULT_ARTIFACT_PATH
from ml.inference import ModelPredictor, PredictionInputError


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
    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        configured_path = artifact_path or Path(
            os.environ.get("FUELVISION_MODEL_PATH", DEFAULT_ARTIFACT_PATH)
        )
        application.state.predictor = ModelPredictor.from_path(configured_path)
        yield
        del application.state.predictor

    application = FastAPI(
        title="FuelVision Prediction Service",
        version="1.0.0",
        description="Internal service for documented experimental estimates.",
        lifespan=lifespan,
    )

    @application.get("/model-info", response_model=ModelInfoResponse)
    def model_info(request: Request) -> dict[str, object]:
        predictor: ModelPredictor = request.app.state.predictor
        return predictor.model_info()

    @application.post("/predict", response_model=PredictionResponse)
    def predict(payload: PredictionRequest, request: Request) -> dict[str, object]:
        predictor: ModelPredictor = request.app.state.predictor
        try:
            return predictor.predict(payload.product, payload.collection_date)
        except PredictionInputError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    return application


app = create_app()
