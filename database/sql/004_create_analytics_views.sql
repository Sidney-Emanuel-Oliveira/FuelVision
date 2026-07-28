\set ON_ERROR_STOP on

BEGIN;
SET LOCAL search_path TO fuelvision, public;

CREATE OR REPLACE VIEW product_price_summary AS
SELECT
    products.id AS product_id,
    products.name AS product,
    products.unit,
    count(*) AS observation_count,
    round(avg(observations.sale_price), 3) AS average_sale_price,
    min(observations.sale_price) AS minimum_sale_price,
    max(observations.sale_price) AS maximum_sale_price,
    max(observations.sale_price) - min(observations.sale_price) AS price_range,
    min(observations.collection_date) AS first_collection_date,
    max(observations.collection_date) AS last_collection_date
FROM price_observations AS observations
JOIN products ON products.id = observations.product_id
GROUP BY products.id, products.name, products.unit;

CREATE OR REPLACE VIEW state_price_summary AS
SELECT
    states.code AS state_code,
    states.name AS state,
    products.id AS product_id,
    products.name AS product,
    products.unit,
    count(*) AS observation_count,
    round(avg(observations.sale_price), 3) AS average_sale_price,
    min(observations.sale_price) AS minimum_sale_price,
    max(observations.sale_price) AS maximum_sale_price,
    max(observations.sale_price) - min(observations.sale_price) AS price_range
FROM price_observations AS observations
JOIN retailers ON retailers.id = observations.retailer_id
JOIN municipalities ON municipalities.id = retailers.municipality_id
JOIN states ON states.code = municipalities.state_code
JOIN products ON products.id = observations.product_id
GROUP BY states.code, states.name, products.id, products.name, products.unit;

CREATE OR REPLACE VIEW municipality_price_summary AS
SELECT
    states.code AS state_code,
    municipalities.id AS municipality_id,
    municipalities.name AS municipality,
    products.id AS product_id,
    products.name AS product,
    products.unit,
    count(*) AS observation_count,
    round(avg(observations.sale_price), 3) AS average_sale_price,
    min(observations.sale_price) AS minimum_sale_price,
    max(observations.sale_price) AS maximum_sale_price,
    max(observations.sale_price) - min(observations.sale_price) AS price_range
FROM price_observations AS observations
JOIN retailers ON retailers.id = observations.retailer_id
JOIN municipalities ON municipalities.id = retailers.municipality_id
JOIN states ON states.code = municipalities.state_code
JOIN products ON products.id = observations.product_id
GROUP BY
    states.code,
    municipalities.id,
    municipalities.name,
    products.id,
    products.name,
    products.unit;

CREATE OR REPLACE VIEW daily_price_history AS
SELECT
    observations.collection_date,
    products.id AS product_id,
    products.name AS product,
    products.unit,
    count(*) AS observation_count,
    round(avg(observations.sale_price), 3) AS average_sale_price,
    min(observations.sale_price) AS minimum_sale_price,
    max(observations.sale_price) AS maximum_sale_price,
    max(observations.sale_price) - min(observations.sale_price) AS price_range
FROM price_observations AS observations
JOIN products ON products.id = observations.product_id
GROUP BY
    observations.collection_date,
    products.id,
    products.name,
    products.unit;

COMMENT ON VIEW product_price_summary IS
    'Descriptive sale price indicators grouped by product.';
COMMENT ON VIEW state_price_summary IS
    'Descriptive sale price indicators grouped by state and product.';
COMMENT ON VIEW municipality_price_summary IS
    'Descriptive sale price indicators grouped by municipality and product.';
COMMENT ON VIEW daily_price_history IS
    'Daily descriptive sale price indicators grouped by product.';

COMMIT;
