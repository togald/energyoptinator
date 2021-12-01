class Storage:
    class IdealBattery:
        def __init__( self, grid, capacity, content ):
            self.grid     = grid
            self.capacity = capacity
            self.contents = [ content ]
        def soc(self):
            return self.contents[-1] / self.capacity
        def socs(self):
            return [ c / self.capacity for c in self.contents ]

class Source:
    class IdealSource:
        def __init__( self, grid, generation ):
            self.grid = grid
            self.generation = generation
    
    class RegulatedSource:
        def __init__( self, grid, maxpower, regInit=0 ):
            self.grid = grid
            self.maxpower = maxpower
            self.power = [ maxpower * regInit ]
        def step(self, reg):
            self.power.append(self.maxpower*reg)

class Sink:
    class IdealSink:
        def __init__( self, grid, drain ):
            self.grid = grid
            self.drain = drain

class Regulator:
    class Onoff:
        def __init__( self, onThr, offThr, initState=0 ):
            self.onThr  = onThr
            self.offThr = offThr
            self.states = [initState]
        def step(self, input):
            if self.states[-1] == 1 and input > self.offThr:
                self.states.append(0)
            elif self.states[-1] == 0 and input < self.onThr: 
                self.states.append(1)
            else:
                self.states.append(self.states[-1])

grids = { 'elec': [0] }
irradiance = [0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 3, 4, 4, 4]
demand     = [2, 2, 2, 2, 2, 5, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
timesteps = min(len(irradiance), len(demand))

batt = Storage.IdealBattery( grids['elec'], 10, 5 )
solar = Source.IdealSource( grids['elec'], irradiance )
hhel = Sink.IdealSink( grids['elec'], demand )
battreg = Regulator.Onoff( 0.3, 0.7 )
gen = Source.RegulatedSource( grids['elec'], 5)
print('soc | pwr  | regu')

for i in range(timesteps):
    gen.step(battreg.states[i])
    batt.contents.append(batt.contents[-1] + solar.generation[i] + gen.power[i] - hhel.drain[i])
    battreg.step(batt.soc())
    print(f"{str(batt.soc()):4s} | {gen.power[-1]:4g} | {battreg.states[-1]:4g}")
