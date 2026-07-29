"""Transform ANP raw CSV records into validated processed data."""

from __future__ import annotations

import argparse
import csv
import json
import logging
import re
import sys
import tempfile
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from pipeline.ingest_raw import (
    DestinationConflictError,
    IngestionError,
    calculate_sha256,
    configure_logging,
    copy_without_overwrite,
    validate_input_path,
)
from pipeline.schema import ANP_SOURCE_COLUMNS, PROCESSED_COLUMNS

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DEFAULT_TRANSFORMATION_LOG_PATH = PROJECT_ROOT / "logs" / "transformation.log"
TRANSFORMATION_VERSION = "v1"

REJECTED_COLUMNS = ("source_row_number", "rejection_reasons") + ANP_SOURCE_COLUMNS

STATE_TO_REGION = {
    "AC": "N",
    "AL": "NE",
    "AP": "N",
    "AM": "N",
    "BA": "NE",
    "CE": "NE",
    "DF": "CO",
    "ES": "SE",
    "GO": "CO",
    "MA": "NE",
    "MT": "CO",
    "MS": "CO",
    "MG": "SE",
    "PA": "N",
    "PB": "NE",
    "PR": "S",
    "PE": "NE",
    "PI": "NE",
    "RJ": "SE",
    "RN": "NE",
    "RS": "S",
    "RO": "N",
    "RR": "N",
    "SC": "S",
    "SP": "SE",
    "SE": "NE",
    "TO": "N",
}

PRODUCT_ALIASES = {
    "DIESEL": "ÓLEO DIESEL",
    "DIESEL S10": "ÓLEO DIESEL S10",
    "ETANOL": "ETANOL HIDRATADO",
    "ETANOL HIDRATADO": "ETANOL HIDRATADO",
    "GASOLINA": "GASOLINA COMUM",
    "GASOLINA COMUM": "GASOLINA COMUM",
    "GASOLINA ADITIVADA": "GASOLINA ADITIVADA",
    "GNV": "GNV",
}

UNIT_ALIASES = {
    "R$ / LITRO": "BRL/liter",
    "R$/LITRO": "BRL/liter",
    "R$ / M³": "BRL/m3",
    "R$/M³": "BRL/m3",
    "R$ / M3": "BRL/m3",
    "R$/M3": "BRL/m3",
}

EXPECTED_UNIT_BY_PRODUCT = {
    "ÓLEO DIESEL": "BRL/liter",
    "ÓLEO DIESEL S10": "BRL/liter",
    "ETANOL HIDRATADO": "BRL/liter",
    "GASOLINA COMUM": "BRL/liter",
    "GASOLINA ADITIVADA": "BRL/liter",
    "GNV": "BRL/m3",
}

VALID_REGION_CODES = frozenset(STATE_TO_REGION.values())

LOGGER = logging.getLogger(__name__)


class TransformationError(Exception):
    """Base error for expected transformation failures."""


class OutputConflictError(TransformationError):
    """Raised when a deterministic output exists with different content."""


def normalize_text(value: str) -> str:
    """Trim external whitespace and collapse repeated internal whitespace."""
    return " ".join(value.strip().split())


def normalize_upper_text(value: str) -> str:
    """Apply the text cleanup and convert letters to uppercase."""
    return normalize_text(value).upper()


def digits_only(value: str) -> str:
    """Keep only decimal digits from a formatted identifier."""
    return re.sub(r"\D", "", value)


def source_value(record: Dict[str, str], column: str) -> str:
    """Return a source field as text even when a malformed row supplies None."""
    value = record.get(column, "")
    return value if isinstance(value, str) else ""


def is_valid_cnpj(value: str) -> bool:
    """Validate the length and two check digits of a normalized CNPJ."""
    if len(value) != 14 or value == value[0] * 14:
        return False

    def calculate_digit(base: str, weights: Tuple[int, ...]) -> str:
        total = sum(
            int(digit) * weight for digit, weight in zip(base, weights, strict=True)
        )
        remainder = total % 11
        return "0" if remainder < 2 else str(11 - remainder)

    first_digit = calculate_digit(value[:12], (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2))
    second_digit = calculate_digit(
        value[:12] + first_digit,
        (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2),
    )
    return value[-2:] == first_digit + second_digit


def parse_date(value: str) -> str:
    """Convert an ANP date into the ISO date format."""
    return datetime.strptime(normalize_text(value), "%d/%m/%Y").date().isoformat()


def parse_positive_decimal(value: str) -> str:
    """Convert a Brazilian decimal representation into a positive decimal text."""
    normalized = normalize_text(value)
    if "," in normalized:
        normalized = normalized.replace(".", "").replace(",", ".")
    try:
        decimal_value = Decimal(normalized)
    except InvalidOperation as error:
        raise ValueError("value is not a valid decimal") from error
    if not decimal_value.is_finite() or decimal_value <= 0:
        raise ValueError("value must be a positive finite decimal")
    return format(decimal_value, "f")


