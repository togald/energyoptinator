import matplotlib.pyplot as plt
import energyoptinator as energy

class Simulation:    
    def __init__(self, name = "", grids = {}, sources = {}, sinks = {}, convs = {}, storages = {}):
        self.name     = name
        self.grids    = grids
        self.sources  = sources
        self.sinks    = sinks
        self.storages = storages
        self.convs    = convs
    def step(self):
        for name, grid in self.grids.items(): 
            grid.powers.append(0)
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
        self.name       = name
        sim.grids[name] = self
        self.powers     = []
        self.sources    = []
        self.sinks      = []
        self.storages   = []
    def plot(self):
        fig = plt.figure(1)
        ax = plt.plot(grid.powers, label=gridname)
        for source in self.sources:
            ax = plt.plot(source.powers, label=source.name)
        for sink in self.sinks:
            ax = plt.plot(sink.powers, label=sink.name)
        for storage in self.storages:
            ax = plt.plot(storage.charges, label=storage.name)
        fig.legend()
        plt.title(self.name)
        plt.show()

class Source:
    def __init__(self, name, sim):
        self.name         = name
        sim.sources[name] = self

class SimpleSolar(Source):
    def __init__(self, name, sim, grid, irradiance, efficiency, area):
        Source.__init__(self, name, sim)
        self.grid       = sim.grids[grid]
        self.grid.sources.append(self)
        self.irradiance = irradiance
        self.efficiency = efficiency
        self.area       = area
        self.powers     = []
    def step(self):
        self.powers.append(self.irradiance[len(self.powers)] * self.efficiency * self.area)
        self.grid.powers[-1] += self.powers[-1]

class Sink:
    def __init__(self, name, sim, grid):
        self.name       = name
        sim.sinks[name] = self
        self.grid       = sim.grids[grid]
        self.grid.sinks.append(self)

class SimpleSink(Sink):
    def __init__(self, name, sim, grid, drain):
        Sink.__init__(self, name, sim, grid)
        self.drain  = drain
        self.powers = []
    def step(self):
        self.powers.append(self.drain)
        self.grid.powers[-1] -= self.powers[-1]

class Conv:
    def __init__(self, name, sim):
        self.name       = name
        sim.convs[name] = self

class Boiler(Conv):
    def __init__(self, name, sim, inputgrid, outputgrid, efficiency=0.85):
        Conv.__init__(self, name, sim)
        self.inputgrid = sim.grids[inputgrid]
        self.outputgrid = sim.grids[outputgrid]
        self.inputgrid.sinks.append(self)
        self.outputgrid.sources.append(self)
        self.efficiency = efficiency
        self.powers = []
    def step(self):
        self.powers.append(0)
        if self.outputgrid.powers[-1] < 0:
            self.powers[-1] += self.outputgrid.powers[-1] / self.efficiency
            self.inputgrid.powers[-1] += self.powers[-1]
            self.outputgrid.powers[-1] = 0
        else:
            pass

class Storage:
    def __init__(self, name, sim, grid):
        self.name          = name
        sim.storages[name] = self
        self.grid          = sim.grids[grid]
        self.grid.storages.append(self)

class IdealBattery:
    def __init__(self, name, sim, grid, capacity, initialCharge):
        Storage.__init__(self, name, sim, grid)
        self.capacity = capacity
        self.charges  = [initialCharge]
    def soc(self):
        return self.charges[-1]/self.capacity
    def step(self):
        self.charges.append(self.charges[-1])
        if self.charges[-1] + self.grid.powers[-1] > self.capacity:
            self.grid.powers[-1] -= self.capacity - self.charges[-1]
            self.charges[-1] = self.capacity
        elif self.charges[-1] + self.grid.powers[-1] < 0:
            self.grid.powers[-1] += self.charges[-1]
            self.charges[-1] = 0
        else:
            self.charges[-1] += self.grid.powers[-1]
            self.grid.powers[-1] = 0

def test1():
    irradiance = [ 13, 24, 41, 90, 114, 108, 102, 105, 88, 90, 53, 16, 13 ]
    hushel = 500
    
    s = Simulation()
    Grid('El', s)
    Grid('Ved', s)
    Grid('Värme', s)
    SimpleSolar('Solceller', s, 'El', irradiance, 0.2, 30)
    SimpleSink('Hushållsel', s, 'El', hushel)
    IdealBattery('Batteri', s, 'El', 50, 25)
    Boiler('Värmepanna', s, 'Ved', 'El', 0.25)
    for _ in irradiance:
        s.step()
    
    # Plot
    for gridname, grid in s.grids.items():
        grid.plot()

#test1()

class TestSim:
    def __init__(self):
        self.grids = {}
        self.entities = {}

class TestGrid:
    def __init__(self, name, sim):
        self.name = name
        sim.grids[name] = self
        self.powers = { self.name : [] }
        self.entities = []

class TestEntity:
    def __init__(self, name, sim, grid):
        self.name = name
        sim.entities[name] = self
        self.grid   = sim.grids[grid]
        self.grid.entities.append(self)
        self.powers = { self.grid.name : [] }
        self.grid.powers[self.name] = self.powers[self.grid.name]

class TestEntity2:
    def __init__(self, name, sim, grid1, grid2):
        self.name = name
        sim.entities[name] = self
        self.grid1   = sim.grids[grid1]
        self.grid1.entities.append(self)
        self.grid2   = sim.grids[grid2]
        self.grid2.entities.append(self)
        self.powers = { self.grid1.name : []
                      , self.grid2.name : []
                      }
        self.grid1.powers[self.name] = self.powers[self.grid1.name]
        self.grid2.powers[self.name] = self.powers[self.grid2.name]

s = TestSim()
TestGrid('El', s)
TestGrid('Värme', s)
TestEntity('Sol', s, 'El')
TestEntity2('Panna', s, 'El', 'Värme')

print(s.grids['El'].powers)
print(s.grids['Värme'].powers)
print(s.entities['Panna'].powers)

s.entities['Panna'].powers['El'].append(2)

print(s.grids['El'].powers)
print(s.grids['Värme'].powers)
print(s.entities['Panna'].powers)

s.grids['Värme'].powers['Panna'].append(2)

print(s.grids['El'].powers)
print(s.grids['Värme'].powers)
print(s.entities['Panna'].powers)
