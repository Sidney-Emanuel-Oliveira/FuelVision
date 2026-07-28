#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=backend_env.sh
source "${SCRIPT_DIR}/backend_env.sh"

exec mvn -f "${BACKEND_ROOT}/pom.xml" spring-boot:run
