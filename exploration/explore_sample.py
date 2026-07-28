"""Explore the small ANP sample used in Module 1."""

from __future__ import annotations

import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, List

SAMPLE_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "samples"
    / "precos-combustiveis-amostra.csv"
)

EXPECTED_COLUMNS = (
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


def load_records(path: Path = SAMPLE_PATH) -> List[Dict[str, str]]:
    """Read the module sample and confirm its documented columns."""
    with path.open(encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=";")

        if tuple(reader.fieldnames or ()) != EXPECTED_COLUMNS:
            raise ValueError("The CSV columns differ from the documented ANP schema.")

        return list(reader)


def parse_date(value: str) -> datetime:
    """Parse a date written in the format used by the source file."""
    return datetime.strptime(value.strip(), "%d/%m/%Y")


def parse_price(value: str) -> Decimal:
    """Parse a Brazilian decimal value without using binary floating point."""
    return Decimal(value.strip().replace(",", "."))


def analyze_records(records: List[Dict[str, str]]) -> Dict[str, object]:
    """Calculate a compact quality profile for the sample."""
    missing_by_column = {
        column: sum(not record[column].strip() for record in records)
        for column in EXPECTED_COLUMNS
    }
    whitespace_by_column = {
        column: sum(record[column] != record[column].strip() for record in records)
        for column in EXPECTED_COLUMNS
    }

    row_signatures = [
        tuple(record[column] for column in EXPECTED_COLUMNS) for record in records
    ]
    exact_duplicate_count = len(row_signatures) - len(set(row_signatures))

    valid_dates = []
    invalid_date_count = 0
    valid_prices = []
    invalid_price_count = 0
    inconsistent_unit_count = 0

    for record in records:
        try:
            valid_dates.append(parse_date(record["Data da Coleta"]))
        except ValueError:
            invalid_date_count += 1

        try:
            valid_prices.append(parse_price(record["Valor de Venda"]))
        except InvalidOperation:
            invalid_price_count += 1

        expected_unit = "R$ / m³" if record["Produto"] == "GNV" else "R$ / litro"
        if record["Unidade de Medida"] != expected_unit:
            inconsistent_unit_count += 1

    return {
        "row_count": len(records),
        "column_count": len(EXPECTED_COLUMNS),
        "regions": sorted({record["Regiao - Sigla"] for record in records}),
        "products": sorted({record["Produto"] for record in records}),
        "start_date": min(valid_dates).date().isoformat() if valid_dates else None,
        "end_date": max(valid_dates).date().isoformat() if valid_dates else None,
        "minimum_sale_price": min(valid_prices) if valid_prices else None,
        "maximum_sale_price": max(valid_prices) if valid_prices else None,
        "missing_by_column": missing_by_column,
        "whitespace_by_column": whitespace_by_column,
        "exact_duplicate_count": exact_duplicate_count,
        "invalid_date_count": invalid_date_count,
        "invalid_price_count": invalid_price_count,
        "inconsistent_unit_count": inconsistent_unit_count,
    }


def print_summary(summary: Dict[str, object]) -> None:
    """Print the profile in a format that is easy to inspect in a terminal."""
    print(f"Rows: {summary['row_count']}")
    print(f"Columns: {summary['column_count']}")
    print(f"Regions: {', '.join(summary['regions'])}")
    print(f"Products: {', '.join(summary['products'])}")
    print(f"Date range: {summary['start_date']} to {summary['end_date']}")
    print(
        "Sale price range in the sample: "
        f"{summary['minimum_sale_price']} to {summary['maximum_sale_price']}"
    )
    print(f"Exact duplicate rows: {summary['exact_duplicate_count']}")
    print(f"Invalid dates: {summary['invalid_date_count']}")
    print(f"Invalid sale prices: {summary['invalid_price_count']}")
    print(f"Product/unit inconsistencies: {summary['inconsistent_unit_count']}")

    missing = {
        column: count for column, count in summary["missing_by_column"].items() if count
    }
    whitespace = {
        column: count
        for column, count in summary["whitespace_by_column"].items()
        if count
    }
    print(f"Missing values by column: {missing}")
    print(f"Values with surrounding whitespace by column: {whitespace}")


def main() -> None:
    """Run the exploration for the versioned sample."""
    print_summary(analyze_records(load_records()))


if __name__ == "__main__":
    main()
