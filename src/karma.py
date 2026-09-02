import re

from src.database import karma_database

KARMA_TOKEN = re.compile(r"^([a-zA-Z0-9_\-\[\]\\`^{}|ñÑáéíóúÁÉÍÓÚ][a-zA-Z0-9_+\-\[\]\\`^{}|ñÑáéíóúÁÉÍÓÚ]*)(\+\+|--)[,.!?;:]*$")


def process_karma(message: str, giver: str) -> list[str]:
    """Apply word++/word-- operations using the legacy karma table."""
    replies = []
    for token in message.split():
        match = KARMA_TOKEN.match(token)
        if not match:
            continue

        subject, operation = match.groups()
        delta = 1 if operation == "++" else -1
        subject = subject.lower()
        giver = giver.lower()

        with karma_database() as database:
            cursor = database.cursor()
            cursor.execute(
                "SELECT karmavalue FROM karma WHERE LOWER(palabra) = ?",
                (subject,),
            )
            row = cursor.fetchone()
            if row:
                cursor.execute(
                    "UPDATE karma SET karmavalue = karmavalue + ? WHERE LOWER(palabra) = ?",
                    (delta, subject),
                )
            else:
                cursor.execute(
                    "INSERT INTO karma (palabra, karmavalue, isuser, karmagiven) VALUES (?, ?, 'NO', 0)",
                    (subject, delta),
                )

            cursor.execute(
                "SELECT karmagiven FROM karma WHERE LOWER(palabra) = ? AND isuser = 'YES'",
                (giver,),
            )
            giver_row = cursor.fetchone()
            if giver_row:
                cursor.execute(
                    "UPDATE karma SET karmagiven = karmagiven + 1 WHERE LOWER(palabra) = ? AND isuser = 'YES'",
                    (giver,),
                )
            else:
                cursor.execute(
                    "INSERT INTO karma (palabra, karmavalue, isuser, karmagiven) VALUES (?, 0, 'YES', 1)",
                    (giver,),
                )

            cursor.execute(
                "SELECT karmavalue FROM karma WHERE LOWER(palabra) = ?",
                (subject,),
            )
            current = cursor.fetchone()[0]
        sign = "+1" if delta > 0 else "-1"
        replies.append(f"{sign} karma para {subject}. Current karma is: {current}")
    return replies
