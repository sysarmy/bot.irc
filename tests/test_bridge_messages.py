import unittest

from src.bridge import message_identity


class BridgeMessageTests(unittest.TestCase):
    def test_extracts_author_and_command_from_configured_bridge(self):
        self.assertEqual(
            message_identity("nbot", "nbot", "<Nachi> !ping", {"nbot"}),
            ("Nachi", "!ping"),
        )

    def test_extracts_regular_relayed_chat(self):
        self.assertEqual(
            message_identity("nbot", "nbot", "<user3> asd", {"nbot"}),
            ("user3", "asd"),
        )

    def test_does_not_parse_unconfigured_irc_users(self):
        self.assertEqual(
            message_identity("someone", "someone", "<Nachi> !ping", {"nbot"}),
            ("someone", "<Nachi> !ping"),
        )

    def test_bridge_nick_matching_is_case_insensitive(self):
        self.assertEqual(
            message_identity("NBot", "account-name", "<user2> !ping", {"nbot"}),
            ("user2", "!ping"),
        )


if __name__ == "__main__":
    unittest.main()
