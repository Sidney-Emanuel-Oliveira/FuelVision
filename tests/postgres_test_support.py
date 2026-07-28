"""Shared fixtures and subprocess execution for PostgreSQL integration tests."""

import subprocess
import tempfile
from pathlib import Path
from typing import Mapping, Optional, Sequence, Tuple

from pipeline.transform_data import transform_file

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = PROJECT_ROOT / "data" / "samples" / "precos-combustiveis-amostra.csv"


def create_processed_fixture() -> Tuple[tempfile.TemporaryDirectory, Path]:
    """Create an isolated processed CSV and return its owner and path."""
    temporary_directory = tempfile.TemporaryDirectory()
    processed_dir = Path(temporary_directory.name) / "processed"
    processed_path = transform_file(SAMPLE_PATH, processed_dir)["processed_path"]
    return temporary_directory, processed_path


def run_project_command(
    command: Sequence[str],
    *,
    check: bool = True,
    environment: Optional[Mapping[str, str]] = None,
) -> subprocess.CompletedProcess:
    """Run a project command with consistent capture and working directory."""
    return subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=check,
    )
