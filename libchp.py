#!/usr/bin/env python3 

import energyoptinator as enopt

gasoline_lit_to_kWh = 9.3
woodpellets_kg_to_kWh = 4.9
charcoal_kg_to_kWh = 8.716666666666667
methane_kg_to_kWh = 9.97/.657
methane_nm3_to_kWh = 9.97

"""Generators
Honda EU22i: 1800 W, 3.6/(3+35/60) l/h, eff=19.3%
Honda EU30is: 2800 W, 13/8 l/h, eff=18.5%
Honda EU70is: 5500 W, 19.2/6.5 l/h, eff=20.02%
Honda EM5500CXS: 5 kW, 23.5/8 l/h, eff=18.3%

Micro-CHP:

"""

print(1.1/(2.8*woodpellets_kg_to_kWh-0.5*charcoal_kg_to_kWh))
print(1.8/((3.6/(3+35/60))*9.3))
print(2.8/((13/8)*9.3))
print(5.5/((19.2/6.5)*9.3))
print(5/((23.5/8)*9.3))
print(0.7/10)
print(0.7/7.9)