def normalize_product(value: str) -> str:
    """Convert a source product label into the canonical FuelVision label."""
    source_product = normalize_upper_text(value)
    try:
        return PRODUCT_ALIASES[source_product]
    except KeyError as error:
        raise ValueError(
            f"unsupported product: {source_product or '<empty>'}"
        ) from error


def normalize_unit(value: str) -> str:
    """Convert a source unit label into the canonical FuelVision unit."""
    source_unit = normalize_upper_text(value)
    try:
        return UNIT_ALIASES[source_unit]
    except KeyError as error:
        raise ValueError(f"unsupported unit: {source_unit or '<empty>'}") from error


def transform_record(record: Dict[str, str]) -> Tuple[Dict[str, str], List[str]]:
    """Normalize one record and return the processed values and rejection reasons."""
    reasons: List[str] = []

    region_code = normalize_upper_text(source_value(record, "Regiao - Sigla"))
    state_code = normalize_upper_text(source_value(record, "Estado - Sigla"))
    municipality = normalize_upper_text(source_value(record, "Municipio"))
    retailer_name = normalize_upper_text(source_value(record, "Revenda"))
    retailer_cnpj = digits_only(source_value(record, "CNPJ da Revenda"))
    street_name = normalize_upper_text(source_value(record, "Nome da Rua"))
    street_number = normalize_upper_text(source_value(record, "Numero Rua"))
    address_complement = normalize_upper_text(source_value(record, "Complemento"))
    neighborhood = normalize_upper_text(source_value(record, "Bairro"))
    postal_code = digits_only(source_value(record, "Cep"))
    brand = normalize_upper_text(source_value(record, "Bandeira"))

    if region_code not in VALID_REGION_CODES:
        reasons.append("invalid_region_code")
    if state_code not in STATE_TO_REGION:
        reasons.append("invalid_state_code")
    elif region_code in VALID_REGION_CODES:
        if STATE_TO_REGION[state_code] != region_code:
            reasons.append("state_region_mismatch")

    required_texts = {
        "municipality": municipality,
        "retailer_name": retailer_name,
        "street_name": street_name,
        "street_number": street_number,
        "neighborhood": neighborhood,
        "brand": brand,
    }
    for field_name, field_value in required_texts.items():
        if not field_value:
            reasons.append(f"missing_{field_name}")

    if not is_valid_cnpj(retailer_cnpj):
        reasons.append("invalid_retailer_cnpj")
    if len(postal_code) != 8:
        reasons.append("invalid_postal_code")

    try:
        product = normalize_product(source_value(record, "Produto"))
    except ValueError:
        product = ""
        reasons.append("invalid_product")

    try:
        collection_date = parse_date(source_value(record, "Data da Coleta"))
    except ValueError:
        collection_date = ""
        reasons.append("invalid_collection_date")

    try:
        sale_price = parse_positive_decimal(source_value(record, "Valor de Venda"))
    except ValueError:
        sale_price = ""
        reasons.append("invalid_sale_price")

    purchase_source = normalize_text(source_value(record, "Valor de Compra"))
    if purchase_source:
        try:
            purchase_price = parse_positive_decimal(purchase_source)
        except ValueError:
            purchase_price = ""
            reasons.append("invalid_purchase_price")
    else:
        purchase_price = ""

    try:
        unit = normalize_unit(source_value(record, "Unidade de Medida"))
    except ValueError:
        unit = ""
        reasons.append("invalid_unit")

    if product and unit and EXPECTED_UNIT_BY_PRODUCT[product] != unit:
        reasons.append("product_unit_mismatch")

    processed = {
        "region_code": region_code,
        "state_code": state_code,
        "municipality": municipality,
        "retailer_name": retailer_name,
        "retailer_cnpj": retailer_cnpj,
        "street_name": street_name,
        "street_number": street_number,
        "address_complement": address_complement,
        "neighborhood": neighborhood,
        "postal_code": postal_code,
        "product": product,
        "collection_date": collection_date,
        "sale_price": sale_price,
        "purchase_price": purchase_price,
        "unit": unit,
        "brand": brand,
    }
    return processed, reasons


def validate_source_header(fieldnames: Optional[List[str]]) -> None:
    """Require the complete ANP source schema without silently ignoring columns."""
    if not fieldnames:
        raise TransformationError("The source CSV is empty or has no header.")
    if len(fieldnames) != len(set(fieldnames)):
        raise TransformationError("The source CSV contains duplicated column names.")

    missing = [column for column in ANP_SOURCE_COLUMNS if column not in fieldnames]
    unexpected = [column for column in fieldnames if column not in ANP_SOURCE_COLUMNS]
    if missing or unexpected:
        details = []
        if missing:
            details.append(f"missing={','.join(missing)}")
        if unexpected:
            details.append(f"unexpected={','.join(unexpected)}")
        raise TransformationError("Source schema mismatch: " + "; ".join(details))


