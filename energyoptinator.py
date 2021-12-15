#!/usr/bin/env python3

import math
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

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
        plt.savefig(f"Grids in {self.name}", dpi=96)

    def plot_storages(self):
        fig = plt.figure(1)
        for name, storage in self.storages.items():
            ax = plt.plot(storage.charges, label=name)
        fig.legend()
        plt.title(self.name)
        plt.savefig(f"Storages in {self.name}", dpi=96)

    def plot_all(self):
        n = len(self.grids.items())
        m = len(self.storages.items())
        fig, axlist = plt.subplots(math.ceil((n+m)/2), 2, figsize=(16, 4.5*n/2), dpi=120)
        for ax, (gridname, grid) in zip(axlist.flatten()[:n], self.grids.items()):
            for name, data in grid.powers.items():
                ax.plot(hourly_to_weekly(_6min_to_hourly(data)), label=name)
            ax.set_title(gridname)
            ax.set_xlabel(grid.timesteplabel)
            ax.set_ylabel(grid.unit)
            ax.legend( bbox_to_anchor=(1.05, 1) )
        for ax, (storagename, storage) in zip(axlist.flatten()[n:], self.storages.items()):
            ax.plot([ c/storage.capacity for c in _6min_to_hourly([i/10 for i in storage.charges[1:] ] ) ], label=storagename)
            ax.set_title(f"{storagename}, {storage.capacity} kWh")
            ax.set_ylabel('SoC')
            ax.set_xlabel('Hour')
            ax.legend( bbox_to_anchor=(1.05, 1) )
        fig.suptitle(self.name)
        plt.tight_layout()
        plt.savefig(self.name, dpi=96)


class Grid:
    def __init__(self, name, sim, unit = 'kW', timesteplabel = 'Week'):
        """ Creates a new Grid object. The new Grid object holds its
        name, places a reference to itself in the simulation it belongs
        to, and contains a dictionary with lists of all contributing
        powers.
        """
        self.name = name
        self.sim = sim
        sim.grids[name] = self
        self.unit = unit
        self.timesteplabel = timesteplabel
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
        plt.ylabel(self.unit)
        plt.xlabel(self.timesteplabel)
        plt.title(self.name)
        plt.tight_layout()
        plt.show()

    def plot_smoothed(self):
        """ Grid.plot() plots a time diagram of all additions and
        subtractions from the grid, one series per connected entity,
        but smoothed.
        """
        fig = plt.figure(1)
        for name, power in self.powers.items():
            ax = plt.plot(savgol_filter(power, 2001, 3), label=name)
        fig.legend()
        plt.ylabel(self.unit)
        plt.xlabel(self.timesteplabel)
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


class TimevariantSource:
    def __init__(self, name, sim, grid, supply):
        """ TimevariantSink takes a list or tuple of data as input,
        and appends the appropriate time step to its power output
        every step.
        """
        self.name = name
        sim.entities[name] = self
        self.grid   = sim.grids[grid]
        self.supply = supply
        self.powers = { self.grid.name : [] }
        self.grid.powers[self.name] = self.powers[self.grid.name]

    def step(self):
        self.powers[self.grid.name].append(self.supply[len(self.powers[self.grid.name])])


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


class TimevariantSink:
    def __init__(self, name, sim, grid, drain):
        """ TimevariantSink takes a list or tuple of data as input,
        and appends the appropriate time step to its power output
        every step.
        """
        self.name = name
        sim.entities[name] = self
        self.grid   = sim.grids[grid]
        self.drain = drain
        self.powers = { self.grid.name : [] }
        self.grid.powers[self.name] = self.powers[self.grid.name]

    def step(self):
        self.powers[self.grid.name].append(-self.drain[len(self.powers[self.grid.name])])


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
        """ Step the storage. Storages are tricky to step since they
        must adhere to both overflowing, being completely emptied, and
        also make sure to update the grid accordingly.
        """
        # Make sure to store initial charge on the first step
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

    def soc(self):
        if self.charges:
            return self.charges[-1]/self.capacity
        else:
            return self.initialCharge/self.capacity

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

    def soc(self):
        if self.charges:
            return self.charges[-1]/self.capacity
        else:
            return self.initialCharge/self.capacity


class RegulatedSource:
    def __init__(self, name, sim, grid, power, regulator, signal):
        """ RegulatedSource is a source that varies according to its
        regulator between 0 and self.power power output.
        """
        self.name = name
        sim.entities[name] = self
        self.grid = sim.grids[grid]
        self.power = power
        self.regulator = regulator
        self.signal = signal
        self.powers = { self.grid.name : [] }
        self.grid.powers[self.name] = self.powers[self.grid.name]

    def step(self):
        if self.signal:
            self.powers[self.grid.name].append(self.power*self.regulator.step(self.signal))
        else:
            self.powers[self.grid.name].append(0)


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


