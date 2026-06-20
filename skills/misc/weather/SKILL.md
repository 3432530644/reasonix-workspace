---
name: weather
description: Get current weather, forecasts, and weather info for any city worldwide. No API key required. Supports city name, airport code, or coordinates.
homepage: https://wttr.in/:help
metadata: {"clawdbot":{"emoji":"🌤️","requires":{"bins":["curl"]}}}
---

# Weather Query

Get weather data for any location. Two free services, no API keys needed.

## Primary: wttr.in

```
# Quick one-liner
curl -s "wttr.in/{location}?format=3"
# → London: ⛅️ +8°C

# Compact format with details
curl -s "wttr.in/{location}?format=%l:+%c+%t+%h+%w"
# → London: ⛅️ +8°C 71% ↙5km/h

# Full forecast (3 days)
curl -s "wttr.in/{location}?T"

# Today only
curl -s "wttr.in/{location}?1"

# Current conditions only
curl -s "wttr.in/{location}?0"
```

### Format Codes
`%c` condition | `%t` temperature | `%h` humidity | `%w` wind | `%l` location | `%m` moon phase | `%p` precipitation

### Tips
- URL-encode spaces: `wttr.in/New+York`
- Airport codes work: `wttr.in/JFK`, `wttr.in/PEK`
- Units: `?m` (metric, default) · `?u` (USCS)
- PNG output: `curl -s "wttr.in/{location}.png" -o /tmp/weather.png`

## Fallback: Open-Meteo (JSON)

When wttr.in fails, use Open-Meteo:
```bash
# First, geocode the city (or use known coordinates)
curl -s "https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"

# Then query weather
curl -s "https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,precipitation_probability"
```

## Display Format

```
🌤️ {Location} — {condition} {temperature}

💧 Humidity: {humidity}%  |  🌬️ Wind: {wind}
📅 Forecast: {brief summary}
```

## Error Handling

| Situation | Response |
|-----------|----------|
| City not found | Suggest checking spelling or trying airport code |
| wttr.in timeout | Auto-fallback to Open-Meteo |
| No coordinates available | Ask user to provide city name or coordinates |

## NEVER

- NEVER try to use a paid/API-key weather service
- NEVER show raw JSON to the user — parse and format it
- NEVER guess a city's coordinates — use the geocoding API
