#!/usr/bin/env python3

from scipy.signal import savgol_filter

def monthly_to_daily(months_iter):
    months = [31, 28, 31, 30, 31, 30, 31, 30, 31, 31, 30, 31]
    days =  []
    for month, data in zip(months, months_iter):
        for _ in range(month):
            days.append(data/month)
    return savgol_filter(days, 201, 3)

def daily_to_hourly(days_iter):
    hours = []
    for day in days_iter:
        for _ in range(24):
            hours.append(day/24)
    return savgol_filter(hours, 201, 3)

def hourly_to_6min(hours_iter):
    sec = []
    for i in hours_iter:
        for _ in range(10):
            sec.append(i/10)
    return sec

def _hemsol(yearly, modifiers):
    months = [31, 28, 31, 30, 31, 30, 31, 30, 31, 31, 30, 31]
    days = []
    for month, mod in zip(months, modifiers):
        for _ in range(month):
            days.append( (yearly/12) * mod/month )
    return savgol_filter(days, 201, 3)

def hemsol_tvv(yearly):
    modifiers = [1.1, 1.1, 1, 1, 1, 0.95, 0.8, 0.95, 1, 1, 1, 1.1]
    return _hemsol(yearly, modifiers)

def hemsol_varme(yearly):
    modifiers = [2, 1.7, 1.7, 1.3, 0.6, 0.2, 0, 0, 0.4, 0.9, 1.4, 1.8]
    return _hemsol(yearly, modifiers)

def demo1():
    import energyoptinator as enopt
    
    timesteps = 8760
    hushel = 6700/timesteps
    tvv = daily_to_hourly(hemsol_tvv(3000))
    varme = daily_to_hourly(hemsol_varme(12000))
    
    s = enopt.Simulation('Demo 1')
    enopt.Grid('El', s)
    enopt.Grid('Värme', s)
    enopt.SimpleSink('Hushållsel', s, 'El', hushel)
    enopt.TimevariantSink('Tappvarmvatten', s, 'Värme', tvv)
    enopt.TimevariantSink('Komfortvärme', s, 'Värme', varme)
    for _ in range(timesteps):
        s.step()
    for _, grid in s.grids.items():
        grid.plot()

if __name__ == "__main__":
    demo1()
