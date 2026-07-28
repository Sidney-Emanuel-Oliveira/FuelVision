\set ON_ERROR_STOP on
SET search_path TO fuelvision, public;

DO $$
DECLARE
    base_count bigint;
BEGIN
    SELECT count(*) INTO base_count FROM price_observations;

    IF base_count = 0 THEN
        RAISE EXCEPTION 'Analytics validation requires price observations.';
    END IF;

    IF (SELECT sum(observation_count) FROM product_price_summary) <> base_count THEN
        RAISE EXCEPTION 'Product summary does not preserve the base row count.';
    END IF;

    IF (SELECT sum(observation_count) FROM state_price_summary) <> base_count THEN
        RAISE EXCEPTION 'State summary does not preserve the base row count.';
    END IF;

    IF (SELECT sum(observation_count) FROM municipality_price_summary) <> base_count THEN
        RAISE EXCEPTION 'Municipality summary does not preserve the base row count.';
    END IF;

    IF (SELECT sum(observation_count) FROM daily_price_history) <> base_count THEN
        RAISE EXCEPTION 'Daily history does not preserve the base row count.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM product_price_summary
        WHERE average_sale_price < minimum_sale_price
            OR average_sale_price > maximum_sale_price
            OR price_range <> maximum_sale_price - minimum_sale_price
    ) THEN
        RAISE EXCEPTION 'Product indicators violate their mathematical limits.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM state_price_summary
        WHERE average_sale_price < minimum_sale_price
            OR average_sale_price > maximum_sale_price
            OR price_range <> maximum_sale_price - minimum_sale_price
    ) THEN
        RAISE EXCEPTION 'State indicators violate their mathematical limits.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM municipality_price_summary
        WHERE average_sale_price < minimum_sale_price
            OR average_sale_price > maximum_sale_price
            OR price_range <> maximum_sale_price - minimum_sale_price
    ) THEN
        RAISE EXCEPTION 'Municipality indicators violate their mathematical limits.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM daily_price_history
        WHERE average_sale_price < minimum_sale_price
            OR average_sale_price > maximum_sale_price
            OR price_range <> maximum_sale_price - minimum_sale_price
    ) THEN
        RAISE EXCEPTION 'Daily indicators violate their mathematical limits.';
    END IF;

    IF EXISTS (
        (
            SELECT
                product_id,
                observation_count,
                average_sale_price,
                minimum_sale_price,
                maximum_sale_price,
                first_collection_date,
                last_collection_date
            FROM product_price_summary
            EXCEPT
            SELECT
                product_id,
                count(*),
                round(avg(sale_price), 3),
                min(sale_price),
                max(sale_price),
                min(collection_date),
                max(collection_date)
            FROM price_observations
            GROUP BY product_id
        )
        UNION ALL
        (
            SELECT
                product_id,
                count(*),
                round(avg(sale_price), 3),
                min(sale_price),
                max(sale_price),
                min(collection_date),
                max(collection_date)
            FROM price_observations
            GROUP BY product_id
            EXCEPT
            SELECT
                product_id,
                observation_count,
                average_sale_price,
                minimum_sale_price,
                maximum_sale_price,
                first_collection_date,
                last_collection_date
            FROM product_price_summary
        )
    ) THEN
        RAISE EXCEPTION 'Product summary differs from the base observations.';
    END IF;

    IF (
        SELECT min(collection_date) FROM daily_price_history
    ) <> (
        SELECT min(collection_date) FROM price_observations
    ) OR (
        SELECT max(collection_date) FROM daily_price_history
    ) <> (
        SELECT max(collection_date) FROM price_observations
    ) THEN
        RAISE EXCEPTION 'Daily history does not preserve the date range.';
    END IF;
END;
$$;

SELECT
    'analytics_validation_passed' AS status,
    (SELECT count(*) FROM price_observations) AS validated_observations,
    (SELECT count(*) FROM product_price_summary) AS product_groups,
    (SELECT count(*) FROM state_price_summary) AS state_groups,
    (SELECT count(*) FROM municipality_price_summary) AS municipality_groups,
    (SELECT count(*) FROM daily_price_history) AS daily_groups;
