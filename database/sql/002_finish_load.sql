\set ON_ERROR_STOP on

SET LOCAL search_path TO fuelvision, public;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM staging_prices) THEN
        RAISE EXCEPTION 'Processed CSV has no data rows.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM staging_prices
        GROUP BY retailer_cnpj, product, collection_date
        HAVING count(*) > 1
    ) THEN
        RAISE EXCEPTION 'Processed CSV contains a duplicated business key.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM staging_prices
        GROUP BY retailer_cnpj
        HAVING count(DISTINCT ROW(
            retailer_name,
            street_name,
            street_number,
            address_complement,
            neighborhood,
            postal_code,
            brand,
            state_code,
            municipality
        )) > 1
    ) THEN
        RAISE EXCEPTION 'Processed CSV contains conflicting retailer data.';
    END IF;
END;
$$;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM staging_prices AS source
        LEFT JOIN states ON states.code = source.state_code
        LEFT JOIN products
            ON products.name = source.product
            AND products.unit = source.unit
        WHERE states.code IS NULL
            OR states.region_code <> source.region_code
            OR products.id IS NULL
    ) THEN
        RAISE EXCEPTION 'Processed CSV contains an unknown state, region, product or unit.';
    END IF;
END;
$$;

INSERT INTO municipalities (state_code, name)
SELECT DISTINCT state_code, municipality
FROM staging_prices
ON CONFLICT (state_code, name) DO NOTHING;

INSERT INTO retailers (
    cnpj,
    name,
    street_name,
    street_number,
    address_complement,
    neighborhood,
    postal_code,
    brand,
    municipality_id
)
SELECT DISTINCT
    source.retailer_cnpj,
    source.retailer_name,
    source.street_name,
    source.street_number,
    NULLIF(source.address_complement, ''),
    source.neighborhood,
    source.postal_code,
    source.brand,
    municipalities.id
FROM staging_prices AS source
JOIN municipalities
    ON municipalities.state_code = source.state_code
    AND municipalities.name = source.municipality
ON CONFLICT (cnpj) DO UPDATE
SET name = EXCLUDED.name,
    street_name = EXCLUDED.street_name,
    street_number = EXCLUDED.street_number,
    address_complement = EXCLUDED.address_complement,
    neighborhood = EXCLUDED.neighborhood,
    postal_code = EXCLUDED.postal_code,
    brand = EXCLUDED.brand,
    municipality_id = EXCLUDED.municipality_id,
    updated_at = CURRENT_TIMESTAMP
WHERE ROW(
    retailers.name,
    retailers.street_name,
    retailers.street_number,
    retailers.address_complement,
    retailers.neighborhood,
    retailers.postal_code,
    retailers.brand,
    retailers.municipality_id
) IS DISTINCT FROM ROW(
    EXCLUDED.name,
    EXCLUDED.street_name,
    EXCLUDED.street_number,
    EXCLUDED.address_complement,
    EXCLUDED.neighborhood,
    EXCLUDED.postal_code,
    EXCLUDED.brand,
    EXCLUDED.municipality_id
);

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM staging_prices AS source
        JOIN retailers ON retailers.cnpj = source.retailer_cnpj
        JOIN products ON products.name = source.product
        JOIN price_observations AS existing
            ON existing.retailer_id = retailers.id
            AND existing.product_id = products.id
            AND existing.collection_date = source.collection_date::date
        WHERE existing.sale_price <> source.sale_price::numeric
            OR existing.purchase_price IS DISTINCT FROM
                NULLIF(source.purchase_price, '')::numeric
    ) THEN
        RAISE EXCEPTION 'Database contains a conflicting price observation.';
    END IF;
END;
$$;

INSERT INTO price_observations (
    retailer_id,
    product_id,
    collection_date,
    sale_price,
    purchase_price
)
SELECT
    retailers.id,
    products.id,
    source.collection_date::date,
    source.sale_price::numeric(10, 3),
    NULLIF(source.purchase_price, '')::numeric(10, 3)
FROM staging_prices AS source
JOIN retailers ON retailers.cnpj = source.retailer_cnpj
JOIN products
    ON products.name = source.product
    AND products.unit = source.unit
ON CONFLICT (retailer_id, product_id, collection_date) DO NOTHING;

SELECT
    (SELECT count(*) FROM staging_prices) AS source_rows,
    (SELECT count(*) FROM price_observations) AS total_observations;

COMMIT;
