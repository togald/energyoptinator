## Typical workflow
1. Set up simulation. 
2. Set up grids
3. Set up entities
4. Loop through simulation
5. Plot whatever result you need

## Simulation flow
1. Simulation calls entities' step() methods, in order: 
    1. Source
    2. Sink
    3. Strage
    4. Conv
2. Entities' step() updates the entity and return control to Simulation. 
3. Simulation calls all Grid.collect(), which collect the grids' 
