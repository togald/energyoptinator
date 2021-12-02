class Simulation:    
    def __init__(self, grids = {}, sources = {}, sinks = {}, convs = {}, storages = {}):
        self.grids    = grids
        self.sources  = sources
        self.sinks    = sinks
        self.convs    = convs
        self.storages = storages
    def step(self):
        for name, grid in self.grids.items(): 
            grid.powers.append(0)
        for name, source in self.sources.items():
            source.step()
        for name, sink in self.sinks.items():
            sink.step()
        for name, conv in self.convs.items():
            conv.step()
        for name, storage in self.storages.items():
            storage.step()

class Grid:
    def __init__(self, name, sim):
        self.name       = name
        sim.grids[name] = self
        self.powers     = []

class Source:
    def __init__(self, name, sim):
        self.name         = name
        sim.sources[name] = self

class SimpleSolar(Source):
    def __init__(self, name, sim, grid, irradiance, efficiency, maxpower):
        Source.__init__(self, name, sim)
        self.grid       = grid
        self.irradiance = irradiance
        self.efficiency = efficiency
        self.maxpower   = maxpower
        self.powers     = []
    def step(self):
        self.powers.append(self.irradiance[len(self.powers)] * self.efficiency * self.maxpower)
        self.grid.powers[-1] += self.powers[-1]

class Sink:
    def __init__(self, name, sim, grid):
        self.name       = name
        sim.sinks[name] = self
        self.grid       = grid

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

class Storage:
    def __init__(self, name, sim, grid):
        self.name          = name
        sim.storages[name] = self
        self.grid          = grid

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
            self.grid.powers -= self.capacity - self.charges[-1]
            self.charges[-1] = self.capacity
        elif self.charges[-1] + self.grid.powers[-1] < 0:
            self.grid.powers[-1] += self.charges[-1]
            self.charges[-1] = 0
        else:
            self.charges[-1] += self.grid.powers[-1]
            self.grid.powers[-1] = 0

s = Simulation()
Grid('electricity', s)
SimpleSolar('solar1', s, s.grids['electricity'], [0, 1, 2], 0.2, 30)
SimpleSink('sink1', s, s.grids['electricity'], [6, 6, 6])
IdealBattery('bat1', s, s.grids['electricity'], 10, 5)
for _ in range(3):
    s.step()
print(s.sources['solar1'].powers)
print(s.sinks['sink1'].powers)
print(s.grids['electricity'].powers)
print(s.storages['bat1'].charges)
