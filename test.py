import matplotlib.pyplot as plt
import energyoptinator as eo
import svenska_schabloner as se


def test1():
    hushel = 2000 # kWh/d
    s = simtest1(hushel, initBatt=hushel/2)
    solarGen = sum(s.entities['Solceller'].powers['El'])
    solarReq = 24
    print(solarReq)
    s = simtest1(hushel, initBatt=500, solarArea = solarReq)
    for _, grid in s.grids.items():
        grid.plot()
    s.plot_storages()

def test2():
    tvv = 3000
    varme = 10000
    hushel = 6700/8760
    s = eo.Simulation()
    eo.Grid('Värme', s)
    eo.Grid('El', s)
    eo.SimpleSink('Hushållsel', s, 'El', hushel)
    eo.SimpleSource('Värmeläck hushållsel', s, 'Värme', hushel*0.3)
    eo.TimevariantSink('tvv', s, 'Värme', se.daily_to_hourly(se.hemsol_tvv(tvv)))
    eo.TimevariantSink('Komfortvärme', s, 'Värme', se.daily_to_hourly(se.hemsol_varme(varme)))
    for _ in range(8760):
        s.step()
    for _, grid in s.grids.items():
        grid.plot()

def const():
    return 0.1

def offgrid_house_sim():
    tvv = 3000
    varme = 10000
    hushel = 6700/87600
    irradiance = [ 13, 24, 41, 90, 114, 108, 102, 105, 88, 90, 53, 16, 13 ] # kWh/m^2, month
    irr = se.hourly_to_6min(se.daily_to_hourly(se.monthly_to_daily(irradiance)))
    s = eo.Simulation('The off-grid house')
    eo.Grid('Electricity', s)
    eo.Grid('Heat', s)
    eo.Grid('Biogas', s, 'nm³/h')
    eo.Grid('Wood pellets', s, 'kg/h')
    eo.SimpleSink('Household electricity', s, 'Electricity', hushel)
    eo.TimevariantSink('Hot water', s, 'Heat', se.hourly_to_6min(se.daily_to_hourly(se.hemsol_tvv(tvv))))
    eo.TimevariantSink('Space heating', s, 'Heat', se.hourly_to_6min(se.daily_to_hourly(se.hemsol_varme(varme))))
    eo.SimpleStorage('Accumulator', s, 'Heat', 28, 5)
    eo.Battery('Battery', s, 'Electricity', 20, 10, 0.001)
    eo.SimpleSolar('Solar', s, 'Electricity', irr, 0.18, 60)
    heatreg = eo.OnoffRegulator(0.3, 0.5, 0)
    heatsig = s.storages['Accumulator'].soc
    eo.CHPboiler('Furnace', s, 'Wood pellets', 'Heat', 'Electricity', heatreg, heatsig, thermalRatedPower=1.4, electricityRatedPower=0.1, fuelUse=0.52)
    elreg = eo.OnoffRegulator(0.3, 0.5, 0)
    elsig = s.storages['Battery'].soc
    eo.CHPboiler('Generator', s, 'Biogas', 'Heat', 'Electricity', elreg, elsig, thermalRatedPower=1.2, electricityRatedPower=0.22, fuelUse=0.15)
    solheatreg = eo.OnoffRegulator(0.7, 0.9, 0, 1)
    solheatsig = s.storages['Battery'].soc
    eo.SimpleBoiler('Electric boiler', s, 'Electricity', 'Heat', solheatreg, solheatsig, 2, 2)
    for _ in range(87600):
        s.step()
    s.plot_all()

if __name__ == '__main__':
    offgrid_house_sim()
