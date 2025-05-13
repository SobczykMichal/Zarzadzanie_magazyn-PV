import tkinter as tk
from tkinter import ttk

def run_simulation():
    pv = pv_scale.get()
    load = load_scale.get()
    soc = soc_scale.get()
    grid_ok = grid_var.get() == 1

    system = EnergySystem(soc=soc)
    system.simulate_hour(pv, load, grid_ok)
    log = system.logs[-1]

    result_text.set(
        f"Mode: {log['mode']}\n"
        f"PV used: {log['pv']} Wh\n"
        f"Battery used: {log['battery']} Wh\n"
        f"Grid used: {log['grid']} Wh\n"
        f"New SOC: {system.SOC:.1f}%"
    )

# EnergySystem klasa z wcześniejszego kodu
class EnergySystem:
    def __init__(self, soc=50):
        self.SOC = soc
        self.SOC_MAX = 80
        self.SOC_MIN = 20
        self.BATTERY_CAPACITY = 7900

        self.logs = []

    def simulate_hour(self, pv_power, load_demand, grid_available=True):
        soc_energy = self.SOC / 100 * self.BATTERY_CAPACITY
        log = {"pv": 0, "battery": 0, "grid": 0, "mode": "", "SOC": self.SOC}

        if pv_power >= load_demand:
            log["pv"] = load_demand
            surplus = pv_power - load_demand

            if self.SOC < self.SOC_MAX:
                charge = min(surplus, (self.SOC_MAX - self.SOC) / 100 * self.BATTERY_CAPACITY)
                self.SOC += (charge / self.BATTERY_CAPACITY) * 100
                log["mode"] = "PV powers load & charges battery"
            else:
                log["mode"] = "PV powers load (battery full)"
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
                    log["mode"] = "PV + Battery + Grid supplies load"
                else:
                    log["mode"] = "Load shedding (battery low, grid off)"
            else:
                log["mode"] = "PV + Battery powers load"

        log["SOC"] = self.SOC
        self.logs.append(log)

# GUI z tkinter
root = tk.Tk()
root.title("Symulacja zarządzania energią")

ttk.Label(root, text="PV Power [Wh]").pack()
pv_scale = ttk.Scale(root, from_=0, to=3000, orient="horizontal")
pv_scale.set(1000)
pv_scale.pack()

ttk.Label(root, text="Load Demand [Wh]").pack()
load_scale = ttk.Scale(root, from_=0, to=3000, orient="horizontal")
load_scale.set(1500)
load_scale.pack()

ttk.Label(root, text="Battery SOC [%]").pack()
soc_scale = ttk.Scale(root, from_=0, to=100, orient="horizontal")
soc_scale.set(50)
soc_scale.pack()

grid_var = tk.IntVar()
tk.Checkbutton(root, text="Grid Available", variable=grid_var).pack()
grid_var.set(1)

tk.Button(root, text="Symuluj", command=run_simulation).pack(pady=10)

result_text = tk.StringVar()
tk.Label(root, textvariable=result_text, justify="left").pack(pady=10)

root.mainloop()
