# BurnMan - a lower mantle toolkit
# Copyright (C) 2012, 2013, Heister, T., Unterborn, C., Rose, I. and Cottaar, S.
# Released under GPL v2 or later.

"""

example_composition
-------------------
    
This example shows how to create different minerals, how to compute seismic
velocities, and how to compare them to a seismic reference model.

There are many different ways in BurnMan to combine minerals into a
composition. Here we present a couple of examples:

1. Two minerals mixed in simple mole fractions. Can be chosen from the BurnMan
   libraries or from user defined minerals (see example_user_input_material)
2. Example with three minerals
3. Using preset solid solutions
4. Defining your own solid solution


To turn a method of mineral creation "on" the first if statement above the
method must be set to True, with all others set to False.

Note: These minerals can include a spin transition in (Mg,Fe)O, see
example_spintransition.py for explanation of how to implement this

*Uses:*

* :doc:`mineral_database`
* :class:`burnman.composite.Composite`
* :class:`burnman.minerals.Mineral`
* :class:`burnman.solidsolution.SolidSolution`

*Demonstrates:*

* Different ways to define a composite
* Using minerals and solid solutions
* Compare computations to seismic models

"""

import os, sys, numpy as np, matplotlib.pyplot as plt
#hack to allow scripts to be placed in subdirectories next to burnman:
if not os.path.exists('burnman') and os.path.exists('../burnman'):
    sys.path.insert(1,os.path.abspath('..'))

import burnman
from burnman import minerals

if __name__ == "__main__":



    # To compute seismic velocities and other properties, we need to supply
    # burnman with a list of minerals (phases) and their molar abundances. Minerals
    # are classes found in burnman.minerals and are derived from
    # burnman.minerals.material.
    # Here are a few ways to define phases and molar_abundances:

    #Example 1: two simple fixed minerals
    if True:
        amount_perovskite = 0.95
        rock = burnman.Composite([amount_perovskite, 1.0-amount_perovskite],
                                 [minerals.SLB_2011.mg_perovskite(),
                                  minerals.SLB_2011.periclase()])


    #Example 2: three materials
    if False:
        rock = burnman.Composite([0.7, 0.2, 0.1],
                                 [minerals.SLB_2011.fe_perovskite(),
                                  minerals.SLB_2011.ferropericlase(0.5),
                                  minerals.SLB_2011.stishovite()])


    #Example 3: Mixing solid solutions
    if False:
        # Defining a rock using a predefined solid solution from the mineral library database.
        preset_solidsolution=minerals.SLB_2011.mg_fe_perovskite()
        # The line below is optional to see which endmembers (and in which order) are in the solid solution
        #print preset_solidsolution.endmembers
        #Set molar_fraction of mg_perovskite, fe_perovskite and al_perovskite
        preset_solidsolution.set_composition([0.9,0.1,0.]) # Set molar_fraction of mg_perovskite, fe_perovskite and al_perovskite
        rock = burnman.Composite([0.8, 0.2], phases=[preset_solidsolution, minerals.SLB_2011.periclase()])


    #Example 4: Defining your own solid solution
    if False:
        # Define a new SolidSolution with mg and fe perovskite endmembers
        new_solidsolution = burnman.SolidSolution([[minerals.SLB_2011.mg_perovskite()],
                                          [minerals.SLB_2011.fe_perovskite()]])
        # Set molar fraction of endmembers
        new_solidsolution.set_composition([0.9,0.1])
        rock=burnman.Composite([0.8, 0.2], [new_solidsolution, minerals.SLB_2011.periclase()])




    #seismic model for comparison:
    # pick from .prem() .slow() .fast() (see burnman/seismic.py)
    seismic_model = burnman.seismic.PREM()
    number_of_points = 20 #set on how many depth slices the computations should be done
    # we will do our computation and comparison at the following depth values:
    depths = np.linspace(700e3, 2800e3, number_of_points)
    #alternatively, we could use the values where prem is defined:
    #depths = seismic_model.internal_depth_list()
    seis_p, seis_rho, seis_vp, seis_vs, seis_vphi = seismic_model.evaluate_all_at(depths)


    temperature = burnman.geotherm.brown_shankland(seis_p)


    print "Calculations are done for:"
    rock.debug_print()

    moduli_list = burnman.calculate_moduli(rock, seis_p, temperature)
    moduli = burnman.average_moduli(moduli_list, burnman.averaging_schemes.VoigtReussHill())
    mat_vp, mat_vs, mat_vphi = burnman.compute_velocities(moduli)
    mat_K = np.array([m.K for m in moduli])
    mat_G = np.array([m.G for m in moduli])
    mat_rho = np.array([m.rho for m in moduli])

    [vs_err, vphi_err, rho_err] = burnman.compare_chifactor (
        [mat_vs,mat_vphi,mat_rho],[seis_vs,seis_vphi,seis_rho])


    # PLOTTING

    # plot vs
    plt.subplot(2,2,1)
    plt.plot(seis_p/1.e9,mat_vs/1.e3,color='b',linestyle='-',marker='o', \
             markerfacecolor='b',markersize=4,label='computation')
    plt.plot(seis_p/1.e9,seis_vs/1.e3,color='k',linestyle='-',marker='o', \
             markerfacecolor='k',markersize=4,label='reference')
    plt.title("Vs (km/s)")
    plt.xlim(min(seis_p)/1.e9,max(seis_p)/1.e9)
    plt.ylim(5.1,7.6)
    plt.legend(loc='lower right')
    plt.text(40,7.3,"misfit= %3.3f" % vs_err)

    # plot Vphi
    plt.subplot(2,2,2)
    plt.plot(seis_p/1.e9,mat_vphi/1.e3,color='b',linestyle='-',marker='o', \
             markerfacecolor='b',markersize=4)
    plt.plot(seis_p/1.e9,seis_vphi/1.e3,color='k',linestyle='-',marker='o', \
             markerfacecolor='k',markersize=4)
    plt.title("Vphi (km/s)")
    plt.xlim(min(seis_p)/1.e9,max(seis_p)/1.e9)
    plt.ylim(7,12)
    plt.text(40,11.5,"misfit= %3.3f" % vphi_err)

    # plot density
    plt.subplot(2,2,3)
    plt.plot(seis_p/1.e9,mat_rho/1.e3,color='b',linestyle='-',marker='o', \
             markerfacecolor='b',markersize=4)
    plt.plot(seis_p/1.e9,seis_rho/1.e3,color='k',linestyle='-',marker='o', \
             markerfacecolor='k',markersize=4)
    plt.title("density (kg/m^3)")
    plt.xlim(min(seis_p)/1.e9,max(seis_p)/1.e9)
    plt.text(40,4.3,"misfit= %3.3f" % rho_err)
    plt.xlabel("Pressure (GPa)")


    # plot geotherm
    plt.subplot(2,2,4)
    plt.plot(seis_p/1e9,temperature,color='r',linestyle='-',marker='o', \
             markerfacecolor='r',markersize=4)
    plt.title("Geotherm (K)")
    plt.xlim(min(seis_p)/1.e9,max(seis_p)/1.e9)
    plt.xlabel("Pressure (GPa)")

    plt.savefig("output_figures/example_composition.png")
    plt.show()
