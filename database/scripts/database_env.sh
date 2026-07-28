#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${FUELVISION_ENV_FILE:-${PROJECT_ROOT}/.env}"

if [[ ! -f "${ENV_FILE}" ]]; then
    echo "Configuration file not found: ${ENV_FILE}" >&2
    echo "Copy .env.example to .env and replace the example values." >&2
    exit 1
fi

set -a
# The local file is controlled by the developer and must contain only assignments.
source "${ENV_FILE}"
set +a

: "${POSTGRES_HOST:?POSTGRES_HOST is required}"
: "${POSTGRES_PORT:?POSTGRES_PORT is required}"
: "${POSTGRES_DB:?POSTGRES_DB is required}"
: "${POSTGRES_USER:?POSTGRES_USER is required}"
: "${POSTGRES_SSLMODE:?POSTGRES_SSLMODE is required}"

export PGHOST="${POSTGRES_HOST}"
export PGPORT="${POSTGRES_PORT}"
export PGDATABASE="${POSTGRES_DB}"
export PGUSER="${POSTGRES_USER}"
export PGPASSWORD="${POSTGRES_PASSWORD:-}"
export PGSSLMODE="${POSTGRES_SSLMODE}"

if [[ -n "${POSTGRES_BIN:-}" ]]; then
    PSQL="${POSTGRES_BIN}/psql"
else
    PSQL="$(command -v psql || true)"
fi

if [[ -z "${PSQL}" || ! -x "${PSQL}" ]]; then
    echo "psql was not found. Install PostgreSQL or set POSTGRES_BIN." >&2
    exit 1
fi
