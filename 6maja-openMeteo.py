import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# --- Parametry użytkownika ---
LATITUDE = 51.7592  # Łódź
LONGITUDE = 19.4560
PANEL_EFFICIENCY = 0.20
PANEL_AREA_M2 = 10.0  # m²
BATTERY_CAPACITY_KWH = 5.0
BATTERY_CURRENT_CHARGE_KWH = 2.5
GRID_ENERGY_COST = 0.8  # PLN/kWh
MAX_CHARGE_DISCHARGE_KW = 2.0

# --- Pobranie danych pogodowych ---
def fetch_weather_data():
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "hourly": "direct_normal_irradiance,temperature_2m,cloudcover",
        "timezone": "Europe/Warsaw",
    }
    url = "https://api.open-meteo.com/v1/forecast"
    response = requests.get(url, params=params)
    data = response.json()
    df = pd.DataFrame(data["hourly"])
    df["time"] = pd.to_datetime(df["time"])
    return df

# --- Obliczenia produkcji PV ---
def estimate_pv_production(df):
    irradiance = df["direct_normal_irradiance"]  # W/m²
    df["pv_production_kwh"] = (irradiance * PANEL_EFFICIENCY * PANEL_AREA_M2) / 1000  # kWh/h
    return df

# --- Zarządzanie energią ---
def manage_energy(df):
    soc = BATTERY_CURRENT_CHARGE_KWH
    soc_history = []
    battery_action = []
    grid_usage = []
    recommendations = []

    for i, row in df.iterrows():
        production = row["pv_production_kwh"]
        demand = 1.0  # stałe zużycie 1 kWh/h jako przykład

        net_energy = production - demand

        if net_energy > 0:
            # Nadmiar – ładuj magazyn
            charge = min(net_energy, MAX_CHARGE_DISCHARGE_KW, BATTERY_CAPACITY_KWH - soc)
            soc += charge
            battery_action.append(f"Ładowanie {charge:.2f} kWh")
            grid_usage.append(0)
            recommendations.append("Sugeruj uruchomienie urządzeń – nadmiar energii")
        else:
            # Niedobór – rozładuj magazyn lub użyj sieci
            discharge = min(-net_energy, MAX_CHARGE_DISCHARGE_KW, soc)
            soc -= discharge
            remaining = -net_energy - discharge
            battery_action.append(f"Rozładowanie {discharge:.2f} kWh")
            grid_usage.append(remaining)
            if remaining > 0:
                recommendations.append("Uwaga! Korzystanie z sieci – kosztowna energia")
            else:
                recommendations.append("Magazyn pokrywa zapotrzebowanie")

        soc_history.append(soc)

    df["battery_soc_kwh"] = soc_history
    df["battery_action"] = battery_action
    df["grid_usage_kwh"] = grid_usage
    df["recommendation"] = recommendations
    return df

# --- Wizualizacja ---
def plot_results(df):
    fig, ax1 = plt.subplots(figsize=(14, 6))

    ax1.plot(df["time"], df["pv_production_kwh"], label="Produkcja PV [kWh]", color="orange")
    ax1.plot(df["time"], df["battery_soc_kwh"], label="Poziom magazynu [kWh]", color="blue")
    ax1.plot(df["time"], df["grid_usage_kwh"], label="Zużycie z sieci [kWh]", color="red")
    ax1.set_ylabel("Energia [kWh]")
    ax1.set_xlabel("Czas")
    ax1.set_title("Zarządzanie energią – prognoza na 24h (Łódź)")
    ax1.legend()
    ax1.grid(True)

    plt.tight_layout()
    plt.show()

# --- Główna logika ---
if __name__ == "__main__":
    df_weather = fetch_weather_data()
    df_weather = estimate_pv_production(df_weather)
    df_weather = manage_energy(df_weather)

    # Wyświetl pierwsze rekomendacje
    print("\n--- Rekomendacje na najbliższe godziny ---")
    print(df_weather[["time", "pv_production_kwh", "battery_action", "grid_usage_kwh", "recommendation"]].head(10))

    # Wykresy
    plot_results(df_weather)
