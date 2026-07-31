"""Contract tests for Module 12 professional documentation and deployment."""

import re
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROFESSIONAL_DOCUMENTS = (
    "README.md",
    "SECURITY.md",
    "docs/INSTALACAO.md",
    "docs/DEPLOY.md",
    "docs/DEPLOY_VERCEL.md",
    "docs/REFERENCIA_API.md",
    "docs/DADOS_METRICAS_LIMITACOES.md",
    "docs/SEGURANCA.md",
    "docs/ACESSIBILIDADE.md",
    "docs/DEMONSTRACAO_PORTFOLIO.md",
    "docs/arquitetura/ARQUITETURA_ATUAL.md",
    "docs/ml/MODEL_CARD.md",
)
MARKDOWN_LINK = re.compile(r"\[[^]]+\]\(([^)]+)\)")


class ProfessionalizationContractTest(unittest.TestCase):
    def test_required_documents_and_real_screenshot_exist(self) -> None:
        for relative_path in PROFESSIONAL_DOCUMENTS:
            path = PROJECT_ROOT / relative_path
            self.assertTrue(path.is_file(), relative_path)
            self.assertGreater(path.stat().st_size, 100, relative_path)

        screenshot = PROJECT_ROOT / "docs" / "assets" / "fuelvision-dashboard.png"
        self.assertTrue(screenshot.is_file())
        self.assertGreater(screenshot.stat().st_size, 100_000)
        self.assertEqual(screenshot.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")

    def test_professional_markdown_has_no_broken_local_links(self) -> None:
        for relative_path in PROFESSIONAL_DOCUMENTS:
            markdown_path = PROJECT_ROOT / relative_path
            text = markdown_path.read_text(encoding="utf-8")
            for target in MARKDOWN_LINK.findall(text):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                clean_target = target.split("#", maxsplit=1)[0]
                linked_path = (markdown_path.parent / clean_target).resolve()
                self.assertTrue(
                    linked_path.exists(),
                    f"{relative_path} -> {target}",
                )

    def test_production_compose_requires_secrets_and_adds_gateway(self) -> None:
        compose = (PROJECT_ROOT / "compose.production.yaml").read_text(encoding="utf-8")

        self.assertIn("  gateway:\n", compose)
        self.assertIn("caddy:2.11.4-alpine", compose)
        self.assertIn("POSTGRES_PASSWORD:?", compose)
        self.assertIn("POSTGRES_ADMIN_PASSWORD:?", compose)
        self.assertIn("FUELVISION_DOMAIN:?", compose)
        self.assertGreaterEqual(compose.count("no-new-privileges:true"), 4)
        self.assertGreaterEqual(compose.count("read_only: true"), 4)
        self.assertIn("127.0.0.1:2019/healthz", compose)

    def test_gateway_and_nginx_define_browser_security_headers(self) -> None:
        caddy = (PROJECT_ROOT / "deploy" / "Caddyfile").read_text(encoding="utf-8")
        nginx = (PROJECT_ROOT / "frontend" / "nginx.conf").read_text(encoding="utf-8")

        for header in (
            "Content-Security-Policy",
            "Permissions-Policy",
            "Referrer-Policy",
            "X-Content-Type-Options",
            "X-Frame-Options",
        ):
            self.assertIn(header, caddy)
            self.assertIn(header, nginx)
        self.assertIn("Strict-Transport-Security", caddy)
        self.assertIn("reverse_proxy frontend:8080", caddy)

    def test_frontend_is_unprivileged_and_has_keyboard_landmarks(self) -> None:
        dockerfile = (PROJECT_ROOT / "frontend" / "Dockerfile").read_text(
            encoding="utf-8"
        )
        app = (PROJECT_ROOT / "frontend" / "src" / "App.tsx").read_text(
            encoding="utf-8"
        )

        self.assertIn("nginx-unprivileged:1.28.2-alpine", dockerfile)
        self.assertIn('className="skip-link"', app)
        self.assertIn('href="#main-content"', app)
        self.assertIn('id="main-content" tabIndex={-1}', app)

    def test_model_card_keeps_measured_result_and_restrictions(self) -> None:
        card = (PROJECT_ROOT / "docs" / "ml" / "MODEL_CARD.md").read_text(
            encoding="utf-8"
        )

        for required_text in (
            "0,527108",
            "0,571978",
            "O Ridge não superou o baseline",
            "50 observações",
            "não deve ser chamado de modelo de previsão de mercado",
        ):
            self.assertIn(required_text, card)

    def test_deploy_smoke_checks_dashboard_api_and_prediction(self) -> None:
        script = (PROJECT_ROOT / "scripts" / "deploy_smoke.sh").read_text(
            encoding="utf-8"
        )

        self.assertIn('"${BASE_URL}/"', script)
        self.assertIn("/api/prices/summary", script)
        self.assertIn("/api/predictions/model", script)
        self.assertIn("/api/predictions", script)
        self.assertIn("--connect-timeout", script)


if __name__ == "__main__":
    unittest.main()
