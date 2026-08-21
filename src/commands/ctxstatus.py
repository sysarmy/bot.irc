from datetime import datetime, timedelta, timezone

import requests


GITHUB_STATUS_URL = "https://www.githubstatus.com"
GITHUB_STATUS_API = f"{GITHUB_STATUS_URL}/api/v2/status.json"
GITHUB_INCIDENTS_API = f"{GITHUB_STATUS_URL}/api/v2/incidents.json"
WINDOW_DAYS = 30


def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def estimated_uptime(incidents: list[dict], now: datetime) -> float:
    """Estimate uptime as time without a published incident in the last 30 days."""
    now = now.astimezone(timezone.utc)
    window_start = now - timedelta(days=WINDOW_DAYS)
    intervals = []

    for incident in incidents:
        created_at = incident.get("created_at")
        if not created_at:
            continue
        start = max(parse_timestamp(created_at), window_start)
        resolved_at = incident.get("resolved_at")
        end = min(parse_timestamp(resolved_at), now) if resolved_at else now
        if start < end and end > window_start:
            intervals.append((start, end))

    intervals.sort()
    merged = []
    for start, end in intervals:
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)

    downtime = sum((end - start).total_seconds() for start, end in merged)
    window_seconds = timedelta(days=WINDOW_DAYS).total_seconds()
    return max(0.0, 100.0 * (window_seconds - downtime) / window_seconds)


async def statusfunctx(ctx, service: str):
    service = service.strip().lower()
    if service != "github":
        await ctx.send("Servicio no soportado. Servicios disponibles: github")
        return

    try:
        status_response = requests.get(GITHUB_STATUS_API, timeout=10)
        status_response.raise_for_status()
        incidents_response = requests.get(GITHUB_INCIDENTS_API, timeout=10)
        incidents_response.raise_for_status()

        status = status_response.json()["status"]
        incidents = incidents_response.json().get("incidents", [])
        uptime = estimated_uptime(incidents, datetime.now(timezone.utc))
        indicator = status.get("indicator", "unknown")
        state = "UP" if indicator == "none" else f"DEGRADADO ({status.get('description', 'estado desconocido')})"
        await ctx.send(
            f"GitHub: {state} - Uptime estimado ultimos 30 dias: {uptime:.3f}% "
            f"- Fuente: {GITHUB_STATUS_URL}"
        )
    except (requests.RequestException, KeyError, TypeError, ValueError):
        await ctx.send("No se pudo consultar el estado de GitHub. Intenta nuevamente mas tarde.")
