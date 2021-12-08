#!/usr/bin/env python3

import matplotlib.pyplot as plt

class Simulation:    
    def __init__(self, name = "", grids = {}, sources = {}, sinks = {}, storages = {}, convs = {}):
        self.name     = name
        self.grids    = grids
        self.sources  = sources
        self.sinks    = sinks
        self.storages = storages
        self.convs    = convs
    def step(self):
        for name, grid in self.grids.items(): 
            grid.powers[name].append(0)
        for name, source in self.sources.items():
            source.step()
        for name, sink in self.sinks.items():
            sink.step()
        for name, storage in self.storages.items():
            storage.step()
        for name, conv in self.convs.items():
            conv.step()

class Grid:
    def __init__(self, name, sim):
        self.name = name
        sim.grids[name] = self
        self.powers = { self.name : [] }
    def plot(self):
        fig = plt.figure(1)
        for name, power in self.powers.items():
            ax = plt.plot(power, label=name)
        fig.legend()
        plt.title(self.name)
        plt.show()

class SimpleSource:
    def __init__(self, name, sim, grid, power):
        self.name = name
        sim.sources[name] = self
        self.grid   = sim.grids[grid]
        self.power = power
        self.powers = { self.grid.name : [] }
        self.grid.powers[self.name] = self.powers[self.grid.name]
    def step(self):
        self.powers[self.grid.name].append(self.power)
        self.grid.powers[self.grid.name][-1] += self.powers[self.grid.name][-1]

class SimpleSink:
    def __init__(self, name, sim, grid, power):
        self.name = name
        sim.sinks[name] = self
        self.grid   = sim.grids[grid]
        self.power = power
        self.powers = { self.grid.name : [] }
        self.grid.powers[self.name] = self.powers[self.grid.name]
    def step(self):
        self.powers[self.grid.name].append(-self.power)
        self.grid.powers[self.grid.name][-1] += self.powers[self.grid.name][-1]

class SimpleBoiler:
    def __init__(self, name, sim, fuelGrid, heatGrid, efficiency = 0.85):
        self.name = name
        sim.convs[name] = self
        self.fuelGrid = sim.grids[fuelGrid]
        self.heatGrid = sim.grids[heatGrid]
        self.efficiency = efficiency
        self.powers = { self.fuelGrid.name : [] 
                      , self.heatGrid.name : []
                      }
        self.fuelGrid.powers[self.name] = self.powers[self.fuelGrid.name]
        self.heatGrid.powers[self.name] = self.powers[self.heatGrid.name]
    def step(self):
        for name, power in self.powers.items(): 
            power.append(0)
        if self.heatGrid.powers[self.heatGrid.name][-1] < 0:
            self.powers[self.heatGrid.name][-1] -= self.heatGrid.powers[self.heatGrid.name][-1]
            self.heatGrid.powers[self.heatGrid.name][-1] = 0
            self.powers[self.fuelGrid.name][-1] += self.powers[self.heatGrid.name][-1] / self.efficiency
            self.fuelGrid.powers[self.fuelGrid.name][-1] += self.powers[self.fuelGrid.name][-1]

s = Simulation('test')
Grid('Heat', s)
Grid('Wood', s)
SimpleSource('Pwr1', s, 'Heat', 20)
SimpleSink('Drain', s, 'Heat', 50)
SimpleBoiler('Boiler1', s, 'Wood', 'Heat')
for _ in range(8760):
    s.step()
for name, grid in s.grids.items():
    grid.plot()
