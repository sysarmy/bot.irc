COMMAND_HELP = {
    "birras": "!birras - Muestra las proximas AdminBirras y eventos de Sysarmy.",
    "caucho": "!caucho - Muestra la tasa de caucion actual.",
    "clima": "!clima <ciudad> - Muestra el clima de una ciudad. Ejemplo: !clima Buenos Aires",
    "cripto": "!cripto - Muestra precios actuales de criptomonedas.",
    "dolar": "!dolar [pesos] - Muestra cotizaciones del dolar. Opcionalmente convierte un monto. Ejemplo: !dolar 50000",
    "euro": "!euro - Muestra la cotizacion actual del euro.",
    "feriadoar": "!feriadoar - Muestra los proximos feriados de Argentina.",
    "feriadocl": "!feriadocl - Muestra los proximos feriados de Chile.",
    "feriadoes": "!feriadoes - Muestra los proximos feriados de Espana.",
    "feriadomx": "!feriadomx - Muestra los proximos feriados de Mexico.",
    "feriadouy": "!feriadouy - Muestra los proximos feriados de Uruguay.",
    "fulbo": "!fulbo <liga> - Muestra resultados de futbol. Ligas: PL, BL1, PD, FL1 y SA. Ejemplo: !fulbo PL",
    "rank": "!rank - Muestra el ranking general de karma.",
    "karma": "!karma <palabra o usuario> - Consulta su karma. Ejemplo: !karma nachi",
    "kgivers": "!kgivers - Muestra quienes dieron mas karma.",
    "kgiven": "!kgiven <usuario> - Consulta cuanto karma dio un usuario. Ejemplo: !kgiven nachi",
    "pesos": "!pesos <monto> - Convierte pesos argentinos a dolares. Ejemplo: !pesos 10000",
    "q": "!q - Devuelve una cita aleatoria del historial.",
    "qadd": "!qadd <cita> - Agrega una cita al historial. Ejemplo: !qadd <nachi> esto queda para la posteridad",
    "qsearch": "!qsearch <texto> - Busca citas por texto o usuario. Ejemplo: !qsearch kubernetes",
    "subte": "!subte - Muestra el estado del Subte de Buenos Aires.",
    "underground": "!underground - Muestra el estado del Underground de Londres.",
    "ping": "!ping - Comprueba si el bot esta respondiendo.",
    "flip": "!flip - Tira una mesa. No requiere argumentos.",
    "shrug": "!shrug - Responde con el clasico encogimiento de hombros.",
    "help": "!help [comando] - Muestra la lista de comandos o ayuda detallada. Ejemplo: !help clima",
}


GENERAL_HELP = """Estos son los comandos disponibles en el bot de Sysarmy:
Economia: !caucho !cripto !dolar !euro !pesos | Servicios: !clima !fulbo !subte !underground | Feriados: !feriadoar !feriadocl !feriadoes !feriadomx !feriadouy | Karma: !rank !karma !kgivers !kgiven | Citas: !q !qadd !qsearch | Comunidad: !birras | Utilidades: !ping !flip !shrug
Ejecuta !help <comando> para ver mas informacion. Ejemplo: !help karma"""


def help_message(argument: str = "") -> str:
    command = argument.strip().lower().removeprefix("!")
    if not command:
        return GENERAL_HELP
    detail = COMMAND_HELP.get(command)
    if detail:
        return detail
    return f"No hay ayuda para '{command}'. Ejecuta !help para ver los comandos disponibles."
