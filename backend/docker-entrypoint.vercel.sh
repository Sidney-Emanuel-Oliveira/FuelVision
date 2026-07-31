#!/bin/sh
set -eu

prediction_url="${FUELVISION_PREDICTION_URL:-}"
java_bin="/opt/java/openjdk/bin/java"

# No `vercel dev`, o binding pode apontar para uma porta publicada no host.
# Dentro do contêiner, 127.0.0.1 representa o próprio backend; no Docker
# Desktop, host.docker.internal representa a máquina que publicou essa porta.
if [ "${VERCEL_ENV:-}" = "development" ] \
    && printf '%s' "$prediction_url" \
        | grep -Eq '^http://127[.]0[.]0[.]1:[0-9]+$'; then
    FUELVISION_PREDICTION_URL="$(
        printf '%s' "$prediction_url" \
            | sed 's#^http://127[.]0[.]0[.]1:#http://host.docker.internal:#'
    )"
    export FUELVISION_PREDICTION_URL
fi

if [ ! -x "$java_bin" ]; then
    echo "Java runtime not found at ${java_bin}" >&2
    exit 1
fi

exec "$java_bin" \
    -Dserver.port="${PORT:-80}" \
    -jar /app/fuelvision-backend.jar
