\set ON_ERROR_STOP on

BEGIN;
SET LOCAL search_path TO fuelvision, public;

CREATE TEMPORARY TABLE staging_prices (
    region_code text,
    state_code text,
    municipality text,
    retailer_name text,
    retailer_cnpj text,
    street_name text,
    street_number text,
    address_complement text,
    neighborhood text,
    postal_code text,
    product text,
    collection_date text,
    sale_price text,
    purchase_price text,
    unit text,
    brand text
) ON COMMIT DROP;
