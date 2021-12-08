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

s = Simulation('test')
Grid('El', s)
SimpleSource('Pwr1', s, 'El', 50)
SimpleSink('Drain', s, 'El', 20)
for _ in range(8760):
    s.step()
for name, grid in s.grids.items():
    grid.plot()
