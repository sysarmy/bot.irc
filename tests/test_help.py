import unittest

from src.help import REQUIRED_ARGUMENTS, help_message, missing_argument_message


class HelpTests(unittest.TestCase):
    def test_general_help_has_exactly_three_ascii_messages(self):
        message = help_message()
        self.assertEqual(len(message.splitlines()), 3)
        self.assertTrue(message.isascii())
        self.assertEqual(
            message.splitlines()[-1],
            "Ejecuta !help <comando> para ver mas informacion. Ejemplo: !help karma",
        )

    def test_command_help_is_case_insensitive(self):
        self.assertEqual(help_message("CLIMA"), help_message("clima"))

    def test_command_help_accepts_command_prefix(self):
        self.assertEqual(help_message("!karma"), help_message("karma"))

    def test_all_detailed_help_is_ascii(self):
        from src.help import COMMAND_HELP

        self.assertTrue(all(message.isascii() for message in COMMAND_HELP.values()))

    def test_unknown_command_has_a_clear_response(self):
        self.assertIn("No hay ayuda", help_message("inexistente"))

    def test_required_commands_identify_the_missing_argument(self):
        for command, argument in REQUIRED_ARGUMENTS.items():
            self.assertEqual(
                missing_argument_message(command),
                f"Falta el argumento <{argument}>. Uso: !{command} <{argument}>",
            )


if __name__ == "__main__":
    unittest.main()
