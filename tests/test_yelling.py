import unittest
from unittest.mock import patch

from src.bridge import message_identity
from src.yelling import has_lowercase_word, random_response


class YellingTests(unittest.TestCase):
    def test_detects_lowercase_words(self):
        self.assertTrue(has_lowercase_word("esto NO ES YELLING"))

    def test_all_caps_is_allowed(self):
        self.assertFalse(has_lowercase_word("ESTO SI ES YELLING!!!"))

    def test_urls_and_colon_emojis_are_ignored(self):
        self.assertFalse(has_lowercase_word("MIRA https://example.com/foo :party_parrot:"))

    def test_relay_prefix_is_removed_before_yelling_check(self):
        author, content = message_identity("nbot", "nbot", "<lowercase-user> TODO EN MAYUSCULAS", {"nbot"})
        self.assertEqual(author, "lowercase-user")
        self.assertFalse(has_lowercase_word(content))

    @patch("src.yelling.random.choice", return_value="LAS MAYUSCULAS!")
    def test_returns_a_legacy_response(self, choice):
        self.assertEqual(random_response(), "LAS MAYUSCULAS!")
        choice.assert_called_once()


if __name__ == "__main__":
    unittest.main()
