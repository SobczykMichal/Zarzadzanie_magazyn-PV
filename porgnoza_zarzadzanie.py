import matplotlib.pyplot as plt
import numpy as np

class SmartEnergySystem:
    def __init__(self, soc=50, pv_forecast_tomorrow=None):
        self.SOC = soc
        self.SOC_DEFAULT_MIN = 20
        self.SOC_DEFAULT_MAX = 80
        self.BATTERY_CAPACITY = 7900  # 7,9 kWh

        self.logs = []

        self.pv_forecast_tomorrow = pv_forecast_tomorrow or [0]*24
        self.SOC_MIN = self.SOC_DEFAULT_MIN
        self.SOC_MAX = self.SOC_DEFAULT_MAX

        self.analyze_forecast()

    def analyze_forecast(self):
        total_pv = sum(self.pv_forecast_tomorrow)
        print(f"[Prognoza] Jutro przewidywana produkcja PV: {total_pv:.0f} Wh")

        if total_pv < 10000:  # Mniej niż 10 kWh = słaba pogoda
            self.SOC_MIN = 35
            print("[Algorytm] Słabe słońce jutro – podnoszę SOC_MIN do 35%")
        else:
            print("[Algorytm] Dobra pogoda – zostawiam SOC_MIN na 20%")

    def simulate_hour(self, pv_power, load_demand, grid_available=True):
        soc_energy = self.SOC / 100 * self.BATTERY_CAPACITY
        log = {"pv": 0, "battery": 0, "grid": 0, "mode": "", "SOC": self.SOC, "load": load_demand}

        if pv_power >= load_demand:
            log["pv"] = load_demand
            surplus = pv_power - load_demand

            if self.SOC < self.SOC_MAX:
                charge = min(surplus, (self.SOC_MAX - self.SOC) / 100 * self.BATTERY_CAPACITY)
                self.SOC += (charge / self.BATTERY_CAPACITY) * 100
                log["battery"] = -charge
                log["mode"] = "PV zasila obciążenie i ładuje baterię"
            else:
                log["mode"] = "PV zasila obciążenie (bateria pełna)"
        else:
            log["pv"] = pv_power
            needed = load_demand - pv_power

            if soc_energy > 0 and self.SOC > self.SOC_MIN:
                from_battery = min(needed, soc_energy, (self.SOC - self.SOC_MIN) / 100 * self.BATTERY_CAPACITY)
                self.SOC -= (from_battery / self.BATTERY_CAPACITY) * 100
                log["battery"] = from_battery
                needed -= from_battery

            if needed > 0:
                if grid_available:
                    log["grid"] = needed
                    log["mode"] = "PV + Bateria + Sieć zasila obciążenie"
                else:
                    log["mode"] = "Ograniczenie obciążenia (bateria niska, sieć wyłączona)"
            else:
                log["mode"] = "PV + Bateria zasila obciążenie"

        log["SOC"] = self.SOC
        self.logs.append(log)

    def simulate_day(self, pv_schedule, load_schedule, grid_status=None):
        for hour in range(24):
            pv = pv_schedule[hour]
            load = load_schedule[hour]
            grid = grid_status[hour] if grid_status else True
            self.simulate_hour(pv, load, grid)

    def summary(self):
        for i, log in enumerate(self.logs):
            print(f"[{i:02d}h] {log['mode']} | PV: {log['pv']:.0f} Wh | Bateria: {log['battery']:.0f} Wh | Sieć: {log['grid']:.0f} Wh | SOC: {log['SOC']:.1f}%")

    def plot_simulation(self):
        hours = np.arange(24)
        pv = [log["pv"] for log in self.logs]
        load = [log["load"] for log in self.logs]
        battery = [max(log["battery"], 0) for log in self.logs]
        grid = [log["grid"] for log in self.logs]
        soc = [log["SOC"] for log in self.logs]

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

        ax1.stackplot(hours, pv, battery, grid, labels=['PV', 'Bateria', 'Sieć'], colors=['#FFD700', '#1E90FF', '#FF4500'])
        ax1.plot(hours, load, 'k-', linewidth=2, label='Obciążenie')
        ax1.set_title('Symulacja systemu energetycznego - Jutro')
        ax1.set_ylabel('Energia (Wh)')
        ax1.legend(loc='upper left')
        ax1.grid(True)

        ax2.plot(hours, soc, 'g-', linewidth=2, label='SOC')
        ax2.set_title('Stan naładowania baterii (SOC)')
        ax2.set_xlabel('Godzina')
        ax2.set_ylabel('SOC (%)')
        ax2.legend(loc='upper left')
        ax2.grid(True)

        plt.tight_layout()
        plt.savefig('energy_simulation_tomorrow.png')
        plt.close(fig)
        print("[Wizualizacja] Wykres zapisany jako 'energy_simulation_tomorrow.png'")