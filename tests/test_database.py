"""Contract and PostgreSQL integration tests for Module 4."""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from pipeline.schema import PROCESSED_COLUMNS
from pipeline.transform_data import transform_file


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = PROJECT_ROOT / "data" / "samples" / "precos-combustiveis-amostra.csv"
SCHEMA_PATH = PROJECT_ROOT / "database" / "sql" / "001_create_schema.sql"
PREPARE_LOAD_PATH = PROJECT_ROOT / "database" / "sql" / "002_prepare_load.sql"
FINISH_LOAD_PATH = PROJECT_ROOT / "database" / "sql" / "002_finish_load.sql"
INITIAL_QUERIES_PATH = PROJECT_ROOT / "database" / "sql" / "003_initial_queries.sql"
LOAD_SCRIPT_PATH = PROJECT_ROOT / "database" / "scripts" / "load_processed.sh"


def read_local_environment() -> dict:
    """Read simple KEY=VALUE assignments from the ignored local .env file."""
    values = {}
    env_path = PROJECT_ROOT / ".env"
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        key, separator, value = stripped.partition("=")
        if not separator:
            raise ValueError(f"Invalid environment assignment: {line}")
        values[key] = value
    return values


class DatabaseContractTest(unittest.TestCase):
    def test_expected_database_files_exist(self) -> None:
        expected_paths = (
            PROJECT_ROOT / ".env.example",
            SCHEMA_PATH,
            PREPARE_LOAD_PATH,
            FINISH_LOAD_PATH,
            INITIAL_QUERIES_PATH,
            PROJECT_ROOT / "database" / "scripts" / "create_schema.sh",
            LOAD_SCRIPT_PATH,
            PROJECT_ROOT / "database" / "scripts" / "run_initial_queries.sh",
        )

        for path in expected_paths:
            self.assertTrue(path.is_file(), path)

    def test_environment_template_has_required_keys_and_no_real_password(self) -> None:
        template = (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8")

        for key in (
            "POSTGRES_HOST",
            "POSTGRES_PORT",
            "POSTGRES_DB",
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
            "POSTGRES_SSLMODE",
        ):
            self.assertIn(f"{key}=", template)
        self.assertIn("POSTGRES_PASSWORD=replace_with_a_local_password", template)

    def test_schema_defines_tables_relationships_and_business_key(self) -> None:
        schema = SCHEMA_PATH.read_text(encoding="utf-8")

        for table_name in (
            "regions",
            "states",
            "municipalities",
            "products",
            "retailers",
            "price_observations",
        ):
            self.assertIn(f"CREATE TABLE IF NOT EXISTS {table_name}", schema)
        self.assertIn("FOREIGN KEY (retailer_id)", schema)
        self.assertIn("FOREIGN KEY (product_id)", schema)
        self.assertIn("UNIQUE (retailer_id, product_id, collection_date)", schema)
        self.assertIn("CHECK (sale_price > 0)", schema)

    def test_loader_uses_transaction_staging_and_conflict_handling(self) -> None:
        preparation = PREPARE_LOAD_PATH.read_text(encoding="utf-8")
        finish = FINISH_LOAD_PATH.read_text(encoding="utf-8")
        loader = LOAD_SCRIPT_PATH.read_text(encoding="utf-8")

        self.assertIn("BEGIN;", preparation)
        self.assertIn("CREATE TEMPORARY TABLE staging_prices", preparation)
        self.assertIn("ON CONFLICT (cnpj) DO UPDATE", finish)
        self.assertIn("ON CONFLICT (retailer_id, product_id, collection_date)", finish)
        self.assertIn("COMMIT;", finish)
        self.assertIn(f'EXPECTED_HEADER="{";".join(PROCESSED_COLUMNS)}"', loader)


@unittest.skipUnless(
    os.environ.get("FUELVISION_RUN_DB_TESTS") == "1",
    "set FUELVISION_RUN_DB_TESTS=1 to run PostgreSQL integration tests",
)
class DatabaseIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.local_values = read_local_environment()
        postgres_bin = cls.local_values.get("POSTGRES_BIN", "")
        if postgres_bin:
            cls.psql = Path(postgres_bin) / "psql"
        else:
            psql_from_path = shutil.which("psql")
            if psql_from_path is None:
                raise unittest.SkipTest("psql was not found in PATH")
            cls.psql = Path(psql_from_path)
        if not cls.psql.is_file():
            raise unittest.SkipTest(f"psql was not found: {cls.psql}")

        cls.database_environment = os.environ.copy()
        cls.database_environment.update(
            {
                "PGHOST": cls.local_values["POSTGRES_HOST"],
                "PGPORT": cls.local_values["POSTGRES_PORT"],
                "PGDATABASE": cls.local_values["POSTGRES_DB"],
                "PGUSER": cls.local_values["POSTGRES_USER"],
                "PGPASSWORD": cls.local_values.get("POSTGRES_PASSWORD", ""),
                "PGSSLMODE": cls.local_values["POSTGRES_SSLMODE"],
            }
        )

        cls.temporary_directory = tempfile.TemporaryDirectory()
        processed_dir = Path(cls.temporary_directory.name) / "processed"
        cls.processed_path = transform_file(SAMPLE_PATH, processed_dir)[
            "processed_path"
        ]
        cls._run_psql_file(SCHEMA_PATH)
        cls._run_loader()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary_directory.cleanup()

    @classmethod
    def _run_command(cls, command, check=True):
        return subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            env=cls.database_environment,
            capture_output=True,
            text=True,
            check=check,
        )

    @classmethod
    def _run_psql_file(cls, sql_path: Path):
        return cls._run_command(
            [
                str(cls.psql),
                "--no-psqlrc",
                "--set=ON_ERROR_STOP=1",
                f"--file={sql_path}",
            ]
        )

    @classmethod
    def _run_psql_command(cls, sql: str, check=True):
        return cls._run_command(
            [
                str(cls.psql),
                "--no-psqlrc",
                "--set=ON_ERROR_STOP=1",
                "--tuples-only",
                "--no-align",
                f"--command={sql}",
            ],
            check=check,
        )

    @classmethod
    def _run_loader(cls):
        return cls._run_command([str(LOAD_SCRIPT_PATH), str(cls.processed_path)])

    def test_database_uses_a_dedicated_non_superuser(self) -> None:
        result = self._run_psql_command(
            "SELECT current_user || '|' || rolsuper "
            "FROM pg_roles WHERE rolname = current_user;"
        )

        self.assertEqual(result.stdout.strip(), "fuelvision_app|false")

    def test_reference_and_loaded_table_counts(self) -> None:
        result = self._run_psql_command(
            "SELECT "
            "(SELECT count(*) FROM fuelvision.regions), "
            "(SELECT count(*) FROM fuelvision.states), "
            "(SELECT count(*) FROM fuelvision.municipalities), "
            "(SELECT count(*) FROM fuelvision.products), "
            "(SELECT count(*) FROM fuelvision.retailers), "
            "(SELECT count(*) FROM fuelvision.price_observations);"
        )

        self.assertEqual(result.stdout.strip(), "5|27|16|6|27|60")

    def test_relationship_query_returns_every_observation(self) -> None:
        result = self._run_psql_command(
            "SELECT count(*) "
            "FROM fuelvision.price_observations AS observations "
            "JOIN fuelvision.retailers ON retailers.id = observations.retailer_id "
            "JOIN fuelvision.municipalities "
            "ON municipalities.id = retailers.municipality_id "
            "JOIN fuelvision.states ON states.code = municipalities.state_code "
            "JOIN fuelvision.products ON products.id = observations.product_id;"
        )

        self.assertEqual(result.stdout.strip(), "60")

    def test_repeated_load_is_idempotent(self) -> None:
        before = self._run_psql_command(
            "SELECT count(*) || '|' || max(updated_at)::text "
            "FROM fuelvision.retailers;"
        ).stdout.strip()

        self._run_loader()

        after = self._run_psql_command(
            "SELECT count(*) || '|' || max(updated_at)::text "
            "FROM fuelvision.retailers;"
        ).stdout.strip()
        observation_count = self._run_psql_command(
            "SELECT count(*) FROM fuelvision.price_observations;"
        ).stdout.strip()
        self.assertEqual(after, before)
        self.assertEqual(observation_count, "60")

    def test_loader_rejects_an_unexpected_header(self) -> None:
        invalid_path = Path(self.temporary_directory.name) / "invalid-header.csv"
        invalid_path.write_text("unexpected;header\nvalue;value\n", encoding="utf-8")

        result = self._run_command(
            [str(LOAD_SCRIPT_PATH), str(invalid_path)],
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("header does not match", result.stderr)

    def test_negative_sale_price_is_rejected(self) -> None:
        result = self._run_psql_command(
            "INSERT INTO fuelvision.price_observations "
            "(retailer_id, product_id, collection_date, sale_price) "
            "SELECT retailer_id, product_id, DATE '2099-01-01', -1 "
            "FROM fuelvision.price_observations LIMIT 1;",
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("price_observations_sale_price_check", result.stderr)

    def test_unknown_retailer_is_rejected_by_foreign_key(self) -> None:
        result = self._run_psql_command(
            "INSERT INTO fuelvision.price_observations "
            "(retailer_id, product_id, collection_date, sale_price) "
            "SELECT -1, id, DATE '2099-01-02', 1 "
            "FROM fuelvision.products LIMIT 1;",
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("price_observations_retailer_fk", result.stderr)

    def test_duplicated_business_key_is_rejected(self) -> None:
        result = self._run_psql_command(
            "INSERT INTO fuelvision.price_observations "
            "(retailer_id, product_id, collection_date, sale_price, purchase_price) "
            "SELECT retailer_id, product_id, collection_date, sale_price, purchase_price "
            "FROM fuelvision.price_observations LIMIT 1;",
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("price_observations_business_key_uk", result.stderr)

    def test_initial_queries_execute_successfully(self) -> None:
        result = self._run_psql_file(INITIAL_QUERIES_PATH)

        self.assertIn("price_observations", result.stdout)
        self.assertIn("retailer_cnpj", result.stdout)


if __name__ == "__main__":
    unittest.main()
