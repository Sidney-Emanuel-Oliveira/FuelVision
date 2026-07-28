"""Tests for the exploratory reader created in Module 1."""

import csv
import tempfile
import unittest
from pathlib import Path

from exploration.explore_sample import (
    EXPECTED_COLUMNS,
    SAMPLE_PATH,
    analyze_records,
    load_records,
)


class ExploreSampleTest(unittest.TestCase):
    def test_sample_has_expected_shape_and_groups(self) -> None:
        records = load_records(SAMPLE_PATH)
        summary = analyze_records(records)

        self.assertEqual(summary["row_count"], 60)
        self.assertEqual(summary["column_count"], 16)
        self.assertEqual(summary["regions"], ["CO", "N", "NE", "S", "SE"])
        self.assertEqual(
            summary["products"],
            [
                "DIESEL",
                "DIESEL S10",
                "ETANOL",
                "GASOLINA",
                "GASOLINA ADITIVADA",
                "GNV",
            ],
        )

    def test_sample_has_valid_core_fields(self) -> None:
        summary = analyze_records(load_records(SAMPLE_PATH))

        self.assertEqual(summary["invalid_date_count"], 0)
        self.assertEqual(summary["invalid_price_count"], 0)
        self.assertEqual(summary["inconsistent_unit_count"], 0)

    def test_quality_profile_matches_the_documented_sample(self) -> None:
        summary = analyze_records(load_records(SAMPLE_PATH))

        self.assertEqual(summary["exact_duplicate_count"], 0)
        self.assertEqual(summary["missing_by_column"]["Complemento"], 43)
        self.assertEqual(summary["missing_by_column"]["Valor de Compra"], 60)
        self.assertEqual(summary["whitespace_by_column"]["CNPJ da Revenda"], 60)
        self.assertEqual(summary["whitespace_by_column"]["Nome da Rua"], 3)

    def test_reader_rejects_an_unexpected_header(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            invalid_path = Path(temporary_directory) / "invalid.csv"
            with invalid_path.open("w", encoding="utf-8", newline="") as csv_file:
                writer = csv.writer(csv_file, delimiter=";")
                writer.writerow(["unexpected_column"])
                writer.writerow(["unexpected_value"])

            with self.assertRaisesRegex(ValueError, "columns differ"):
                load_records(invalid_path)

    def test_expected_schema_has_no_repeated_columns(self) -> None:
        self.assertEqual(len(EXPECTED_COLUMNS), len(set(EXPECTED_COLUMNS)))


if __name__ == "__main__":
    unittest.main()
