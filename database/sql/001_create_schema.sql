\set ON_ERROR_STOP on

BEGIN;

CREATE SCHEMA IF NOT EXISTS fuelvision;
SET LOCAL search_path TO fuelvision, public;

CREATE TABLE IF NOT EXISTS regions (
    code varchar(2) PRIMARY KEY,
    name varchar(20) NOT NULL UNIQUE,
    CONSTRAINT regions_code_check CHECK (code IN ('N', 'NE', 'CO', 'SE', 'S'))
);

CREATE TABLE IF NOT EXISTS states (
    code char(2) PRIMARY KEY,
    name varchar(30) NOT NULL UNIQUE,
    region_code varchar(2) NOT NULL,
    CONSTRAINT states_region_fk
        FOREIGN KEY (region_code) REFERENCES regions (code),
    CONSTRAINT states_code_format_check CHECK (code ~ '^[A-Z]{2}$')
);

CREATE TABLE IF NOT EXISTS municipalities (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    state_code char(2) NOT NULL,
    name varchar(120) NOT NULL,
    CONSTRAINT municipalities_state_fk
        FOREIGN KEY (state_code) REFERENCES states (code),
    CONSTRAINT municipalities_state_name_uk UNIQUE (state_code, name),
    CONSTRAINT municipalities_name_not_blank CHECK (btrim(name) <> '')
);

CREATE TABLE IF NOT EXISTS products (
    id smallint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name varchar(40) NOT NULL UNIQUE,
    unit varchar(10) NOT NULL,
    CONSTRAINT products_name_not_blank CHECK (btrim(name) <> ''),
    CONSTRAINT products_unit_check CHECK (unit IN ('BRL/liter', 'BRL/m3'))
);

CREATE TABLE IF NOT EXISTS retailers (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cnpj char(14) NOT NULL UNIQUE,
    name varchar(180) NOT NULL,
    street_name varchar(180) NOT NULL,
    street_number varchar(30) NOT NULL,
    address_complement varchar(120),
    neighborhood varchar(120) NOT NULL,
    postal_code char(8) NOT NULL,
    brand varchar(80) NOT NULL,
    municipality_id bigint NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT retailers_municipality_fk
        FOREIGN KEY (municipality_id) REFERENCES municipalities (id),
    CONSTRAINT retailers_cnpj_format_check CHECK (cnpj ~ '^[0-9]{14}$'),
    CONSTRAINT retailers_postal_code_format_check CHECK (postal_code ~ '^[0-9]{8}$'),
    CONSTRAINT retailers_name_not_blank CHECK (btrim(name) <> ''),
    CONSTRAINT retailers_street_name_not_blank CHECK (btrim(street_name) <> ''),
    CONSTRAINT retailers_street_number_not_blank CHECK (btrim(street_number) <> ''),
    CONSTRAINT retailers_neighborhood_not_blank CHECK (btrim(neighborhood) <> ''),
    CONSTRAINT retailers_brand_not_blank CHECK (btrim(brand) <> '')
);

CREATE TABLE IF NOT EXISTS price_observations (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    retailer_id bigint NOT NULL,
    product_id smallint NOT NULL,
    collection_date date NOT NULL,
    sale_price numeric(10, 3) NOT NULL,
    purchase_price numeric(10, 3),
    loaded_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT price_observations_retailer_fk
        FOREIGN KEY (retailer_id) REFERENCES retailers (id),
    CONSTRAINT price_observations_product_fk
        FOREIGN KEY (product_id) REFERENCES products (id),
    CONSTRAINT price_observations_business_key_uk
        UNIQUE (retailer_id, product_id, collection_date),
    CONSTRAINT price_observations_sale_price_check CHECK (sale_price > 0),
    CONSTRAINT price_observations_purchase_price_check
        CHECK (purchase_price IS NULL OR purchase_price > 0)
);

CREATE INDEX IF NOT EXISTS price_observations_collection_date_idx
    ON price_observations (collection_date);

CREATE INDEX IF NOT EXISTS price_observations_product_date_idx
    ON price_observations (product_id, collection_date);

INSERT INTO regions (code, name)
VALUES
    ('N', 'NORTE'),
    ('NE', 'NORDESTE'),
    ('CO', 'CENTRO-OESTE'),
    ('SE', 'SUDESTE'),
    ('S', 'SUL')
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO states (code, name, region_code)
VALUES
    ('AC', 'ACRE', 'N'),
    ('AL', 'ALAGOAS', 'NE'),
    ('AP', 'AMAPÁ', 'N'),
    ('AM', 'AMAZONAS', 'N'),
    ('BA', 'BAHIA', 'NE'),
    ('CE', 'CEARÁ', 'NE'),
    ('DF', 'DISTRITO FEDERAL', 'CO'),
    ('ES', 'ESPÍRITO SANTO', 'SE'),
    ('GO', 'GOIÁS', 'CO'),
    ('MA', 'MARANHÃO', 'NE'),
    ('MT', 'MATO GROSSO', 'CO'),
    ('MS', 'MATO GROSSO DO SUL', 'CO'),
    ('MG', 'MINAS GERAIS', 'SE'),
    ('PA', 'PARÁ', 'N'),
    ('PB', 'PARAÍBA', 'NE'),
    ('PR', 'PARANÁ', 'S'),
    ('PE', 'PERNAMBUCO', 'NE'),
    ('PI', 'PIAUÍ', 'NE'),
    ('RJ', 'RIO DE JANEIRO', 'SE'),
    ('RN', 'RIO GRANDE DO NORTE', 'NE'),
    ('RS', 'RIO GRANDE DO SUL', 'S'),
    ('RO', 'RONDÔNIA', 'N'),
    ('RR', 'RORAIMA', 'N'),
    ('SC', 'SANTA CATARINA', 'S'),
    ('SP', 'SÃO PAULO', 'SE'),
    ('SE', 'SERGIPE', 'NE'),
    ('TO', 'TOCANTINS', 'N')
ON CONFLICT (code) DO UPDATE
SET name = EXCLUDED.name,
    region_code = EXCLUDED.region_code;

INSERT INTO products (name, unit)
VALUES
    ('GASOLINA COMUM', 'BRL/liter'),
    ('GASOLINA ADITIVADA', 'BRL/liter'),
    ('ETANOL HIDRATADO', 'BRL/liter'),
    ('ÓLEO DIESEL', 'BRL/liter'),
    ('ÓLEO DIESEL S10', 'BRL/liter'),
    ('GNV', 'BRL/m3')
ON CONFLICT (name) DO UPDATE SET unit = EXCLUDED.unit;

COMMENT ON TABLE price_observations IS
    'Validated fuel price observations loaded from FuelVision processed data.';
COMMENT ON CONSTRAINT price_observations_business_key_uk ON price_observations IS
    'Prevents two observations for the same retailer, product and collection date.';

COMMIT;
