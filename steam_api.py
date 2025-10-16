import requests
import time
import pandas as pd
from tqdm import tqdm

# --- Configuración ---
N_GAMES = 500  # Puedes subirlo progresivamente
DELAY = 0.3    # segundos entre requests para evitar rate limit

# 1️⃣ Obtener lista de juegos
apps_url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
apps = requests.get(apps_url).json()["applist"]["apps"][:N_GAMES]

data = []

for app in tqdm(apps):
    appid = app["appid"]
    name = app["name"]

    # 2️⃣ Obtener detalles del juego
    details_url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=us&l=en"
    try:
        details = requests.get(details_url, timeout=10).json()
        if not details[str(appid)]["success"]:
            continue
        info = details[str(appid)]["data"]
    except Exception:
        continue

    # 3️⃣ Obtener jugadores activos
    players_url = f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={appid}"
    try:
        players = requests.get(players_url, timeout=5).json()
        players_count = players["response"].get("player_count", 0)
    except Exception:
        players_count = None

    # 4️⃣ Extraer datos de interés
    price = None
    if "price_overview" in info:
        price = info["price_overview"]["final"] / 100.0  # precio en USD

    reviews = info.get("recommendations", {}).get("total", None)

    data.append({
        "appid": appid,
        "name": name,
        "price_usd": price,
        "players_now": players_count,
        "reviews": reviews,
    })

    time.sleep(DELAY)

# 5️⃣ Guardar resultados
df = pd.DataFrame(data)
df.to_csv("datos/steam_api_data.csv", index=False)
print("✅ Datos guardados en steam_games_data.csv")