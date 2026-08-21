import os
import sqlite3
import tempfile
import unittest

import src.database
import src.karma


class KarmaTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        path = os.path.join(self.tempdir.name, "karma.db")
        src.database.KARMA_DB = path
        src.database.QUOTES_DB = os.path.join(self.tempdir.name, "quotes.db")
        src.karma.karma_database = src.database.karma_database
        src.database.initialize_databases()

    def tearDown(self):
        self.tempdir.cleanup()

    def test_existing_karma_database_is_updated(self):
        with sqlite3.connect(src.database.KARMA_DB) as database:
            database.execute(
                "INSERT INTO karma (palabra, karmavalue, isuser, karmagiven) VALUES ('linux', 41, 'NO', 0)"
            )

        replies = src.karma.process_karma("linux++", "emilio")

        with sqlite3.connect(src.database.KARMA_DB) as database:
            value = database.execute(
                "SELECT karmavalue FROM karma WHERE palabra = 'linux'"
            ).fetchone()[0]
            given = database.execute(
                "SELECT karmagiven FROM karma WHERE palabra = 'emilio' AND isuser = 'YES'"
            ).fetchone()[0]
        self.assertEqual(value, 42)
        self.assertEqual(given, 1)
        self.assertEqual(replies, ["+1 karma para linux. Current karma is: 42"])

    def test_non_karma_text_is_ignored(self):
        self.assertEqual(src.karma.process_karma("hello from IRC", "emilio"), [])


if __name__ == "__main__":
    unittest.main()