def build_output_paths(source: Path, output_dir: Path) -> Dict[str, Path]:
    """Build deterministic processed, rejected and manifest paths."""
    base_name = f"{source.stem}__{TRANSFORMATION_VERSION}"
    return {
        "processed": output_dir / f"{base_name}__processed.csv",
        "rejected": output_dir / f"{base_name}__rejected.csv",
        "manifest": output_dir / f"{base_name}__manifest.json",
    }


def create_temporary_path(output_dir: Path, suffix: str) -> Path:
    """Create a unique temporary file path in the destination filesystem."""
    try:
        temporary_file = tempfile.NamedTemporaryFile(
            dir=output_dir,
            prefix=".fuelvision-",
            suffix=suffix,
            delete=False,
        )
    except OSError as error:
        raise TransformationError(
            f"Could not create temporary output in: {output_dir}"
        ) from error
    temporary_file.close()
    return Path(temporary_file.name)


def publish_output(temporary_path: Path, destination: Path) -> Tuple[str, str]:
    """Publish deterministic output without replacing conflicting content."""
    digest = calculate_sha256(temporary_path)
    try:
        status = copy_without_overwrite(temporary_path, destination, digest)
    except DestinationConflictError as error:
        raise OutputConflictError(str(error)) from error
    except IngestionError as error:
        raise TransformationError(str(error)) from error
    finally:
        temporary_path.unlink(missing_ok=True)
    return status, digest


def validate_output_destination(destination: Path, expected_digest: str) -> None:
    """Reject an existing destination whose content differs from the new output."""
    if not destination.exists():
        return
    try:
        existing_digest = calculate_sha256(destination)
    except IngestionError as error:
        raise TransformationError(
            f"Could not validate existing output: {destination}"
        ) from error
    if existing_digest != expected_digest:
        raise OutputConflictError(
            f"Destination already exists with different content: {destination}"
        )


