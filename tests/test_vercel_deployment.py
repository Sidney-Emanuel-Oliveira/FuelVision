"""Contract tests for the optional Vercel deployment profile."""

import json
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class VercelDeploymentContractTest(unittest.TestCase):
    def setUp(self) -> None:
        config_path = PROJECT_ROOT / "vercel.json"
        self.config = json.loads(config_path.read_text(encoding="utf-8"))

    def test_services_keep_frontend_api_and_prediction_in_one_project(self) -> None:
        services = self.config["services"]

        self.assertEqual(set(services), {"frontend", "backend", "prediction"})
        self.assertEqual(services["frontend"]["framework"], "vite")
        self.assertEqual(services["backend"]["runtime"], "container")
        self.assertEqual(services["prediction"]["runtime"], "container")
        self.assertEqual(
            services["backend"]["entrypoint"],
            "Dockerfile.vercel",
        )
        self.assertEqual(
            services["prediction"]["entrypoint"],
            "Dockerfile.vercel",
        )

    def test_prediction_service_is_private_and_bound_to_backend(self) -> None:
        backend = self.config["services"]["backend"]
        binding = backend["bindings"][0]
        public_services = {
            rewrite["destination"]["service"] for rewrite in self.config["rewrites"]
        }

        self.assertEqual(binding["service"], "prediction")
        self.assertEqual(binding["env"], "FUELVISION_PREDICTION_URL")
        self.assertNotIn("prediction", public_services)

    def test_public_routes_preserve_same_origin_api(self) -> None:
        rewrites = self.config["rewrites"]

        self.assertEqual(rewrites[0]["source"], "/api/(.*)")
        self.assertEqual(rewrites[0]["destination"]["service"], "backend")
        self.assertEqual(rewrites[-1]["source"], "/(.*)")
        self.assertEqual(rewrites[-1]["destination"]["service"], "frontend")

    def test_container_entrypoints_respect_vercel_port(self) -> None:
        for relative_path in (
            "backend/Dockerfile.vercel",
            "Dockerfile.vercel",
        ):
            dockerfile = (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")
            self.assertIn("${PORT:-80}", dockerfile, relative_path)
            self.assertIn("USER fuelvision", dockerfile, relative_path)

    def test_database_setup_uses_ignored_local_configuration(self) -> None:
        gitignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")
        script = (PROJECT_ROOT / "scripts" / "prepare_vercel_database.sh").read_text(
            encoding="utf-8"
        )

        self.assertIn(".env.*", gitignore)
        self.assertIn(".vercel/", gitignore)
        self.assertIn("deploy/.env.vercel", script)
        self.assertIn("validate_analytics.sh", script)
        self.assertNotIn("POSTGRES_PASSWORD=", script)

    def test_local_vercel_entrypoint_rewrites_only_loopback_binding(self) -> None:
        entrypoint = (
            PROJECT_ROOT / "backend" / "docker-entrypoint.vercel.sh"
        ).read_text(encoding="utf-8")

        self.assertIn('VERCEL_ENV:-}" = "development"', entrypoint)
        self.assertIn("http://127[.]0[.]0[.]1:", entrypoint)
        self.assertIn("http://host.docker.internal:", entrypoint)
        self.assertIn('java_bin="/opt/java/openjdk/bin/java"', entrypoint)
        self.assertIn('exec "$java_bin"', entrypoint)
        self.assertIn("-XX:TieredStopAtLevel=1", entrypoint)
        self.assertIn("-XX:SharedArchiveFile=/app/application.jsa", entrypoint)
        self.assertIn("-Dspring.main.lazy-initialization=true", entrypoint)
        self.assertIn("-Dspringdoc.api-docs.enabled=false", entrypoint)
        self.assertIn("-Dspringdoc.swagger-ui.enabled=false", entrypoint)
        self.assertIn("-jar /app/application.jar", entrypoint)

    def test_backend_uses_spring_boot_fast_start_layout(self) -> None:
        dockerfile = (PROJECT_ROOT / "backend" / "Dockerfile.vercel").read_text(
            encoding="utf-8"
        )

        self.assertIn("-Djarmode=tools", dockerfile)
        self.assertIn("--layers", dockerfile)
        self.assertIn("/build/extracted/dependencies/", dockerfile)
        self.assertIn("/build/extracted/application/", dockerfile)
        self.assertIn("-XX:ArchiveClassesAtExit=/app/application.jsa", dockerfile)
        self.assertIn("-Dspring.context.exit=onRefresh", dockerfile)

    def test_container_commands_do_not_depend_on_runtime_path(self) -> None:
        prediction_dockerfile = (PROJECT_ROOT / "Dockerfile.vercel").read_text(
            encoding="utf-8"
        )

        self.assertIn("/opt/venv/bin/python -m uvicorn", prediction_dockerfile)
        self.assertIn("/opt/venv/bin/python -c", prediction_dockerfile)


if __name__ == "__main__":
    unittest.main()
