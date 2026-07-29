#!/usr/bin/env bash

set -euo pipefail

BASE_URL="${1:-}"

if [[ -z "${BASE_URL}" ]]; then
    echo "Usage: $0 <base-url>" >&2
    echo "Example: $0 https://fuelvision.example.com" >&2
    exit 2
fi

if [[ ! "${BASE_URL}" =~ ^https?://[^/]+$ ]]; then
    echo "The base URL must include http:// or https:// and no path." >&2
    exit 2
fi

CURL=(curl --fail --silent --show-error --connect-timeout 5 --max-time 20)

"${CURL[@]}" "${BASE_URL}/" >/dev/null
"${CURL[@]}" "${BASE_URL}/api/prices/summary" >/dev/null
"${CURL[@]}" "${BASE_URL}/api/predictions/model" >/dev/null
"${CURL[@]}" \
    --request POST \
    --header "Content-Type: application/json" \
    --data '{"product":"GASOLINA COMUM","collectionDate":"2026-01-03"}' \
    "${BASE_URL}/api/predictions" >/dev/null

echo "deployment_smoke_passed base_url=${BASE_URL}"
