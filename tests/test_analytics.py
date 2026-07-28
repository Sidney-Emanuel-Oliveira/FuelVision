"""Contract and PostgreSQL integration tests for Module 5 analytics."""

import os
import unittest

from postgres_test_support import (
    PROJECT_ROOT,
    create_processed_fixture,
    run_project_command,
)

CREATE_VIEWS_PATH = PROJECT_ROOT / "database" / "sql" / "004_create_analytics_views.sql"
REPORT_PATH = PROJECT_ROOT / "database" / "sql" / "005_analysis_report.sql"
VALIDATION_PATH = PROJECT_ROOT / "database" / "sql" / "006_validate_analytics.sql"
CREATE_SCHEMA_SCRIPT = PROJECT_ROOT / "database" / "scripts" / "create_schema.sh"
LOAD_SCRIPT = PROJECT_ROOT / "database" / "scripts" / "load_processed.sh"
CREATE_VIEWS_SCRIPT = (
    PROJECT_ROOT / "database" / "scripts" / "create_analytics_views.sh"
)
RUN_ANALYTICS_SCRIPT = PROJECT_ROOT / "database" / "scripts" / "run_analytics.sh"
VALIDATE_ANALYTICS_SCRIPT = (
    PROJECT_ROOT / "database" / "scripts" / "validate_analytics.sh"
)


class AnalyticsContractTest(unittest.TestCase):
    def test_expected_analytics_files_exist(self) -> None:
        for path in (
            CREATE_VIEWS_PATH,
            REPORT_PATH,
            VALIDATION_PATH,
            CREATE_VIEWS_SCRIPT,
            RUN_ANALYTICS_SCRIPT,
            VALIDATE_ANALYTICS_SCRIPT,
        ):
            self.assertTrue(path.is_file(), path)

    def test_four_reusable_analytics_views_are_defined(self) -> None:
        definitions = CREATE_VIEWS_PATH.read_text(encoding="utf-8")

        for view_name in (
            "product_price_summary",
            "state_price_summary",
            "municipality_price_summary",
            "daily_price_history",
        ):
            self.assertIn(f"CREATE OR REPLACE VIEW {view_name}", definitions)

    def test_views_calculate_required_descriptive_indicators(self) -> None:
        definitions = CREATE_VIEWS_PATH.read_text(encoding="utf-8")

        self.assertGreaterEqual(definitions.count("count(*) AS observation_count"), 4)
        self.assertGreaterEqual(definitions.count("avg(observations.sale_price)"), 4)
        self.assertGreaterEqual(definitions.count("min(observations.sale_price)"), 4)
        self.assertGreaterEqual(definitions.count("max(observations.sale_price)"), 4)
        self.assertGreaterEqual(definitions.count("GROUP BY"), 4)

    def test_report_supports_location_product_and_date_filters(self) -> None:
        report = REPORT_PATH.read_text(encoding="utf-8")

        for filter_name in (
            "product_filter",
            "state_filter",
            "municipality_filter",
            "start_date_filter",
            "end_date_filter",
        ):
            self.assertIn(filter_name, report)
        self.assertIn("WHERE", report)
        self.assertIn("GROUP BY", report)

    def test_help_does_not_require_database_configuration(self) -> None:
        environment = os.environ.copy()
        environment["FUELVISION_ENV_FILE"] = "/path/that/does/not/exist"

        result = run_project_command(
            [str(RUN_ANALYTICS_SCRIPT), "--help"],
            environment=environment,
        )

        self.assertIn("Usage:", result.stdout)


@unittest.skipUnless(
    os.environ.get("FUELVISION_RUN_DB_TESTS") == "1",
    "set FUELVISION_RUN_DB_TESTS=1 to run PostgreSQL integration tests",
)
class AnalyticsIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary_directory, cls.processed_path = create_processed_fixture()
        cls._run([str(CREATE_SCHEMA_SCRIPT)])
        cls._run([str(LOAD_SCRIPT), str(cls.processed_path)])
        cls._run([str(CREATE_VIEWS_SCRIPT)])

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary_directory.cleanup()

    @classmethod
    def _run(cls, command, check=True):
        return run_project_command(
            command,
            check=check,
        )

    def test_view_creation_is_repeatable(self) -> None:
        result = self._run([str(CREATE_VIEWS_SCRIPT)])

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.count("CREATE VIEW"), 4)

    def test_sql_validation_confirms_all_sixty_observations(self) -> None:
        result = self._run([str(VALIDATE_ANALYTICS_SCRIPT)])

        self.assertIn("analytics_validation_passed", result.stdout)
        self.assertIn("60", result.stdout)
        self.assertIn("39", result.stdout)
        self.assertIn("42", result.stdout)
        self.assertIn("14", result.stdout)

    def test_unfiltered_report_contains_verified_product_indicators(self) -> None:
        result = self._run([str(RUN_ANALYTICS_SCRIPT)])

        self.assertIn("=== PRODUCT SUMMARY ===", result.stdout)
        self.assertIn("GASOLINA COMUM", result.stdout)
        self.assertIn("6.594", result.stdout)
        self.assertIn("GNV", result.stdout)
        self.assertIn("4.489", result.stdout)

    def test_combined_filters_return_the_verified_macae_gnv_group(self) -> None:
        result = self._run(
            [
                str(RUN_ANALYTICS_SCRIPT),
                "--product",
                "GNV",
                "--state",
                "RJ",
                "--municipality",
                "MACAE",
                "--start-date",
                "2026-01-01",
                "--end-date",
                "2026-01-07",
            ]
        )

        self.assertIn("MACAE", result.stdout)
        self.assertIn("4.935", result.stdout)
        self.assertIn("4.880", result.stdout)
        self.assertIn("4.990", result.stdout)
        self.assertNotIn("GASOLINA", result.stdout)

    def test_unknown_filter_option_is_rejected(self) -> None:
        result = self._run(
            [str(RUN_ANALYTICS_SCRIPT), "--unknown", "value"],
            check=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("Unknown option", result.stderr)


if __name__ == "__main__":
    unittest.main()
