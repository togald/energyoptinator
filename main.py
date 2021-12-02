class Simulation:
    def __init__(self):
        self.grids = {}
    def assemble(self):
        for grid in grids:
            pass
    class Grid:
        def __init__(self, name, sim):
            sim.grids[name] = self
            self.power      = []
            self.sources    = []
            self.sinks      = []
            self.storages   = []
            self.converters = []

class Source:
    class IdealSource:
        def __init__( self, grid, generation ):
            self.grid = grid
            grid.sources.append(self)
            self.generation = generation
            self.power      = [ generation[0] ]
        def step(self):
            self.power.append(self.generation[len(self.power)-1])
    
    class RegulatedSource:
        def __init__( self, grid, maxpower, reg ):
            self.grid       = grid
            grid.sources.append(self)
            self.maxpower   = maxpower
            self.reg        = reg
            self.power      = [ maxpower*self.reg.sigs[0] ]
        def step(self):
            self.power.append(self.maxpower*self.reg.step())

class Sink:
    class IdealSink:
        def __init__( self, grid, drain ):
            self.grid = grid
            grid.sinks.append(self)
            self.drain = drain

class Storage:
    class IdealBattery:
        def __init__( self, grid, capacity, initialCharge ):
            self.grid     = grid
            grid.storages.append(self)
            self.capacity = capacity
            self.contents = [ initialCharge ]
        def soc(self):
            return self.contents[-1] / self.capacity
        def socs(self):
            return [ c / self.capacity for c in self.contents ]

class Converter:
    class IdealConverter:
        def __init__( inputgrid, outputgrid ):
            self.inputgrid = inputgrid
            inputgrid.converters.append(self)
            self.outputgrid = outputgrid
            outputgrid.converters.append(self)

class Regulator:
    class Onoff:
        def __init__( self, onThr, offThr, sig, initialState ):
            self.onThr  = onThr
            self.offThr = offThr
            self.sig    = sig
            self.sigs   = [initialState]
        def step(self):
            if self.sigs[-1] == 1 and self.sig > self.offThr:
                self.sigs.append(0)
            elif self.sigs[-1] == 0 and self.sig < self.onThr: 
                self.sigs.append(1)
            else:
                self.sigs.append(self.sigs[-1])
            return self.sigs[-1]

def test1():
    elec = Grid()
    irradiance = [0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 3, 4, 4, 4]
    demand     = [2, 2, 2, 2, 2, 5, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    timesteps = min(len(irradiance), len(demand))
    
    batt = Storage.IdealBattery( elec, 10, 5 )
    solar = Source.IdealSource( elec, irradiance )
    hhel = Sink.IdealSink( elec, demand )
    gen = Source.RegulatedSource( elec, 5, Regulator.Onoff( 0.3, 0.7, batt.soc(), 0 ))
    print('soc | pwr  | regu')
    
    for i in range(timesteps):
        for source in elec.sources:
            source.step()
            print(source.power)
        #print(f"{str(batt.soc()):4s} | {gen.power[-1]:4g} | {gen.reg.sigs[-1]:4g}")

def test2():
    sim = 

if __name__ == "__main__":
    test2()
