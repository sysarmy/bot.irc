import unittest

from src.help import help_message


class HelpTests(unittest.TestCase):
    def test_general_help_is_one_line_and_explains_detailed_help(self):
        message = help_message()
        self.assertNotIn("\n", message)
        self.assertTrue(
            message.endswith(
                "Ejecutá !help <comando> para ver más información. Ejemplo: !help karma"
            )
        )

    def test_command_help_is_case_insensitive(self):
        self.assertEqual(help_message("CLIMA"), help_message("clima"))

    def test_command_help_accepts_command_prefix(self):
        self.assertEqual(help_message("!karma"), help_message("karma"))

    def test_unknown_command_has_a_clear_response(self):
        self.assertIn("No hay ayuda", help_message("inexistente"))


if __name__ == "__main__":
    unittest.main()
