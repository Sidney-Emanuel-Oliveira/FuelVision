"""Tests for the raw ingestion pipeline introduced in Module 2."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from pipeline.ingest_raw import (
    DestinationConflictError,
    InputFileNotFoundError,
    InvalidExtensionError,
    InvalidInputTypeError,
    SchemaValidationError,
    build_destination_path,
    calculate_sha256,
    ingest_file,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = PROJECT_ROOT / "data" / "samples" / "precos-combustiveis-amostra.csv"


class IngestRawTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.temp_path = Path(self.temporary_directory.name)
        self.output_dir = self.temp_path / "raw"

    def test_ingestion_copies_the_exact_source_bytes(self) -> None:
        result = ingest_file(SAMPLE_PATH, self.output_dir)
        destination = result["destination"]

        self.assertEqual(result["status"], "created")
        self.assertEqual(destination.read_bytes(), SAMPLE_PATH.read_bytes())
        self.assertIn(result["sha256"][:12], destination.name)

    def test_repeated_ingestion_does_not_overwrite_existing_content(self) -> None:
        first_result = ingest_file(SAMPLE_PATH, self.output_dir)
        first_inode = first_result["destination"].stat().st_ino

        second_result = ingest_file(SAMPLE_PATH, self.output_dir)

        self.assertEqual(second_result["status"], "already_exists")
        self.assertEqual(second_result["destination"].stat().st_ino, first_inode)
        self.assertEqual(second_result["destination"].read_bytes(), SAMPLE_PATH.read_bytes())

    def test_missing_input_is_rejected(self) -> None:
        with self.assertRaises(InputFileNotFoundError):
            ingest_file(self.temp_path / "missing.csv", self.output_dir)

    def test_directory_input_is_rejected(self) -> None:
        with self.assertRaises(InvalidInputTypeError):
            ingest_file(self.temp_path, self.output_dir)

    def test_non_csv_extension_is_rejected(self) -> None:
        text_file = self.temp_path / "input.txt"
        text_file.write_text("not a csv", encoding="utf-8")

        with self.assertRaises(InvalidExtensionError):
            ingest_file(text_file, self.output_dir)

    def test_uppercase_csv_extension_is_accepted(self) -> None:
        uppercase_csv = self.temp_path / "INPUT.CSV"
        uppercase_csv.write_bytes(SAMPLE_PATH.read_bytes())

        result = ingest_file(uppercase_csv, self.output_dir)

        self.assertEqual(result["status"], "created")

    def test_empty_csv_is_rejected(self) -> None:
        empty_csv = self.temp_path / "empty.csv"
        empty_csv.write_text("", encoding="utf-8")

        with self.assertRaisesRegex(SchemaValidationError, "empty or has no header"):
            ingest_file(empty_csv, self.output_dir)

    def test_missing_required_columns_are_reported(self) -> None:
        invalid_csv = self.temp_path / "invalid.csv"
        invalid_csv.write_text("Municipio;Produto\nRECIFE;GASOLINA\n", encoding="utf-8")

        with self.assertRaisesRegex(SchemaValidationError, "Missing required columns"):
            ingest_file(invalid_csv, self.output_dir)

    def test_destination_conflict_is_rejected(self) -> None:
        digest = calculate_sha256(SAMPLE_PATH)
        destination = build_destination_path(SAMPLE_PATH, self.output_dir, digest)
        destination.parent.mkdir(parents=True)
        destination.write_bytes(b"different content")

        with self.assertRaises(DestinationConflictError):
            ingest_file(SAMPLE_PATH, self.output_dir)

    def test_command_line_execution_creates_output_and_log(self) -> None:
        log_path = self.temp_path / "logs" / "ingestion.log"
        process = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "pipeline" / "ingest_raw.py"),
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
        self.assertIn("status=created", process.stdout)
        self.assertIn("ingestion_completed", log_path.read_text(encoding="utf-8"))

    def test_command_line_failure_returns_one_and_writes_log(self) -> None:
        log_path = self.temp_path / "logs" / "failure.log"
        process = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "pipeline" / "ingest_raw.py"),
                str(self.temp_path / "missing.csv"),
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

        self.assertEqual(process.returncode, 1)
        self.assertIn("Ingestion failed", process.stderr)
        self.assertIn("ingestion_failed", log_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
