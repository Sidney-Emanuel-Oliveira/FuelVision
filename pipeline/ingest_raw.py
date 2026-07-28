"""Validate a CSV input and preserve its bytes in the raw data layer."""

from __future__ import annotations

import argparse
import csv
import hashlib
import logging
import shutil
import sys
from pathlib import Path
from typing import Dict, Optional, Sequence, Tuple

from pipeline.schema import INGESTION_REQUIRED_COLUMNS

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "raw"
DEFAULT_LOG_PATH = PROJECT_ROOT / "logs" / "ingestion.log"

REQUIRED_COLUMNS = INGESTION_REQUIRED_COLUMNS

LOGGER = logging.getLogger(__name__)


class IngestionError(Exception):
    """Base error for expected ingestion failures."""


class InputFileNotFoundError(IngestionError):
    """Raised when the input path does not exist."""


class InvalidInputTypeError(IngestionError):
    """Raised when the input path does not point to a regular file."""


class InvalidExtensionError(IngestionError):
    """Raised when the input file is not a CSV file."""


class SchemaValidationError(IngestionError):
    """Raised when the CSV header cannot satisfy the minimum schema."""


class DestinationConflictError(IngestionError):
    """Raised when a destination name exists with different content."""


def validate_input_path(source: Path) -> None:
    """Confirm that the input exists, is a file and has a CSV extension."""
    if not source.exists():
        raise InputFileNotFoundError(f"Input file does not exist: {source}")
    if not source.is_file():
        raise InvalidInputTypeError(f"Input path is not a regular file: {source}")
    if source.suffix.lower() != ".csv":
        raise InvalidExtensionError(f"Input file must use the .csv extension: {source}")


def read_and_validate_header(source: Path) -> Tuple[str, ...]:
    """Read only the header and confirm that required columns are present."""
    try:
        with source.open(encoding="utf-8-sig", newline="") as csv_file:
            header = next(csv.reader(csv_file, delimiter=";"), None)
    except (OSError, UnicodeDecodeError, csv.Error) as error:
        raise SchemaValidationError(
            f"Could not read the CSV header: {error}"
        ) from error

    if not header:
        raise SchemaValidationError("The CSV file is empty or has no header.")

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in header]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise SchemaValidationError(f"Missing required columns: {missing}")

    return tuple(header)


def calculate_sha256(path: Path) -> str:
    """Calculate a content identifier without loading the whole file in memory."""
    digest = hashlib.sha256()
    try:
        with path.open("rb") as file_object:
            for chunk in iter(lambda: file_object.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as error:
        raise IngestionError(f"Could not read file for SHA-256: {path}") from error
    return digest.hexdigest()


def build_destination_path(source: Path, output_dir: Path, digest: str) -> Path:
    """Build a stable name from the original stem and the content hash."""
    return output_dir / f"{source.stem}__{digest[:12]}.csv"


def copy_without_overwrite(source: Path, destination: Path, digest: str) -> str:
    """Copy bytes safely, skip identical content and reject name conflicts."""
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise IngestionError(
            f"Could not create raw output directory: {destination.parent}"
        ) from error

    if destination.exists():
        if calculate_sha256(destination) == digest:
            return "already_exists"
        raise DestinationConflictError(
            f"Destination already exists with different content: {destination}"
        )

    destination_created = False
    try:
        with source.open("rb") as source_file, destination.open("xb") as raw_file:
            destination_created = True
            shutil.copyfileobj(source_file, raw_file, length=1024 * 1024)
    except FileExistsError:
        if calculate_sha256(destination) == digest:
            return "already_exists"
        raise DestinationConflictError(
            f"Destination was created concurrently with different content: {destination}"
        ) from None
    except OSError as error:
        if destination_created:
            destination.unlink(missing_ok=True)
        raise IngestionError(f"Could not copy input to raw layer: {error}") from error

    if calculate_sha256(destination) != digest:
        destination.unlink(missing_ok=True)
        raise IngestionError("Copied file failed the SHA-256 integrity check.")

    return "created"


def ingest_file(
    source: Path, output_dir: Path = DEFAULT_OUTPUT_DIR
) -> Dict[str, object]:
    """Run the raw ingestion flow and return its auditable result."""
    source = source.expanduser().resolve()
    output_dir = output_dir.expanduser().resolve()

    LOGGER.info("ingestion_started source=%s output_dir=%s", source, output_dir)
    validate_input_path(source)
    header = read_and_validate_header(source)
    digest = calculate_sha256(source)
    destination = build_destination_path(source, output_dir, digest)
    status = copy_without_overwrite(source, destination, digest)

    result: Dict[str, object] = {
        "status": status,
        "source": source,
        "destination": destination,
        "sha256": digest,
        "bytes": destination.stat().st_size,
        "columns": header,
    }
    LOGGER.info(
        "ingestion_completed status=%s destination=%s sha256=%s bytes=%s",
        status,
        destination,
        digest,
        result["bytes"],
    )
    return result


def configure_logging(log_path: Path) -> None:
    """Configure a file log for command-line executions."""
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
    except OSError as error:
        raise IngestionError(
            f"Could not create or open log file: {log_path}"
        ) from error

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[file_handler],
        force=True,
    )


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line interface for the raw ingestion."""
    parser = argparse.ArgumentParser(
        description="Validate a FuelVision CSV and copy its bytes to the raw layer."
    )
    parser.add_argument("input_path", type=Path, help="Path to the source CSV file.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Raw output directory. Default: {DEFAULT_OUTPUT_DIR}",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=DEFAULT_LOG_PATH,
        help=f"Log file path. Default: {DEFAULT_LOG_PATH}",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Execute the CLI and translate expected failures into exit code 1."""
    arguments = build_parser().parse_args(argv)
    try:
        configure_logging(arguments.log_file.expanduser().resolve())
        result = ingest_file(arguments.input_path, arguments.output_dir)
    except IngestionError as error:
        LOGGER.error("ingestion_failed error=%s", error)
        print(f"Ingestion failed: {error}", file=sys.stderr)
        return 1

    print(f"status={result['status']}")
    print(f"destination={result['destination']}")
    print(f"sha256={result['sha256']}")
    print(f"bytes={result['bytes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