def transform_file(
    source: Path, output_dir: Path = DEFAULT_PROCESSED_DIR
) -> Dict[str, object]:
    """Transform a raw ANP CSV and publish processed, rejected and manifest files."""
    source = source.expanduser().resolve()
    output_dir = output_dir.expanduser().resolve()
    validate_input_path(source)

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise TransformationError(
            f"Could not create processed output directory: {output_dir}"
        ) from error

    output_paths = build_output_paths(source, output_dir)
    processed_temp = create_temporary_path(output_dir, ".processed.csv")
    try:
        rejected_temp = create_temporary_path(output_dir, ".rejected.csv")
    except TransformationError:
        processed_temp.unlink(missing_ok=True)
        raise

    rows_read = 0
    accepted_count = 0
    rejected_count = 0
    duplicate_count = 0
    conflicting_duplicate_count = 0
    seen_business_keys: Dict[Tuple[str, str, str], Tuple[str, ...]] = {}

    LOGGER.info("transformation_started source=%s output_dir=%s", source, output_dir)
    try:
        with source.open(encoding="utf-8-sig", newline="") as source_file:
            reader = csv.DictReader(source_file, delimiter=";")
            validate_source_header(reader.fieldnames)

            with processed_temp.open(
                "w", encoding="utf-8", newline=""
            ) as processed_file:
                with rejected_temp.open(
                    "w", encoding="utf-8", newline=""
                ) as rejected_file:
                    processed_writer = csv.DictWriter(
                        processed_file,
                        fieldnames=PROCESSED_COLUMNS,
                        delimiter=";",
                        lineterminator="\n",
                    )
                    rejected_writer = csv.DictWriter(
                        rejected_file,
                        fieldnames=REJECTED_COLUMNS,
                        delimiter=";",
                        lineterminator="\n",
                    )
                    processed_writer.writeheader()
                    rejected_writer.writeheader()

                    for source_row_number, record in enumerate(reader, start=2):
                        rows_read += 1
                        processed, reasons = transform_record(record)
                        if record.get(None):
                            reasons.append("unexpected_extra_values")

                        if not reasons:
                            business_key = (
                                processed["retailer_cnpj"],
                                processed["product"],
                                processed["collection_date"],
                            )
                            signature = tuple(
                                processed[column] for column in PROCESSED_COLUMNS
                            )
                            previous_signature = seen_business_keys.get(business_key)
                            if previous_signature is not None:
                                if previous_signature == signature:
                                    reasons.append("duplicate_record")
                                    duplicate_count += 1
                                else:
                                    reasons.append("conflicting_duplicate")
                                    conflicting_duplicate_count += 1
                            else:
                                seen_business_keys[business_key] = signature

                        if reasons:
                            rejected_count += 1
                            rejected_writer.writerow(
                                {
                                    "source_row_number": source_row_number,
                                    "rejection_reasons": "|".join(reasons),
                                    **{
                                        column: record.get(column, "")
                                        for column in ANP_SOURCE_COLUMNS
                                    },
                                }
                            )
                        else:
                            accepted_count += 1
                            processed_writer.writerow(processed)
    except (OSError, UnicodeDecodeError, csv.Error, KeyError) as error:
        processed_temp.unlink(missing_ok=True)
        rejected_temp.unlink(missing_ok=True)
        raise TransformationError(f"Could not transform source CSV: {error}") from error
    except TransformationError:
        processed_temp.unlink(missing_ok=True)
        rejected_temp.unlink(missing_ok=True)
        raise

    processed_hash = calculate_sha256(processed_temp)
    rejected_hash = calculate_sha256(rejected_temp)

    manifest = {
        "transformation_version": TRANSFORMATION_VERSION,
        "source_file": source.name,
        "source_sha256": calculate_sha256(source),
        "rows_read": rows_read,
        "accepted_count": accepted_count,
        "rejected_count": rejected_count,
        "duplicate_count": duplicate_count,
        "conflicting_duplicate_count": conflicting_duplicate_count,
        "processed_file": output_paths["processed"].name,
        "processed_sha256": processed_hash,
        "rejected_file": output_paths["rejected"].name,
        "rejected_sha256": rejected_hash,
    }
    try:
        manifest_temp = create_temporary_path(output_dir, ".manifest.json")
    except TransformationError:
        processed_temp.unlink(missing_ok=True)
        rejected_temp.unlink(missing_ok=True)
        raise

    try:
        try:
            manifest_temp.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True)
                + "\n",
                encoding="utf-8",
            )
        except OSError as error:
            raise TransformationError(
                "Could not write transformation manifest."
            ) from error

        manifest_hash = calculate_sha256(manifest_temp)
        outputs = (
            (processed_temp, output_paths["processed"], processed_hash),
            (rejected_temp, output_paths["rejected"], rejected_hash),
            (manifest_temp, output_paths["manifest"], manifest_hash),
        )
        for _, destination, digest in outputs:
            validate_output_destination(destination, digest)

        statuses: List[str] = []
        published_paths: List[Path] = []
        try:
            for temporary_path, destination, _ in outputs:
                status, _ = publish_output(temporary_path, destination)
                statuses.append(status)
                if status == "created":
                    published_paths.append(destination)
        except (IngestionError, TransformationError):
            for published_path in published_paths:
                published_path.unlink(missing_ok=True)
            raise
    finally:
        processed_temp.unlink(missing_ok=True)
        rejected_temp.unlink(missing_ok=True)
        manifest_temp.unlink(missing_ok=True)

    status_set = set(statuses)
    result: Dict[str, object] = {
        **manifest,
        "status": "already_exists" if status_set == {"already_exists"} else "created",
        "processed_path": output_paths["processed"],
        "rejected_path": output_paths["rejected"],
        "manifest_path": output_paths["manifest"],
        "manifest_sha256": manifest_hash,
    }
    LOGGER.info(
        "transformation_completed status=%s rows=%s accepted=%s rejected=%s",
        result["status"],
        rows_read,
        accepted_count,
        rejected_count,
    )
    return result


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line interface for transformation."""
    parser = argparse.ArgumentParser(
        description="Transform a FuelVision raw CSV into processed and rejected outputs."
    )
    parser.add_argument("input_path", type=Path, help="Path to the raw ANP CSV file.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_PROCESSED_DIR,
        help=f"Processed output directory. Default: {DEFAULT_PROCESSED_DIR}",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=DEFAULT_TRANSFORMATION_LOG_PATH,
        help=f"Log file path. Default: {DEFAULT_TRANSFORMATION_LOG_PATH}",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Execute the transformation CLI and return a process exit code."""
    arguments = build_parser().parse_args(argv)
    try:
        configure_logging(arguments.log_file.expanduser().resolve())
        result = transform_file(arguments.input_path, arguments.output_dir)
    except (IngestionError, TransformationError) as error:
        LOGGER.error("transformation_failed error=%s", error)
        print(f"Transformation failed: {error}", file=sys.stderr)
        return 1

    print(f"status={result['status']}")
    print(f"rows_read={result['rows_read']}")
    print(f"accepted={result['accepted_count']}")
    print(f"rejected={result['rejected_count']}")
    print(f"processed={result['processed_path']}")
    print(f"rejected_file={result['rejected_path']}")
    print(f"manifest={result['manifest_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
