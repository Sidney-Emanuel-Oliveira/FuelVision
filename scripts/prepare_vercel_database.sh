#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${FUELVISION_PYTHON_BIN:-${PROJECT_ROOT}/.venv/bin/python}"
VERCEL_ENV_FILE="${FUELVISION_VERCEL_ENV_FILE:-${PROJECT_ROOT}/deploy/.env.vercel}"
SAMPLE_FILE="${PROJECT_ROOT}/data/samples/precos-combustiveis-amostra.csv"
PROCESSED_NAME="precos-combustiveis-amostra__v1__processed.csv"

if [[ ! -x "${PYTHON_BIN}" ]]; then
    echo "Python environment not found: ${PYTHON_BIN}" >&2
    echo "Create .venv and install ml/requirements-dev.txt." >&2
    exit 1
fi

if [[ ! -f "${VERCEL_ENV_FILE}" ]]; then
    echo "Vercel database configuration not found: ${VERCEL_ENV_FILE}" >&2
    echo "Copy deploy/vercel.env.example to deploy/.env.vercel." >&2
    exit 1
fi

TEMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TEMP_DIR}"' EXIT

cd "${PROJECT_ROOT}"

"${PYTHON_BIN}" -m pipeline.transform_data \
    "${SAMPLE_FILE}" \
    --output-dir "${TEMP_DIR}" \
    --log-file "${TEMP_DIR}/transformation.log"

FUELVISION_ENV_FILE="${VERCEL_ENV_FILE}" \
    database/scripts/create_schema.sh
FUELVISION_ENV_FILE="${VERCEL_ENV_FILE}" \
    database/scripts/load_processed.sh "${TEMP_DIR}/${PROCESSED_NAME}"
FUELVISION_ENV_FILE="${VERCEL_ENV_FILE}" \
    database/scripts/create_analytics_views.sh
FUELVISION_ENV_FILE="${VERCEL_ENV_FILE}" \
    database/scripts/validate_analytics.sh

echo "FuelVision sample database prepared and validated."
