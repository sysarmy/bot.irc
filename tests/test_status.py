from datetime import datetime, timezone
import unittest
from unittest.mock import AsyncMock

from src.commands.ctxstatus import estimated_uptime, statusfunctx


class StatusTests(unittest.IsolatedAsyncioTestCase):
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

    async def test_only_github_is_supported(self):
        ctx = unittest.mock.Mock()
        ctx.send = AsyncMock()

        await statusfunctx(ctx, "gitlab")

        ctx.send.assert_awaited_once_with(
            "Servicio no soportado. Servicios disponibles: github"
        )


if __name__ == "__main__":
    unittest.main()
