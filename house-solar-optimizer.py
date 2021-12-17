import matplotlib.pyplot as plt
import energyoptinator as eo
import svenska_schabloner as se

def sim(atemp=150, hushel=6000, varme=18000, solar_efficiency=0.18, solar_area=0):
    tvv = 20*atemp
    hushel = hushel
    varme = atemp*120-tvv-hushel
    hushel = hushel/8760
    irr = se.monthly_to_power([ 13, 24, 41, 90, 114, 108, 102, 105, 88, 90, 53, 16 ]) # kWh/m^2, month
    tvv = se.monthly_to_power(se.hemsol_tvv(tvv))
    varme = se.monthly_to_power(se.hemsol_varme(varme))
    s = eo.Simulation('Solar optimizer')
    eo.Grid('Electricity', s)
    eo.Grid('Heat', s)
    eo.SimpleSink('Household electricity', s, 'Electricity', hushel)
    eo.TimevariantSink('Hot water', s, 'Heat', tvv)
    eo.TimevariantSink('Space heating', s, 'Heat', varme)
    eo.SimpleSolar('Solar', s, 'Electricity', irr, solar_efficiency, solar_area)
    for _ in range(12):
        s.step()
    return max([ e/h for e, h in zip(s.grids['Electricity'].powers['Electricity'], s.grids['Heat'].powers['Heat']) ])

def plot_heatfactor():
    atemp = 150
    heatfactors = []
    for a in range(int(atemp/5), atemp):
        heatfactors.append(sim(atemp=atemp, solar_area=a))
    fig = plt.figure()
    plt.plot(heatfactors)
    plt.xlabel('Solar area')
    plt.ylabel('Maximum heat factor')
    plt.show()

if __name__ == '__main__':
    plot_heatfactor()
