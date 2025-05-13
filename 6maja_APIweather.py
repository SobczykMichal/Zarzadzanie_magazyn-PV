import requests
import datetime

# Konfiguracja
LAT, LON = 52.2297, 21.0122  # Warszawa
MOC_KWP = 5  # Twoja instalacja PV
WSPOLCZYNNIK = 0.0012  # Produkcja na W/m²

# Pobierz prognozę z Open-Meteo
url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&hourly=shortwave_radiation&timezone=Europe%2FWarsaw"
response = requests.get(url)
data = response.json()

godziny = data['hourly']['time']
irradiacja = data['hourly']['shortwave_radiation']

# Analiza produkcji jutro
dzisiaj = datetime.date.today()
jutro = dzisiaj + datetime.timedelta(days=1)

print(f"⏳ Prognozowana produkcja PV na {jutro}:\n")

for i, godzina in enumerate(godziny):
    if godzina.startswith(str(jutro)):
        irr = irradiacja[i]
        energia = irr * WSPOLCZYNNIK * MOC_KWP  # w kWh
        czas = godzina[11:16]
        print(f"{czas} → {energia:.2f} kWh (irr: {irr:.0f} W/m²)")

        # Przykład prostego działania:
        if energia > 0.5:
            print(f"   ⚡️ Zalecane: Włącz urządzenie o {czas}")