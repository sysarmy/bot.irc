import os
import sqlite3
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

from src.commands.ctxkarma import karmagiversuserfunctx, karmawordfunctx


REAL_CONNECT = sqlite3.connect


class KarmaCommandTests(unittest.IsolatedAsyncioTestCase):
    async def test_lookup_is_case_insensitive_with_legacy_schema(self):
        with tempfile.TemporaryDirectory() as tempdir:
            database_path = os.path.join(tempdir, "karma.db")
            with REAL_CONNECT(database_path) as database:
                database.execute(
                    "CREATE TABLE karma (palabra TEXT, karmavalue INTEGER, isuser TEXT, karmagiven INTEGER)"
                )
                database.execute(
                    "INSERT INTO karma VALUES ('Nachi', 42, 'YES', 7)"
                )

            ctx = unittest.mock.Mock()
            ctx.send = AsyncMock()
            with patch(
                "src.commands.ctxkarma.sqlite3.connect",
                side_effect=lambda _path: REAL_CONNECT(database_path),
            ):
                await karmawordfunctx(ctx, "nachi")
                await karmawordfunctx(ctx, "Nachi")

            self.assertEqual(
                ctx.send.await_args_list,
                [
                    unittest.mock.call("**nachi** tiene 42 karma."),
                    unittest.mock.call("**Nachi** tiene 42 karma."),
                ],
            )

    async def test_kgiven_lookup_is_case_insensitive_with_legacy_schema(self):
        with tempfile.TemporaryDirectory() as tempdir:
            database_path = os.path.join(tempdir, "karma.db")
            with REAL_CONNECT(database_path) as database:
                database.execute(
                    "CREATE TABLE karma (palabra TEXT, karmavalue INTEGER, isuser TEXT, karmagiven INTEGER)"
                )
                database.execute(
                    "INSERT INTO karma VALUES ('Nachichuri', 0, 'YES', 7)"
                )

            ctx = unittest.mock.Mock()
            ctx.send = AsyncMock()
            with patch(
                "src.commands.ctxkarma.sqlite3.connect",
                side_effect=lambda _path: REAL_CONNECT(database_path),
            ):
                await karmagiversuserfunctx(ctx, "nachichuri")
                await karmagiversuserfunctx(ctx, "Nachichuri")
                await karmagiversuserfunctx(ctx, "NACHICHURI")

            self.assertEqual(
                [call.args[0] for call in ctx.send.await_args_list],
                [
                    "**nachichuri** tiene 7 karmagiven.",
                    "**Nachichuri** tiene 7 karmagiven.",
                    "**NACHICHURI** tiene 7 karmagiven.",
                ],
            )


if __name__ == "__main__":
    unittest.main()
