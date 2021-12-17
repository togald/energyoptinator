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

def offgrid_house_sim():
    tvv = 20*150
    hushel = 6000
    # 150 m² vila
    varme = 18000-tvv-hushel
    # 100 m² villa
    #varme = 12000-tvv-hushel
    hushel = hushel/87600
    irradiance = [ 13, 24, 41, 90, 114, 108, 102, 105, 88, 90, 53, 16, 13 ] # kWh/m^2, month
    irr = se.hourly_to_6min(se.daily_to_hourly(se.monthly_to_daily(irradiance)))
    s = eo.Simulation('The off-grid house')
    eo.Grid('Electricity', s)
    eo.Grid('Heat', s)
    eo.Grid('Gasoline', s)
    eo.Grid('Wood pellets', s)
    eo.SimpleSink('Household electricity', s, 'Electricity', hushel)
    eo.TimevariantSink('Hot water', s, 'Heat', se.hourly_to_6min(se.daily_to_hourly(se.monthly_to_daily(se.hemsol_tvv(tvv)))))
    eo.TimevariantSink('Space heating', s, 'Heat', se.hourly_to_6min(se.daily_to_hourly(se.monthly_to_daily(se.hemsol_varme(varme)))))
    #eo.Battery('Battery', s, 'Electricity', 20, 15, 0.03/30/24/10)
    #eo.SimpleStorage('Accumulator', s, 'Heat', 50, 25)
    eo.SimpleSolar('Solar', s, 'Electricity', irr, 0.18, 40)
    heatreg = eo.OnoffRegulator(0.4, 0.6, 1)
    #heatsig = s.storages['Accumulator'].soc
    # Based on Valtis Viva GT stirling furnace, 20 kW thermal power and 1 kW electric power, 90% thermal efficiency.
    #eo.CHPboiler('Furnace', s, 'Wood pellets', 'Heat', 'Electricity', heatreg, heatsig, thermalRatedPower=2, electricityRatedPower=0.1, fuelUse=2.333333333333)
    # Based on Microgen natural gas generator, 5 kW thermal power, 1 kW electrical power, 6.5 kW fuel
    #eo.CHPboiler('Furnace', s, 'Wood pellets', 'Heat', 'Electricity', heatreg, heatsig, thermalRatedPower=.79, electricityRatedPower=0.07, fuelUse=1)
    elreg = eo.OnoffRegulator(0.3, 0.6, 1)
    #elsig = s.storages['Battery'].soc
    # Based on Honda EU22i. 1.8 kW electric power, 1,0909 l gasoline/h, heat recovery with efficiency of 80%
    # https://www.honda.se/industrial/get-a-brochure/_jcr_content/par1/textcolumnwithimagem/textColumn/richtextdownload_ba5/file.res/262264_PL_LO262264.pdf
    #eo.CHPboiler('Generator', s, 'Gasoline', 'Heat', 'Electricity', elreg, elsig, thermalRatedPower=0.66, electricityRatedPower=0.18, fuelUse=1.0145)
    # Based on Honda EU70is, Honda's most efficient gasoline generator.
    #eo.CHPboiler('Generator', s, 'Gasoline', 'Heat', 'Electricity', elreg, elsig, thermalRatedPower=1.75766, electricityRatedPower=0.55, fuelUse=2.7471)
    solheatreg = eo.OnoffRegulator(0.89, 0.9, 0, 1)
    #solheatsig = s.storages['Battery'].soc
    #eo.SimpleBoiler('Electric boiler', s, 'Electricity', 'Heat', solheatreg, solheatsig, 0.1, 0.1)
    for _ in range(87600):
        s.step()
    #s.plot_storages()
    #s.plot_all()
    totalelec = s.grids['Electricity'].powers['Electricity']
    totalheat = s.grids['Heat'].powers['Heat']
    heatfactor = [ e/(h+0.0000000000000001) for e, h in zip(totalelec, totalheat) ]
    
    fig = plt.figure()
    plt.plot(totalheat, label='Heat')
    plt.plot(totalelec, label='Electricity')
    plt.plot(heatfactor, label=f"Heat factor necessary, max: {max(heatfactor)*100:2.1f}%")
    plt.legend()
    plt.show()

    print(f"Start/stop for Generator: {len([ 1 for i in range(len(elreg.states)-2) if [elreg.states[i], elreg.states[i+1]] == [0, 1] ])}")
    print(f"Generator running time: {sum(elreg.states)/10}")
    print(f"Start/stop for Furnace: {len([ 1 for i in range(len(heatreg.states)-2) if [heatreg.states[i], heatreg.states[i+1]] == [0, 1] ])}")
    print(f"Furnace running time: {sum(heatreg.states)/10}")
    print()
    print(f"Generator fuel use: {sum(s.grids['Gasoline'].powers['Gasoline'])/1000:2.1f} MWh")
    print(f"Furnace fuel use: {sum(s.grids['Wood pellets'].powers['Wood pellets'])/1000:2.1f} MWh")
    print(f"Total solar provided: {sum(s.grids['Electricity'].powers['Solar'])/1000:2.1f} MWh")
    print(f"Total added energy: {(sum(s.grids['Gasoline'].powers['Gasoline']) + sum(s.grids['Wood pellets'].powers['Wood pellets']) + sum(s.grids['Electricity'].powers['Solar']))/1000:2.1f} MWh")
    print()
    print(f"Household electricity: {-sum(s.grids['Electricity'].powers['Household electricity'])/1000:2.1f} MWh")
    print(f"Space heating: {-sum(s.grids['Heat'].powers['Space heating'])/1000:2.1f} MWh")
    print(f"Hot water: {-sum(s.grids['Heat'].powers['Hot water'])/1000:2.1f} MWh")
    print(f"Total energy demand: {-(sum(s.grids['Electricity'].powers['Household electricity']) + sum(s.grids['Heat'].powers['Space heating']) + sum(s.grids['Heat'].powers['Hot water']))/1000:2.1f} MWh")
    print(f"Primary energy number according to BBR-29: {(sum(s.grids['Gasoline'].powers['Gasoline']) + sum(s.grids['Wood pellets'].powers['Wood pellets']))*0.6/150:3.1f} kWh/m², y")
    
if __name__ == '__main__':
    offgrid_house_sim()
