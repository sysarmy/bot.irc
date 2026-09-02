from datetime import datetime
import aiohttp
from ratelimit import limits
import os
from dotenv import load_dotenv

quince_minutos = 900
load_dotenv()


# Limitamos las API calls por las dudas. Esta libreria es medio negra. Lo dejamos asi por ahora, Mariano del futuro lo va a hacer manual
@limits(calls=15, period=quince_minutos)
async def climafunctx(ctx, city):

    FechaActual = datetime.now()

    try:
        url = "https://api.weatherapi.com/v1/current.json"
        CLIMA_key = os.getenv("WEATHER_key")
        params = {"key": f"{CLIMA_key}", "q": city}

        # Llama a la API y trae la data
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params) as res:  # <-- Necesitamos la ciudad para checkear el clima en la API
                data = await res.json()
                if res.status != 200 or "error" in data:
                    await ctx.send(f"No reconozco la ubicacion: {city}")
                    return

                location = data["location"]["name"]
                country = data["location"]["country"]
                temp_c = data["current"]["temp_c"]
                feelslike_c = data["current"]["feelslike_c"]
                humidity = data["current"]["humidity"]

                # Log
                print(FechaActual)
                print(f"Se ha ejecutado el comando clima para {city}")

                await ctx.send(f"El clima en {location}, {country} es {temp_c} °C, sensación termica {feelslike_c} °C, humedad {humidity} %")

    except (aiohttp.ClientError, TimeoutError, KeyError, ValueError):

        # En caso de error en la API, se imprime el mensaje
        await ctx.send("Error en la API call - avisar a algun root")
        print("Error en la API")
