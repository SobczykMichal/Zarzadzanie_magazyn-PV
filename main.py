import random
import matplotlib.pyplot as plt

class EnergySystem:
    def __init__(self, soc=50):
        self.SOC = soc  # [%]
        self.SOC_MAX = 80
        self.SOC_MIN = 20
        self.BATTERY_CAPACITY = 7900  # Wh (7.9 kWh)

        self.grid_consumed = 0
        self.pv_consumed = 0
        self.battery_consumed = 0
        self.battery_charged = 0
        self.logs = []

    def simulate_hour(self, pv_power, load_demand, grid_available=True):
        soc_energy = self.SOC / 100 * self.BATTERY_CAPACITY
        log = {
            "pv_power": pv_power,
            "load_demand": load_demand,
            "SOC": self.SOC,
            "grid": 0,
            "battery": 0,
            "pv": 0,
            "mode": ""
        }

        # Try PV first
        if pv_power >= load_demand:
            log["pv"] = load_demand
            surplus = pv_power - load_demand

            if self.SOC < self.SOC_MAX:
                charge_amount = min(surplus, (self.SOC_MAX - self.SOC) / 100 * self.BATTERY_CAPACITY)
                self.SOC += (charge_amount / self.BATTERY_CAPACITY) * 100
                self.battery_charged += charge_amount
                log["mode"] = "PV powers load & charges battery"
            else:
                log["mode"] = "PV powers load (battery full)"
        else:
            # Not enough from PV
            log["pv"] = pv_power
            needed = load_demand - pv_power

            # Use battery if possible
            if soc_energy > 0 and self.SOC > self.SOC_MIN:
                from_battery = min(needed, soc_energy, (self.SOC - self.SOC_MIN) / 100 * self.BATTERY_CAPACITY)
                self.SOC -= (from_battery / self.BATTERY_CAPACITY) * 100
                log["battery"] = from_battery
                self.battery_consumed += from_battery
                needed -= from_battery
                soc_energy -= from_battery

            # Use grid if still needed
            if needed > 0:
                if grid_available:
                    log["grid"] = needed
                    self.grid_consumed += needed
                    log["mode"] = "PV + Battery + Grid supplies load"
                else:
                    log["mode"] = "Load shedding (no grid, battery low)"
            else:
                log["mode"] = "PV + Battery powers load"

        self.pv_consumed += log["pv"]
        self.logs.append(log)

    def simulate_day(self, hours=24):
        for hour in range(hours):
            # Przykładowa generacja i zapotrzebowanie
            pv = max(0, random.gauss(1500 if 6 <= hour <= 17 else 0, 300))  # Słońce tylko między 6 a 17
            load = random.randint(400, 1200)  # Zapotrzebowanie (np. 0.5-1.2 kWh)
            grid_ok = random.random() > 0.05  # 5% szansy na awarię sieci

            self.simulate_hour(pv, load, grid_ok)

    def summary(self):
        print(f"Energy from PV used directly: {self.pv_consumed:.1f} Wh")
        print(f"Energy from Battery: {self.battery_consumed:.1f} Wh")
        print(f"Energy charged to Battery: {self.battery_charged:.1f} Wh")
        print(f"Energy from Grid: {self.grid_consumed:.1f} Wh")
        print(f"Final SOC: {self.SOC:.1f}%")

    def plot(self):
        hours = list(range(len(self.logs)))
        pv = [log["pv"] for log in self.logs]
        battery = [log["battery"] for log in self.logs]
        grid = [log["grid"] for log in self.logs]
        soc = [log["SOC"] for log in self.logs]

        plt.figure(figsize=(12, 6))
        plt.stackplot(hours, pv, battery, grid, labels=['PV', 'Battery', 'Grid'], alpha=0.7)
        plt.plot(hours, soc, label='Battery SOC [%]', color='black', linestyle='--')
        plt.title("Symulacja dnia – Zużycie energii i SOC baterii")
        plt.xlabel("Godzina")
        plt.ylabel("Energia (Wh)")
        plt.legend()
        plt.grid(True)
        plt.show()
if __name__ == "__main__":
    system = EnergySystem(soc=50)  # Startujemy z 50% baterii
    system.simulate_day()
    system.summary()
    system.plot()

