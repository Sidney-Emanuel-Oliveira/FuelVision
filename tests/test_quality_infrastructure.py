"""Contract tests for the Module 11 quality and container configuration."""

import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class QualityInfrastructureContractTest(unittest.TestCase):
    def test_compose_defines_four_services_and_health_order(self) -> None:
        compose = (PROJECT_ROOT / "compose.yaml").read_text(encoding="utf-8")

        for service in ("postgres", "prediction", "backend", "frontend"):
            self.assertIn(f"  {service}:\n", compose)
        self.assertGreaterEqual(compose.count("condition: service_healthy"), 3)
        self.assertIn("fuelvision_postgres_data:", compose)
        self.assertIn("127.0.0.1:", compose)

    def test_each_application_image_has_a_health_check(self) -> None:
        for relative_path in (
            "ml/Dockerfile",
            "backend/Dockerfile",
            "frontend/Dockerfile",
        ):
            dockerfile = (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")
            self.assertIn("HEALTHCHECK", dockerfile, relative_path)

    def test_database_image_creates_a_restricted_application_role(self) -> None:
        role_sql = (
            PROJECT_ROOT / "database" / "sql" / "docker_create_role.sql"
        ).read_text(encoding="utf-8")
        init_script = (
            PROJECT_ROOT / "database" / "docker" / "init-fuelvision.sh"
        ).read_text(encoding="utf-8")

        self.assertIn("NOSUPERUSER", role_sql)
        self.assertIn("NOCREATEDB", role_sql)
        self.assertIn("NOCREATEROLE", role_sql)
        self.assertIn("001_create_schema.sql", init_script)
        self.assertIn("004_create_analytics_views.sql", init_script)

    def test_docker_context_excludes_local_and_generated_files(self) -> None:
        dockerignore = (PROJECT_ROOT / ".dockerignore").read_text(encoding="utf-8")

        for ignored_path in (
            ".env",
            ".venv",
            "frontend/node_modules",
            "data/raw",
            "data/processed",
            "ml/artifacts",
            "docs/aprendizado",
        ):
            self.assertIn(ignored_path, dockerignore)

    def test_workflow_runs_quality_builds_and_smoke_tests(self) -> None:
        workflow = (PROJECT_ROOT / ".github" / "workflows" / "quality.yml").read_text(
            encoding="utf-8"
        )

        required_commands = (
            "ruff check",
            "shellcheck",
            "unittest discover",
            "backend/scripts/test.sh --with-postgres",
            "npm --prefix frontend test",
            "compose.production.yaml build",
            "compose.production.yaml up --detach --wait",
            "deploy_smoke.sh http://localhost:8088",
            "compose.production.yaml down --volumes",
        )
        for command in required_commands:
            self.assertIn(command, workflow)

    def test_quality_script_keeps_all_existing_barriers(self) -> None:
        quality_script = (PROJECT_ROOT / "scripts" / "quality.sh").read_text(
            encoding="utf-8"
        )

        for command in (
            "sys.version_info < (3, 11)",
            "ruff check",
            "--config ml/pyproject.toml",
            "ruff format --check",
            "unittest discover",
            "backend/scripts/test.sh",
            "mvn -f backend/pom.xml package",
            "npm --prefix frontend run lint",
            "npm --prefix frontend test",
            "npm --prefix frontend run build",
            "git diff --check",
        ):
            self.assertIn(command, quality_script)


if __name__ == "__main__":
    unittest.main()
