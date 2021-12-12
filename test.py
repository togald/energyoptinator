import matplotlib.pyplot as plt
import energyoptinator as eo
from scipy.signal import savgol_filter

class SimpleSolar:
    def __init__(self, name, sim, grid, irradiance, efficiency, area):
        """ Creates a SimpleSolar power source, taking irradiance data
        given in [W/m^2], efficiency in absolute numbers, and area in
        [m^2], and stuffs the power with [W].
        """
        self.name = name
        sim.entities[name] = self
        self.grid = sim.grids[grid]
        self.irradiance = irradiance
        self.efficiency = efficiency
        self.area = area
        self.powers = { self.grid.name: [] }
        self.grid.powers[self.name] = self.powers[self.grid.name]
    def step(self):
        self.powers[self.grid.name].append(self.irradiance[len(self.powers[self.grid.name])] * self.efficiency * self.area)

class Battery:
    def __init__(self, name, sim, grid, capacity, initialCharge, selfDischargeRate = 0.03):
        self.name = name
        sim.storages[name] = self
        self.grid = sim.grids[grid]
        self.capacity = capacity
        self.charges = []
        self.initialCharge = initialCharge
        self.selfDischargeRate = selfDischargeRate
        self.powers = { self.grid.name : [] }
        self.grid.powers[self.name] = self.powers[self.grid.name]
    def step(self):
        if not self.charges:
            self.charges.append(self.initialCharge)
        else:
            self.charges.append(self.charges[-1] - self.selfDischargeRate*self.capacity)
        if self.charges[-1] + self.grid.powers[self.grid.name][-1] > self.capacity:
            # Storage is overflowing
            self.powers[self.grid.name].append(self.capacity - self.charges[-1])
            self.grid.powers[self.grid.name][-1] -= self.powers[self.grid.name][-1]
            self.charges[-1] = self.capacity
        elif self.charges[-1] + self.grid.powers[self.grid.name][-1] < 0:
            # Storage is emptied
            self.powers[self.grid.name].append(self.charges[-1])
            self.grid.powers[self.grid.name][-1] += self.powers[self.grid.name][-1]
            self.charges[-1] = 0
        else:
            # Storage is used normally
            self.powers[self.grid.name].append(-self.grid.powers[self.grid.name][-1])
            self.grid.powers[self.grid.name][-1] = 0
            self.charges[-1] -= self.powers[self.grid.name][-1]

def monthly_to_daily(months_iter):
    months = [31, 28, 31, 30, 31, 30, 31, 30, 31, 31, 30, 31]
    days =  []
    for month, data in zip(months, months_iter):
        for _ in range(month):
            days.append(data/month)
    return savgol_filter(days, 201, 3)

def simtest1(hushel, initBatt = 500, solarArea = 1):
    irradiance = [ 13, 24, 41, 90, 114, 108, 102, 105, 88, 90, 53, 16, 13 ] # kWh/m^2, month
    irr = monthly_to_daily(irradiance)

    s = eo.Simulation()
    eo.Grid('El', s)
    SimpleSolar('Solceller', s, 'El', irr, 0.14, solarArea)
    eo.SimpleSink('Hushållsel', s, 'El', hushel/365)
    Battery('Batteri', s, 'El', hushel, initBatt, selfDischargeRate = 0.03/30)
    for _ in irr:
        s.step()
    return s

if __name__ == '__main__':
    hushel = 2000 # kWh/d
    s = simtest1(hushel, initBatt=hushel/2)
    solarGen = sum(s.entities['Solceller'].powers['El'])
    solarReq = 24
    print(solarReq)
    s = simtest1(hushel, initBatt=500, solarArea = solarReq)
    for _, grid in s.grids.items():
        grid.plot()
    s.plot_storages()
