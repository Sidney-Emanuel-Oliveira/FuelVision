#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/database_env.sh"

"${PSQL}" \
    --no-psqlrc \
    --set=ON_ERROR_STOP=1 \
    --file="${PROJECT_ROOT}/database/sql/006_validate_analytics.sql"
