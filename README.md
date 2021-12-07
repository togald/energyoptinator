# energyoptinator

## Simulation class
### Standard methods:
- step(): moves simulation one step forward

## Grid class
### Standard methods:
- plot(): plots the grid with all local sinks, sources and storages
  
## Source class
A Source provides an inflow of energy to one or more grids. 

### Standard methods: 
- plot(): plots the Source's energy flow(s) in all of its grid(s). 
- step(): timesteps the Source forward. 

## Sink class
A sink drains power from one or more grids. 

### Standard methods: 
- plot(): plots the Sink's energy flow(s) in all of its grid(s). 
- step(): timesteps the Sink forward. 

## Storage class
A storage stores power from one (1) grid, and is able to release stored energy back to the grid. Typical storages are batteries, accumulator tanks. 

### Standard methods:
- plot(): plots the Storage's flow of energy, and its current level of charge. May also plot energy losses, if any. 
- step(): timesteps the Storage forward. 

## Conv class
A Conv (converter) converts energy between different forms. Typically conversion happens one-way and has an efficiency, for two-way conversion two separate converters should be used. 

### Standard methods:
- plot(): plots the Conv's energy flows in all of its grids. 
- step(): timesteps the Conv forward. 
