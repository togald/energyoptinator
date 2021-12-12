#!/usr/bin/env python3

import matplotlib.pyplot as plt

class Simulation:
    def __init__( self
                , name = ""
                , grids = {}
                , entities = {}
                , storages = {} ):
        """ Initializes a simulation. The simulation object holds a
        reference to all grids and entities in the simulation. Every
        object has a name, and objects are expected to be stored in
        dictionaries.

        Entities are expected to add themselves to the reference lists.
        """
        self.name     = name
        self.grids    = grids
        self.entities = entities
        self.storages = storages
    def step(self):
        for _, entity in self.entities.items():
            entity.step()
        for _, grid in self.grids.items():
            grid.step()
        for _, storage in self.storages.items():
            storage.step()
    def plot_grids(self):
        fig = plt.figure(1)
        for name, grid in self.grids.items():
            ax = plt.plot(grid.powers[name], label=name)
        fig.legend()
        plt.title(self.name)
        plt.show()
    def plot_storages(self):
        fig = plt.figure(1)
        for name, storage in self.storages.items():
            ax = plt.plot(storage.charges, label=name)
        fig.legend()
        plt.title(self.name)
        plt.show()

class Grid:
    def __init__(self, name, sim):
        """ Creates a new Grid object. The new Grid object holds its
        name, places a reference to itself in the simulation it belongs
        to, and contains a dictionary with lists of all contributing
        powers.
        """
        self.name = name
        self.sim = sim
        sim.grids[name] = self
        self.powers = { self.name : [] }
    def step(self):
        self.powers[self.name].append(0)
        for name, power in self.powers.items():
            if name in self.sim.entities.keys():
                self.powers[self.name][-1] += power[-1]
    def plot(self):
        """ Grid.plot() plots a time diagram of all additions and
        subtractions from the grid, one series per connected entity.
        """
        fig = plt.figure(1)
        for name, power in self.powers.items():
            ax = plt.plot(power, label=name)
        fig.legend()
        plt.title(self.name)
        plt.show()

class SimpleSource:
    def __init__(self, name, sim, grid, power):
        """ SimpleSource is the simplest possible source, it adds its
        self.power to its self.grid every time step. There is no unit
        conversion, no variation.
        """
        self.name = name
        sim.entities[name] = self
        self.grid = sim.grids[grid]
        self.power = power
        self.powers = { self.grid.name : [] }
        self.grid.powers[self.name] = self.powers[self.grid.name]
    def step(self):
        self.powers[self.grid.name].append(self.power)

class SimpleSink:
    def __init__(self, name, sim, grid, power):
        """ SimpleSink is the simplest possible sink, it subtracts its
        self.power to its self.grid every time step. There is no unit
        conversion, no variation.
        """
        self.name = name
        sim.entities[name] = self
        self.grid   = sim.grids[grid]
        self.power = power
        self.powers = { self.grid.name : [] }
        self.grid.powers[self.name] = self.powers[self.grid.name]
    def step(self):
        self.powers[self.grid.name].append(-self.power)

class SimpleStorage:
    def __init__(self, name, sim, grid, capacity, initialCharge):
        """SimpleStorage is the simplest possible storage. There is no
        over-time losses, no charging or discharging losses, and no
        unit conversion.
        """
        self.name = name
        sim.storages[name] = self
        self.grid = sim.grids[grid]
        self.capacity = capacity
        self.charges = []
        self.initialCharge = initialCharge
        self.powers = { self.grid.name : [] }
        self.grid.powers[self.name] = self.powers[self.grid.name]
    def step(self):
        """ If overflowing:
        - Set power to be absorbed (self.grid.powers[self.name])
        - Subtract that from grid (self.powers[self.grid.name])
        - Set charge to full
        If completely drained:
        - Set power to be delivered is equal to current charge
        -
        """
        if not self.charges:
            self.charges.append(self.initialCharge)
        else:
            self.charges.append(self.charges[-1])
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

class SimpleBoiler:
    def __init__(self, name, sim, fuelGrid, heatGrid, efficiency = 0.85):
        self.name = name
        sim.entities[name] = self
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

def dem1():
    s = Simulation('test')
    Grid('Heat', s)
    SimpleSource('Heater1', s, 'Heat', 20)
    SimpleSink('Drain1', s, 'Heat', 50)
    SimpleStorage('Acc1', s, 'Heat', 100000, 100000)
    for _ in range(8760):
        s.step()
    for name, grid in s.grids.items():
        grid.plot()
    s.plot_grids()
    s.plot_storages()

if __name__ == '__main__':
    dem1()
