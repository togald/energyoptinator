# Energy-optinator
This is a framework for running energy simulations for small- and medium-sized energy systems. It can be used for larger systems, but those usually require more intricate analysis and behave more dynamically. Typicall questions this program can help answer:

- How much solar power should I add to my house? 
- If I change the water temperature my furnace turns on at, is that going to affect its fuel use? 
- I don't have a grid connection, how much fuel is my generator going to use? 

The real benefit of a simulation like this over an Excel spreadsheet is that it can also tell us stuff like cycle degradation in batteries, take self-discharge rates into account etc. 

## How to use
The standard library is `energyoptinator.py`. `test.py` contains a few test cases to help you get started with simulations, and `svenska_schabloner.py` is an extra library containing somewhat accurate average values for a swedish household's energy use. 

## Todo
- More comments in code
- Use numpy-arrays for data? Pandas time series, maybe? 
- Make simulation time-aware? Automatic data interpolation according to simulation parameters? 
    - Datetime objects to store date, automatic interpolation depending on desired resolution? This could be where Pandas comes in. 
- Read data from file, methods for each object? Centralized method, have it return data in the right format for the simulation? 
