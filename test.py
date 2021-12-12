import matplotlib.pyplot as plt
import energyoptinator as eo

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

def monthly_to_daily_flat(months_iter):
    months = [31, 28, 31, 30, 31, 30, 31, 30, 31, 31, 30, 31]
    days =  []
    for month, data in zip(months, months_iter):
        for _ in range(month):
            days.append(data/month)
    return days

def test1(initBatt):
    irradiance = [ 13, 24, 41, 90, 114, 108, 102, 105, 88, 90, 53, 16, 13 ] # kWh/m^2, month
    irr = monthly_to_daily_flat(irradiance)
    hushel = 3000/365 # kWh/d

    s = eo.Simulation()
    eo.Grid('El', s)
    SimpleSolar('Solceller', s, 'El', irr, 0.2, 30)
    eo.SimpleSink('Hushållsel', s, 'El', hushel)
    eo.SimpleStorage('Batteri', s, 'El', 500, initBatt)
    for _ in irr:
        s.step()

    # Plot
    for _, grid in s.grids.items():
        grid.plot()
    s.plot_storages()
    return s.storages['Batteri'].charges[-1]

if __name__ == '__main__':
    test1(test1(500))
