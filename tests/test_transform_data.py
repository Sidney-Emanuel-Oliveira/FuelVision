"""Tests for cleaning, transformation and validation in Module 3."""

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from pipeline.schema import ANP_SOURCE_COLUMNS
from pipeline.transform_data import (
    OutputConflictError,
    TransformationError,
    build_output_paths,
    is_valid_cnpj,
    transform_file,
    transform_record,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = PROJECT_ROOT / "data" / "samples" / "precos-combustiveis-amostra.csv"


class TransformDataTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.temp_path = Path(self.temporary_directory.name)
        self.output_dir = self.temp_path / "processed"
        self.first_source_record = self._read_first_source_record()

    def _read_first_source_record(self):
        with SAMPLE_PATH.open(encoding="utf-8", newline="") as sample_file:
            return next(csv.DictReader(sample_file, delimiter=";"))

    def _write_source(self, records, name="input.csv", fieldnames=ANP_SOURCE_COLUMNS):
        source_path = self.temp_path / name
        with source_path.open("w", encoding="utf-8", newline="") as source_file:
            writer = csv.DictWriter(
                source_file,
                fieldnames=fieldnames,
                delimiter=";",
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(records)
        return source_path

    def test_sample_is_transformed_into_sixty_valid_records(self) -> None:
        result = transform_file(SAMPLE_PATH, self.output_dir)

        self.assertEqual(result["status"], "created")
        self.assertEqual(result["rows_read"], 60)
        self.assertEqual(result["accepted_count"], 60)
        self.assertEqual(result["rejected_count"], 0)

        with result["processed_path"].open(encoding="utf-8", newline="") as output:
            processed_records = list(csv.DictReader(output, delimiter=";"))

        first_record = processed_records[0]
        self.assertEqual(len(processed_records), 60)
        self.assertEqual(first_record["retailer_cnpj"], "01492748000383")
        self.assertEqual(first_record["collection_date"], "2026-01-02")
        self.assertEqual(first_record["sale_price"], "7.97")
        self.assertEqual(first_record["product"], "GASOLINA COMUM")
        self.assertEqual(first_record["unit"], "BRL/liter")

        manifest = json.loads(result["manifest_path"].read_text(encoding="utf-8"))
        self.assertEqual(manifest["accepted_count"], 60)
        self.assertEqual(manifest["rejected_count"], 0)

    def test_optional_empty_values_are_preserved_without_rejection(self) -> None:
        processed, reasons = transform_record(self.first_source_record)

        self.assertEqual(reasons, [])
        self.assertEqual(processed["address_complement"], "")
        self.assertEqual(processed["purchase_price"], "")

    def test_cnpj_validation_uses_check_digits(self) -> None:
        self.assertTrue(is_valid_cnpj("01492748000383"))
        self.assertFalse(is_valid_cnpj("01492748000384"))
        self.assertFalse(is_valid_cnpj("11111111111111"))

    def test_invalid_values_are_written_with_rejection_reasons(self) -> None:
        invalid_record = dict(self.first_source_record)
        invalid_record["Estado - Sigla"] = "XX"
        invalid_record["Data da Coleta"] = "31/02/2026"
        invalid_record["Valor de Venda"] = "-1,00"
        source_path = self._write_source([invalid_record])

        result = transform_file(source_path, self.output_dir)

        self.assertEqual(result["accepted_count"], 0)
        self.assertEqual(result["rejected_count"], 1)
        with result["rejected_path"].open(encoding="utf-8", newline="") as rejected:
            rejected_record = next(csv.DictReader(rejected, delimiter=";"))
        reasons = rejected_record["rejection_reasons"].split("|")
        self.assertIn("invalid_state_code", reasons)
        self.assertIn("invalid_collection_date", reasons)
        self.assertIn("invalid_sale_price", reasons)
        self.assertEqual(rejected_record["source_row_number"], "2")

    def test_domain_mismatches_are_reported(self) -> None:
        invalid_record = dict(self.first_source_record)
        invalid_record["Regiao - Sigla"] = "N"
        invalid_record["Estado - Sigla"] = "SP"
        invalid_record["CNPJ da Revenda"] = "01.492.748/0003-84"
        invalid_record["Cep"] = "123"
        invalid_record["Produto"] = "GNV"
        invalid_record["Unidade de Medida"] = "R$ / litro"
        invalid_record["Valor de Compra"] = "zero"

        _, reasons = transform_record(invalid_record)

        self.assertIn("state_region_mismatch", reasons)
        self.assertIn("invalid_retailer_cnpj", reasons)
        self.assertIn("invalid_postal_code", reasons)
        self.assertIn("product_unit_mismatch", reasons)
        self.assertIn("invalid_purchase_price", reasons)

    def test_exact_duplicate_is_rejected(self) -> None:
        source_path = self._write_source(
            [self.first_source_record, self.first_source_record]
        )

        result = transform_file(source_path, self.output_dir)

        self.assertEqual(result["accepted_count"], 1)
        self.assertEqual(result["rejected_count"], 1)
        self.assertEqual(result["duplicate_count"], 1)
        rejected_text = result["rejected_path"].read_text(encoding="utf-8")
        self.assertIn("duplicate_record", rejected_text)

    def test_conflicting_duplicate_is_rejected(self) -> None:
        conflicting_record = dict(self.first_source_record)
        conflicting_record["Valor de Venda"] = "9,99"
        source_path = self._write_source(
            [self.first_source_record, conflicting_record]
        )

        result = transform_file(source_path, self.output_dir)

        self.assertEqual(result["accepted_count"], 1)
        self.assertEqual(result["conflicting_duplicate_count"], 1)
        rejected_text = result["rejected_path"].read_text(encoding="utf-8")
        self.assertIn("conflicting_duplicate", rejected_text)

    def test_repeated_transformation_does_not_overwrite_outputs(self) -> None:
        first_result = transform_file(SAMPLE_PATH, self.output_dir)
        first_inodes = {
            key: first_result[key].stat().st_ino
            for key in ("processed_path", "rejected_path", "manifest_path")
        }

        second_result = transform_file(SAMPLE_PATH, self.output_dir)

        self.assertEqual(second_result["status"], "already_exists")
        second_inodes = {
            key: second_result[key].stat().st_ino
            for key in ("processed_path", "rejected_path", "manifest_path")
        }
        self.assertEqual(second_inodes, first_inodes)

    def test_output_conflict_is_rejected(self) -> None:
        first_result = transform_file(SAMPLE_PATH, self.output_dir)
        first_result["processed_path"].write_text("conflict", encoding="utf-8")

        with self.assertRaises(OutputConflictError):
            transform_file(SAMPLE_PATH, self.output_dir)
        self.assertEqual(list(self.output_dir.glob(".fuelvision-*")), [])

    def test_late_output_conflict_does_not_publish_partial_set(self) -> None:
        self.output_dir.mkdir()
        output_paths = build_output_paths(SAMPLE_PATH, self.output_dir)
        output_paths["rejected"].write_text("conflict", encoding="utf-8")

        with self.assertRaises(OutputConflictError):
            transform_file(SAMPLE_PATH, self.output_dir)

        self.assertFalse(output_paths["processed"].exists())
        self.assertFalse(output_paths["manifest"].exists())
        self.assertEqual(list(self.output_dir.glob(".fuelvision-*")), [])

    def test_truncated_row_is_rejected_instead_of_crashing(self) -> None:
        source_path = self.temp_path / "truncated.csv"
        source_path.write_text(
            ";".join(ANP_SOURCE_COLUMNS) + "\nN;AC\n",
            encoding="utf-8",
        )

        result = transform_file(source_path, self.output_dir)

        self.assertEqual(result["accepted_count"], 0)
        self.assertEqual(result["rejected_count"], 1)
        rejected_text = result["rejected_path"].read_text(encoding="utf-8")
        self.assertIn("missing_municipality", rejected_text)

    def test_extra_row_values_are_rejected_instead_of_ignored(self) -> None:
        source_path = self.temp_path / "extra-values.csv"
        source_path.write_text(
            ";".join(ANP_SOURCE_COLUMNS)
            + "\n"
            + ";".join(self.first_source_record[column] for column in ANP_SOURCE_COLUMNS)
            + ";EXTRA\n",
            encoding="utf-8",
        )

        result = transform_file(source_path, self.output_dir)

        self.assertEqual(result["accepted_count"], 0)
        rejected_text = result["rejected_path"].read_text(encoding="utf-8")
        self.assertIn("unexpected_extra_values", rejected_text)

    def test_unexpected_source_column_is_rejected(self) -> None:
        fieldnames = ANP_SOURCE_COLUMNS + ("Unexpected",)
        unexpected_record = {**self.first_source_record, "Unexpected": "value"}
        source_path = self._write_source(
            [unexpected_record], fieldnames=fieldnames
        )

        with self.assertRaisesRegex(TransformationError, "unexpected=Unexpected"):
            transform_file(source_path, self.output_dir)

    def test_command_line_execution_creates_three_outputs_and_log(self) -> None:
        log_path = self.temp_path / "logs" / "transformation.log"
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "pipeline.transform_data",
                str(SAMPLE_PATH),
                "--output-dir",
                str(self.output_dir),
                "--log-file",
                str(log_path),
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn("accepted=60", process.stdout)
        self.assertIn("rejected=0", process.stdout)
        self.assertIn("transformation_completed", log_path.read_text(encoding="utf-8"))
        self.assertEqual(len(list(self.output_dir.iterdir())), 3)


if __name__ == "__main__":
    unittest.main()
