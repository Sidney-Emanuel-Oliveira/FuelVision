"""Schemas shared by the FuelVision ingestion and transformation stages."""

ANP_SOURCE_COLUMNS = (
    "Regiao - Sigla",
    "Estado - Sigla",
    "Municipio",
    "Revenda",
    "CNPJ da Revenda",
    "Nome da Rua",
    "Numero Rua",
    "Complemento",
    "Bairro",
    "Cep",
    "Produto",
    "Data da Coleta",
    "Valor de Venda",
    "Valor de Compra",
    "Unidade de Medida",
    "Bandeira",
)

INGESTION_REQUIRED_COLUMNS = (
    "Estado - Sigla",
    "Municipio",
    "Produto",
    "Data da Coleta",
    "Valor de Venda",
    "Unidade de Medida",
)

PROCESSED_COLUMNS = (
    "region_code",
    "state_code",
    "municipality",
    "retailer_name",
    "retailer_cnpj",
    "street_name",
    "street_number",
    "address_complement",
    "neighborhood",
    "postal_code",
    "product",
    "collection_date",
    "sale_price",
    "purchase_price",
    "unit",
    "brand",
)
