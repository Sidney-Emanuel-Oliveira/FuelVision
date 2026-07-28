#!/usr/bin/env bash

set -euo pipefail

BACKEND_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_ROOT="$(cd "${BACKEND_ROOT}/.." && pwd)"
ENV_FILE="${FUELVISION_ENV_FILE:-${PROJECT_ROOT}/.env}"

if [[ ! -f "${ENV_FILE}" ]]; then
    echo "Configuration file not found: ${ENV_FILE}" >&2
    echo "Copy .env.example to .env and replace the example values." >&2
    exit 1
fi

set -a
# O arquivo local pertence ao desenvolvedor e deve conter somente atribuições.
# shellcheck source=/dev/null
source "${ENV_FILE}"
set +a

: "${POSTGRES_HOST:?POSTGRES_HOST is required}"
: "${POSTGRES_PORT:?POSTGRES_PORT is required}"
: "${POSTGRES_DB:?POSTGRES_DB is required}"
: "${POSTGRES_USER:?POSTGRES_USER is required}"

POSTGRES_SSLMODE="${POSTGRES_SSLMODE:-prefer}"
export SPRING_DATASOURCE_URL="jdbc:postgresql://${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}?sslmode=${POSTGRES_SSLMODE}"
export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-}"
