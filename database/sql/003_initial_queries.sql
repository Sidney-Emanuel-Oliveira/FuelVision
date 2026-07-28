\set ON_ERROR_STOP on
SET search_path TO fuelvision, public;

SELECT 'regions' AS table_name, count(*) AS row_count FROM regions
UNION ALL
SELECT 'states', count(*) FROM states
UNION ALL
SELECT 'municipalities', count(*) FROM municipalities
UNION ALL
SELECT 'products', count(*) FROM products
UNION ALL
SELECT 'retailers', count(*) FROM retailers
UNION ALL
SELECT 'price_observations', count(*) FROM price_observations
ORDER BY table_name;

SELECT
    observations.collection_date,
    states.code AS state_code,
    municipalities.name AS municipality,
    products.name AS product,
    observations.sale_price,
    products.unit,
    retailers.cnpj AS retailer_cnpj,
    retailers.name AS retailer_name
FROM price_observations AS observations
JOIN retailers ON retailers.id = observations.retailer_id
JOIN municipalities ON municipalities.id = retailers.municipality_id
JOIN states ON states.code = municipalities.state_code
JOIN products ON products.id = observations.product_id
ORDER BY observations.collection_date, states.code, products.name, retailers.cnpj
LIMIT 10;
