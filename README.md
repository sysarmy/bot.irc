# Bot IRC BOFH

Versión exclusiva para IRC del bot BOFH de Sysarmy. Este repositorio es la migración del histórico repositorio [sysarmy/bot.ai](https://github.com/sysarmy/bot.ai): conserva las funcionalidades de IRC y deja afuera las integraciones específicas de Discord.

¡Las contribuciones son bienvenidas! Si encontrás un problema o querés proponer una mejora, abrí un issue o mandá un pull request.

El bot escucha todos los `PRIVMSG`, ejecuta comandos solamente cuando el mensaje empieza con `!` y mantiene el karma de texto (`palabra++` y `palabra--`) usando el esquema existente de `db/karma.db`.

Los comandos slash de Discord, reacciones, sincronización de miembros, embeds, operaciones del foro de empleos y publicación de RSS en Discord quedaron intencionalmente fuera de este proyecto.

## Ejecutarlo con Docker Compose

1. Copiá `.env.example` a `.env` y configurá la conexión a IRC.
2. Copiá los archivos existentes `karma.db` y, opcionalmente, `quotes.db` dentro de `db/`.
3. Iniciá el bot:

   ```sh
   docker compose up --build -d
   docker compose logs -f bot
   ```

Se monta el directorio completo `db/` en `/app/db`; las actualizaciones de SQLite persisten en el host. Si falta una base de datos, el bot crea una vacía compatible.
`main.py` y `src/` también se montan como solo lectura, así que después de traer cambios de código solo hace falta reiniciar el bot:

```sh
git pull
docker compose restart bot
```

Reconstruí con `docker compose up --build -d` solamente cuando cambien `requirements.txt` o el Dockerfile.
En Linux, configurá `PUID` y `PGID` en `.env` con el propietario del directorio `db/` para que SQLite pueda escribir.

Para conectarte a varios canales, listalos separados por comas en `.env`:

```dotenv
IRC_CHANNELS="#sysarmy,#sysarmy-offtopic,#jobs"
```

El bot entra a todos los canales indicados y responde en el canal donde recibió cada comando.

## Operación en Libera.Chat

Usá TLS y SASL, registrá una cuenta separada para el bot y configurá `IRC_REALNAME` para identificarlo claramente e indicar cómo contactar a quien lo administra. Pedí permiso a los operadores de cada canal configurado antes de agregarlo a `IRC_CHANNELS`.

El cliente responde a los pings del servidor aun cuando las APIs de comandos estén lentas, detecta conexiones silenciosas, se reconecta con backoff exponencial y jitter, y vuelve a entrar a los canales configurados luego de perder la conexión. Intencionalmente no intenta volver a entrar de inmediato si un operador lo expulsa. Los mensajes salientes se serializan a razón de uno cada 2,1 segundos para respetar el límite habitual de Libera.Chat.

## Identidad y karma

Cuando el servidor soporta `account-tag` de IRCv3, se registra el nombre de la cuenta autenticada como quien otorgó el karma. De lo contrario, el bot usa el nick actual. Por eso se recomienda SASL.

No ejecutes este bot con el mismo nick que una instancia conectada de Matterbridge: los nicks de IRC tienen que ser únicos. Muchas redes permiten varias conexiones simultáneas de una misma cuenta NickServ/SASL con nicks distintos, aunque depende de la política de cada red.

Se soportan los mensajes de Matterbridge con el formato `<usuario> !comando` cuando provienen de un nick de bridge configurado. `IRC_BRIDGE_NICKS` es una lista separada por comas y su valor predeterminado es `nbot`; el nombre de usuario reenviado se usa como identidad para comandos y karma.

## Canal de gritos

`IRC_YELLING_CHANNELS` es una lista separada por comas cuyo valor predeterminado es `#sysarmy-yelling`. Los mensajes que contienen palabras en minúscula reciben un recordatorio aleatorio en mayúsculas. Se ignoran las URLs y los tokens `:emoji:`. Los mensajes de Matterbridge se verifican luego de extraer el nombre de usuario y el contenido de Discord o Slack.

## Comandos

Ejecutá `!help` para ver la lista actual. Los comandos migrados incluyen `birras`, `caucho`, `clima`, `cripto`, `dolar`, `euro`, comandos de feriados por país, `fulbo`, comandos de karma y ranking, conversión de pesos, citas, `subte`, `underground` y utilidades pequeñas.
