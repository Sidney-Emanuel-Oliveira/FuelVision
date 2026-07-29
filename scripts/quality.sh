#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${FUELVISION_PYTHON_BIN:-${PROJECT_ROOT}/.venv/bin/python}"
WITH_POSTGRES="${1:-}"

if [[ "${WITH_POSTGRES}" != "" && "${WITH_POSTGRES}" != "--with-postgres" ]]; then
    echo "Usage: $0 [--with-postgres]" >&2
    exit 2
fi

if [[ ! -x "${PYTHON_BIN}" ]]; then
    echo "Python environment not found: ${PYTHON_BIN}" >&2
    echo "Create .venv and install ml/requirements-dev.txt." >&2
    exit 1
fi

if ! "${PYTHON_BIN}" -c 'import sys; raise SystemExit(sys.version_info < (3, 11))'; then
    echo "Python 3.11 or newer is required: ${PYTHON_BIN}" >&2
    echo "Recreate .venv with a supported Python version." >&2
    exit 1
fi

if [[ ! -d "${PROJECT_ROOT}/frontend/node_modules" ]]; then
    echo "Front-end dependencies not found. Run npm ci inside frontend/." >&2
    exit 1
fi

cd "${PROJECT_ROOT}"

"${PYTHON_BIN}" -m ruff check exploration pipeline ml tests
"${PYTHON_BIN}" -m ruff check \
    --config ml/pyproject.toml \
    ml tests/test_ml_baseline.py tests/test_ml_serving.py
"${PYTHON_BIN}" -m ruff format --check exploration pipeline ml tests

if [[ "${WITH_POSTGRES}" == "--with-postgres" ]]; then
    FUELVISION_RUN_DB_TESTS=1 "${PYTHON_BIN}" -m unittest discover -s tests -v
    backend/scripts/test.sh --with-postgres
else
    "${PYTHON_BIN}" -m unittest discover -s tests -v
    backend/scripts/test.sh
fi

mvn -f backend/pom.xml package -DskipTests

npm --prefix frontend run typecheck
npm --prefix frontend run lint
npm --prefix frontend run format:check
npm --prefix frontend test
npm --prefix frontend run build

git diff --check
