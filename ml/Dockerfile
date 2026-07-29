FROM python:3.14-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH=/opt/venv/bin:$PATH

WORKDIR /app

COPY ml/requirements.txt ./ml/requirements.txt
RUN python -m venv /opt/venv \
    && python -m pip install --upgrade pip==26.1.2 setuptools==83.0.0 \
    && python -m pip install -r ml/requirements.txt

COPY pipeline ./pipeline
COPY ml ./ml
COPY data/samples/precos-combustiveis-amostra.csv ./data/samples/precos-combustiveis-amostra.csv

RUN python -m pipeline.transform_data \
        data/samples/precos-combustiveis-amostra.csv \
        --output-dir /generated \
        --log-file /tmp/transformation.log \
    && python -m ml.artifact \
        --input /generated/precos-combustiveis-amostra__v1__processed.csv \
        --output /generated/fuel-price-baseline-v1.joblib

FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    FUELVISION_MODEL_PATH=/app/ml/artifacts/fuel-price-baseline-v1.joblib \
    PATH=/opt/venv/bin:$PATH

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY ml ./ml
COPY --from=builder \
    /generated/fuel-price-baseline-v1.joblib \
    /app/ml/artifacts/fuel-price-baseline-v1.joblib

RUN /usr/local/bin/python -m pip install \
        --no-cache-dir \
        --upgrade \
        pip==26.1.2 \
        setuptools==83.0.0 \
    && useradd --create-home --uid 10001 fuelvision \
    && chown -R fuelvision:fuelvision /app

USER fuelvision

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=6 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/model-info', timeout=2)" || exit 1

CMD ["python", "-m", "uvicorn", "ml.inference_api:app", "--host", "0.0.0.0", "--port", "8000", "--ws", "none"]
