import unittest

from src.text import ascii_message


class OutgoingTextTests(unittest.TestCase):
    def test_transliterates_correct_utf8_accents(self):
        self.assertEqual(ascii_message("Proximos días en España"), "Proximos dias en Espana")

    def test_repairs_mojibake_before_transliterating(self):
        self.assertEqual(
            ascii_message("DÃ­a de la ConcepciÃ³n de MarÃ­a"),
            "Dia de la Concepcion de Maria",
        )

    def test_replaces_dashes_and_removes_emoji(self):
        self.assertEqual(ascii_message("La timba! 🚀 🌕 — ahora"), "La timba!   - ahora")

    def test_every_output_character_is_ascii(self):
        result = ascii_message("áéíóú ñ 🚀 — ‘texto’")
        self.assertTrue(result.isascii())

    def test_ascii_emoticons_survive_unchanged(self):
        self.assertEqual(ascii_message("(table flip) (/o_o)/  ====|____|"), "(table flip) (/o_o)/  ====|____|")
        self.assertEqual(ascii_message("\\_(o_o)_/"), "\\_(o_o)_/")


if __name__ == "__main__":
    unittest.main()
