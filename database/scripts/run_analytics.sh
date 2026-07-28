#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PRODUCT_FILTER=""
STATE_FILTER=""
MUNICIPALITY_FILTER=""
START_DATE_FILTER=""
END_DATE_FILTER=""

show_usage() {
    echo "Usage: $0 [--product NAME] [--state UF] [--municipality NAME]" \
        "[--start-date YYYY-MM-DD] [--end-date YYYY-MM-DD]"
}

while [[ $# -gt 0 ]]; do
    if [[ "$1" == "--help" ]]; then
        show_usage
        exit 0
    fi
    if [[ $# -lt 2 ]]; then
        echo "Missing value for option: $1" >&2
        show_usage >&2
        exit 2
    fi
    case "$1" in
        --product) PRODUCT_FILTER="$2" ;;
        --state) STATE_FILTER="$2" ;;
        --municipality) MUNICIPALITY_FILTER="$2" ;;
        --start-date) START_DATE_FILTER="$2" ;;
        --end-date) END_DATE_FILTER="$2" ;;
        *)
            echo "Unknown option: $1" >&2
            show_usage >&2
            exit 2
            ;;
    esac
    shift 2
done

source "${SCRIPT_DIR}/database_env.sh"

"${PSQL}" \
    --no-psqlrc \
    --set=ON_ERROR_STOP=1 \
    --set="product_filter=${PRODUCT_FILTER}" \
    --set="state_filter=${STATE_FILTER}" \
    --set="municipality_filter=${MUNICIPALITY_FILTER}" \
    --set="start_date_filter=${START_DATE_FILTER}" \
    --set="end_date_filter=${END_DATE_FILTER}" \
    --file="${PROJECT_ROOT}/database/sql/005_analysis_report.sql"