class SimpleBoiler:
    def __init__( self
                , name
                , sim
                , fuelGrid
                , heatGrid
                , regulator
                , signal
                , thermalRatedPower=8
                , fuelUse=9.5 ):
        self.name = name
        sim.entities[name] = self
        self.fuelGrid = sim.grids[fuelGrid]
        self.heatGrid = sim.grids[heatGrid]
        self.powers = { self.fuelGrid.name : []
                      , self.heatGrid.name : []
                      }
        self.fuelGrid.powers[self.name] = self.powers[self.fuelGrid.name]
        self.heatGrid.powers[self.name] = self.powers[self.heatGrid.name]
        self.regulator = regulator
        self.signal = signal
        self.thermalRatedPower = thermalRatedPower
        self.fuelUse = fuelUse

    def step(self):
        if self.signal:
            reg = self.regulator.step(self.signal)
        else:
            reg = 0
        self.powers[self.fuelGrid.name].append(-reg*self.fuelUse)
        self.powers[self.heatGrid.name].append(reg*self.thermalRatedPower)

class CHPboiler:
    def __init__(self
                , name
                , sim
                , fuelGrid
                , heatGrid
                , electricityGrid
                , regulator
                , signal
                , thermalRatedPower = 14
                , electricityRatedPower = 1
                , fuelUse = 17.3 ):
        self.name = name
        sim.entities[name] = self
        self.fuelGrid = sim.grids[fuelGrid]
        self.heatGrid = sim.grids[heatGrid]
        self.electricityGrid = sim.grids[electricityGrid]
        self.powers = { self.fuelGrid.name : []
                      , self.heatGrid.name : []
                      , self.electricityGrid.name : []
                      }
        self.fuelGrid.powers[self.name] = self.powers[self.fuelGrid.name]
        self.heatGrid.powers[self.name] = self.powers[self.heatGrid.name]
        self.electricityGrid.powers[self.name] = self.powers[self.electricityGrid.name]
        self.regulator = regulator
        self.signal = signal
        self.thermalRatedPower = thermalRatedPower
        self.electricityRatedPower = electricityRatedPower
        self.fuelUse = fuelUse

    def step(self):
        if self.signal:
            reg = self.regulator.step(self.signal)
        else:
            reg = 0
        self.powers[self.fuelGrid.name].append(reg*self.fuelUse)
        self.powers[self.heatGrid.name].append(reg*self.thermalRatedPower)
        self.powers[self.electricityGrid.name].append(reg*self.electricityRatedPower)


class OnoffRegulator:
    def __init__(self, onThr, offThr, initState, flip=0):
        """ Simplest possible regulator there is, an on/off regulator.
        onThr is the low point where the regulator turns on, offThr
        is the high point where the regulator turns off. Outputs a
        signal that is either 0 or 1, nothing in between.
        """
        self.onThr = onThr
        self.offThr = offThr
        self.states = []
        self.initState = initState
        self.flip = flip

    def step(self, signal):
        """ Steps the regulator. Regulators must be passed their
        signal every step for it to update. OnoffRegulator requires
        the signal to be a function returning a value between 0 and 1,
        ideally a Storage.soc() method.
        """
        # If there is no previous step, the regulator is set to its initial state.
        if not self.states:
            self.states.append(self.initState)
        # Things to do if regulator was previously on
        elif self.states[-1] == 1:
            if signal() > self.offThr:
                self.states.append(0)
            else:
                self.states.append(1)
        # Things to do if regulator was previously off
        else:
            if signal() < self.onThr:
                self.states.append(1)
            else:
                self.states.append(0)
        if self.flip:
            return 1-self.states[-1]
        else:
            return self.states[-1]

## STANDARD DATA MANIPULATORS
#
# These are some standard functions to manipulate data into different
# resolutions. Some of them might be destructive - be careful.
def increase_resolution(data, magnifier):
    output = []
    for d in data:
        for _ in range(magnifier):
            output.append(d/magnifier)
    return output

def decrease_resolution(data, denominator):
    output = []
    for i in range(len(data)//denominator):
        output.append(sum(data[i*denominator-denominator:i*denominator]))
    return output

def monthly_to_daily(data):
    """ This function takes monthly data and converts it into smoothed
    daily data. To get weekly data, it is advised to go via this
    function first.
    """
    months = [31, 28, 31, 30, 31, 30, 31, 30, 31, 31, 30, 31]
    output =  []
    for month, d in zip(months, data):
        for _ in range(month):
            output.append(d/month)
    return savgol_filter(output, 201, 3)

def monthly_to_weekly(data):
    return daily_to_weekly(monthly_to_daily(data))

def daily_to_hourly(data):
    return increase_resolution(data, 24)

def daily_to_hourly_smoothed(data):
    return savgol_filter(daily_to_hourly(data), 47, 2)

def hourly_to_6min(data):
    return increase_resolution(data, 10)

def hourly_to_6min_smoothed(data):
    return savgol_filter(hourly_to_6min(data), 19, 5)

def _6min_to_hourly(data):
    return decrease_resolution(data, 10)

def hourly_to_daily(data):
    return [ i/24 for i in decrease_resolution(data, 24) ]

def hourly_to_weekly(data):
    return [ i/168 for i in decrease_resolution(data, 168) ]

def daily_to_weekly(data):
    return [ i/7 for i in decrease_resolution(data, 7) ]

if __name__ == '__main__':
    pass
