\set ON_ERROR_STOP on

BEGIN;
SET LOCAL search_path TO fuelvision, public;

CREATE TEMPORARY VIEW filtered_price_observations AS
SELECT
    observations.collection_date,
    observations.sale_price,
    products.name AS product,
    products.unit,
    states.code AS state_code,
    municipalities.name AS municipality
FROM price_observations AS observations
JOIN retailers ON retailers.id = observations.retailer_id
JOIN municipalities ON municipalities.id = retailers.municipality_id
JOIN states ON states.code = municipalities.state_code
JOIN products ON products.id = observations.product_id
WHERE (NULLIF(:'product_filter', '') IS NULL OR products.name = :'product_filter')
    AND (NULLIF(:'state_filter', '') IS NULL OR states.code = upper(:'state_filter'))
    AND (
        NULLIF(:'municipality_filter', '') IS NULL
        OR municipalities.name = upper(:'municipality_filter')
    )
    AND observations.collection_date >= COALESCE(
        NULLIF(:'start_date_filter', '')::date,
        '-infinity'::date
    )
    AND observations.collection_date <= COALESCE(
        NULLIF(:'end_date_filter', '')::date,
        'infinity'::date
    );

\echo '=== PRODUCT SUMMARY ==='
SELECT
    product,
    unit,
    count(*) AS observation_count,
    round(avg(sale_price), 3) AS average_sale_price,
    min(sale_price) AS minimum_sale_price,
    max(sale_price) AS maximum_sale_price,
    max(sale_price) - min(sale_price) AS price_range
FROM filtered_price_observations
GROUP BY product, unit
ORDER BY product;

\echo '=== STATE COMPARISON ==='
SELECT
    state_code,
    product,
    unit,
    count(*) AS observation_count,
    round(avg(sale_price), 3) AS average_sale_price,
    min(sale_price) AS minimum_sale_price,
    max(sale_price) AS maximum_sale_price
FROM filtered_price_observations
GROUP BY state_code, product, unit
ORDER BY product, average_sale_price, state_code;

\echo '=== MUNICIPALITY COMPARISON ==='
SELECT
    state_code,
    municipality,
    product,
    unit,
    count(*) AS observation_count,
    round(avg(sale_price), 3) AS average_sale_price,
    min(sale_price) AS minimum_sale_price,
    max(sale_price) AS maximum_sale_price
FROM filtered_price_observations
GROUP BY state_code, municipality, product, unit
ORDER BY product, average_sale_price, state_code, municipality;

\echo '=== DAILY HISTORY ==='
SELECT
    collection_date,
    product,
    unit,
    count(*) AS observation_count,
    round(avg(sale_price), 3) AS average_sale_price,
    min(sale_price) AS minimum_sale_price,
    max(sale_price) AS maximum_sale_price
FROM filtered_price_observations
GROUP BY collection_date, product, unit
ORDER BY collection_date, product;

COMMIT;
