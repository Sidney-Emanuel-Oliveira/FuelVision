#!/usr/bin/env bash

set -euo pipefail

: "${POSTGRES_USER:?POSTGRES_USER is required}"
: "${POSTGRES_DB:?POSTGRES_DB is required}"
: "${FUELVISION_DB_USER:?FUELVISION_DB_USER is required}"
: "${FUELVISION_DB_PASSWORD:?FUELVISION_DB_PASSWORD is required}"

psql \
    --no-psqlrc \
    --set=ON_ERROR_STOP=1 \
    --set=app_user="${FUELVISION_DB_USER}" \
    --set=app_password="${FUELVISION_DB_PASSWORD}" \
    --set=app_database="${POSTGRES_DB}" \
    --username="${POSTGRES_USER}" \
    --dbname="${POSTGRES_DB}" \
    --file=/opt/fuelvision/sql/docker_create_role.sql

export PGPASSWORD="${FUELVISION_DB_PASSWORD}"
APP_PSQL=(
    psql
    --no-psqlrc
    --set=ON_ERROR_STOP=1
    --username="${FUELVISION_DB_USER}"
    --dbname="${POSTGRES_DB}"
)

"${APP_PSQL[@]}" --file=/opt/fuelvision/sql/001_create_schema.sql
"${APP_PSQL[@]}" \
    --file=/opt/fuelvision/sql/002_prepare_load.sql \
    --command="\copy staging_prices FROM '/opt/fuelvision/data/sample.csv' WITH (FORMAT csv, HEADER true, DELIMITER ';', ENCODING 'UTF8')" \
    --file=/opt/fuelvision/sql/002_finish_load.sql
"${APP_PSQL[@]}" --file=/opt/fuelvision/sql/004_create_analytics_views.sql
