#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

case "${1:-}" in
    "")
        exec mvn -f "${BACKEND_ROOT}/pom.xml" test
        ;;
    --with-postgres)
        # shellcheck source=backend_env.sh
        source "${SCRIPT_DIR}/backend_env.sh"
        export FUELVISION_RUN_DB_TESTS=1
        exec mvn -f "${BACKEND_ROOT}/pom.xml" test
        ;;
    *)
        echo "Usage: $0 [--with-postgres]" >&2
        exit 2
        ;;
esac
