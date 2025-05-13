import requests
import matplotlib.pyplot as plt
from porgnoza_zarzadzanie import SmartEnergySystem


def pobierz_prognoze_openmeteo(szerokosc=51.7592, dlugosc=19.4550):
    """
    Pobiera godzinową prognozę promieniowania słonecznego na dziś i jutro z API Open-Meteo dla Łodzi.
    Zwraca krotkę: (pv_today, pv_forecast_tomorrow) w Wh.
    """
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        parametry = {
            "latitude": szerokosc,
            "longitude": dlugosc,
            "hourly": "shortwave_radiation",
            "forecast_days": 2,
            "timezone": "Europe/Warsaw"
        }
        odpowiedz = requests.get(url, params=parametry)
        odpowiedz.raise_for_status()

        dane = odpowiedz.json()
        promieniowanie_godzinowe = dane["hourly"]["shortwave_radiation"]
        pv_today = promieniowanie_godzinowe[0:24]
        pv_forecast_tomorrow = promieniowanie_godzinowe[24:48]

        efektywnosc_pv = 0.20
        powierzchnia_paneli = 30.0
        pv_today = [promieniowanie * efektywnosc_pv * powierzchnia_paneli for promieniowanie in pv_today]
        pv_forecast_tomorrow = [promieniowanie * efektywnosc_pv * powierzchnia_paneli for promieniowanie in
                                pv_forecast_tomorrow]

        return pv_today, pv_forecast_tomorrow

    except requests.RequestException as e:
        print(f"[Błąd] Nie udało się pobrać danych Open-Meteo: {e}")
        return [0] * 24, [0] * 24


# Realistyczny profil obciążenia (Wh) dla jutra
load_tomorrow = [
    300, 300, 300, 300, 350, 400, 500, 600, 700, 800, 800, 800,
    800, 800, 800, 800, 1000, 1200, 1500, 1500, 1200, 1000, 600, 400
]  # Suma: 14 kWh/dzień

# Taryfa G12: ceny energii (PLN/kWh) dla każdej godziny
taryfa_g12 = [
    0.60, 0.60, 0.60, 0.60, 0.60, 0.60, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00,  # 0-11
    0.60, 0.60, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 0.60, 0.60  # 12-23
]

# Cena sprzedaży nadmiaru PV (PLN/kWh)
cena_sprzedazy_pv = 0.50

# Pobierz dane PV na dziś i jutro
pv_today, pv_forecast_tomorrow = pobierz_prognoze_openmeteo()

# Zainicjuj i uruchom system dla jutrzejszej symulacji
system = SmartEnergySystem(soc=50, pv_forecast_tomorrow=pv_forecast_tomorrow)
system.simulate_day(pv_forecast_tomorrow, load_tomorrow, taryfa_g12=taryfa_g12)
system.summary()
system.calculate_savings(taryfa_g12, cena_sprzedazy_pv)
system.plot_simulation()