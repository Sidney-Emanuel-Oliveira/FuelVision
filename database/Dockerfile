FROM python:3.9-slim AS data-builder

WORKDIR /build

COPY pipeline ./pipeline
COPY data/samples/precos-combustiveis-amostra.csv ./data/samples/precos-combustiveis-amostra.csv

RUN python -m pipeline.transform_data \
        data/samples/precos-combustiveis-amostra.csv \
        --output-dir /generated \
        --log-file /tmp/transformation.log

FROM postgres:17-alpine

COPY database/sql /opt/fuelvision/sql
COPY database/docker/init-fuelvision.sh /docker-entrypoint-initdb.d/10-init-fuelvision.sh
COPY --from=data-builder \
    /generated/precos-combustiveis-amostra__v1__processed.csv \
    /opt/fuelvision/data/sample.csv
