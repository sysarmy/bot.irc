from datetime import datetime, timezone
import unittest
from unittest.mock import AsyncMock, Mock, call, patch

from src.commands.ctxstatus import STATUSPAGE_SERVICES, estimated_uptime, statusfunctx, supported_services


class StatusTests(unittest.IsolatedAsyncioTestCase):
    def test_claude_is_supported(self):
        self.assertEqual(STATUSPAGE_SERVICES["claude"], ("Claude", "https://status.claude.com"))

    def test_donweb_is_supported(self):
        self.assertEqual(STATUSPAGE_SERVICES["donweb"], ("DonWeb", "https://status.donweb.com"))

    def test_uptime_merges_overlapping_incidents(self):
        now = datetime(2026, 8, 21, tzinfo=timezone.utc)
        incidents = [
            {"created_at": "2026-08-20T00:00:00Z", "resolved_at": "2026-08-20T02:00:00Z"},
            {"created_at": "2026-08-20T01:00:00Z", "resolved_at": "2026-08-20T03:00:00Z"},
        ]

        self.assertAlmostEqual(estimated_uptime(incidents, now), 99.583333, places=5)

    def test_ongoing_incident_counts_until_now(self):
        now = datetime(2026, 8, 21, tzinfo=timezone.utc)
        incidents = [{"created_at": "2026-08-20T12:00:00Z", "resolved_at": None}]

        self.assertAlmostEqual(estimated_uptime(incidents, now), 98.333333, places=5)

    async def test_unknown_service_lists_supported_services(self):
        ctx = unittest.mock.Mock()
        ctx.send = AsyncMock()

        await statusfunctx(ctx, "gitlab")

        ctx.send.assert_awaited_once_with(f"Servicio no soportado. Servicios disponibles: {supported_services()}")

    async def test_statuspage_service_uses_its_configured_endpoints(self):
        status_response = Mock()
        status_response.raise_for_status.return_value = None
        status_response.json.return_value = {"status": {"indicator": "none", "description": "All Systems Operational"}}
        incidents_response = Mock()
        incidents_response.raise_for_status.return_value = None
        incidents_response.json.return_value = {"incidents": []}
        ctx = unittest.mock.Mock()
        ctx.send = AsyncMock()

        with patch(
            "src.commands.ctxstatus.requests.get",
            side_effect=[status_response, incidents_response],
        ) as get:
            await statusfunctx(ctx, "Cloudflare")

        status_url = STATUSPAGE_SERVICES["cloudflare"][1]
        self.assertEqual(
            get.call_args_list,
            [
                call(f"{status_url}/api/v2/status.json", timeout=10),
                call(f"{status_url}/api/v2/incidents.json", timeout=10),
            ],
        )
        message = ctx.send.await_args.args[0]
        self.assertIn("Cloudflare: UP", message)
        self.assertIn("100.000%", message)


if __name__ == "__main__":
    unittest.main()
