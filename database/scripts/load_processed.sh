#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/database_env.sh"

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 path/to/processed.csv" >&2
    exit 2
fi

if [[ ! -f "$1" ]]; then
    echo "Processed CSV not found: $1" >&2
    exit 1
fi

PROCESSED_FILE="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
EXPECTED_HEADER="region_code;state_code;municipality;retailer_name;retailer_cnpj;street_name;street_number;address_complement;neighborhood;postal_code;product;collection_date;sale_price;purchase_price;unit;brand"
ACTUAL_HEADER="$(LC_ALL=C sed -n '1p' "${PROCESSED_FILE}")"

if [[ "${ACTUAL_HEADER}" != "${EXPECTED_HEADER}" ]]; then
    echo "Processed CSV header does not match the FuelVision contract." >&2
    exit 1
fi

PROCESSED_FILE_SQL="${PROCESSED_FILE//\'/\'\'}"

"${PSQL}" \
    --no-psqlrc \
    --set=ON_ERROR_STOP=1 \
    --file="${PROJECT_ROOT}/database/sql/002_prepare_load.sql" \
    --command="\\copy staging_prices FROM '${PROCESSED_FILE_SQL}' WITH (FORMAT csv, HEADER true, DELIMITER ';', ENCODING 'UTF8')" \
    --file="${PROJECT_ROOT}/database/sql/002_finish_load.sql"
