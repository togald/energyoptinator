#!/usr/bin/env python3

from scipy.signal import savgol_filter
from energyoptinator import *

## Hemsol functions
#
# These functions provide a convenient way to extend yearly values for
# heat and hot water consumption into sensible monthly values.

def _hemsol(yearly, mod):
    """ Hemsol helper function
    """
    data = []
    for month in range(12):
            data.append( (yearly/12) * mod[month] )
    return data

def hemsol_tvv(yearly):
    """ Hemsol hot water splitter. Takes a yearly hot water usage and
    splits it into monthly usage.
    """
    modifiers = [1.1, 1.1, 1, 1, 1, 0.95, 0.8, 0.95, 1, 1, 1, 1.1]
    return _hemsol(yearly, modifiers)

def hemsol_tvv_smoothed(yearly):
    """ Hemsol hot water splitter. Takes a yearly hot water usage,
    splits it into daily usage and smooths it.
    """
    return savgol_filter(monthly_to_daily(hemsol_tvv(yearly)), 201, 3)

def hemsol_varme(yearly):
    """ Hemsol comfort heat splitter. Takes a yearly comfort heat usage
    and splits it into monthly usage.
    """
    modifiers = [2, 1.7, 1.7, 1.3, 0.6, 0.2, 0, 0, 0.4, 0.9, 1.4, 1.8]
    return _hemsol(yearly, modifiers)

def hemsol_varme_smoothed(yearly):
    """ Hemsol comfort heat splitter. Takes a yearly hot water usage,
    splits it into daily usage and smooths it.
    """
    return savgol_filter(monthly_to_daily(hemsol_varme(yearly)), 201, 4)

def demo1():
    timesteps = 8760
    hushel = 6700/timesteps
    tvv = daily_to_hourly(hemsol_tvv_smoothed(3000))
    varme = daily_to_hourly(hemsol_varme_smoothed(12000))

    s = Simulation('Demo 1')
    #enopt.Grid('El', s)
    Grid('Värme', s)
    #enopt.SimpleSink('Hushållsel', s, 'El', hushel)
    TimevariantSink('Tappvarmvatten', s, 'Värme', tvv)
    TimevariantSink('Komfortvärme', s, 'Värme', varme)
    for _ in range(timesteps):
        s.step()
    for _, grid in s.grids.items():
        grid.plot()

if __name__ == "__main__":
    demo1()
