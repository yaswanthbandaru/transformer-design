import pandas as pd
import numpy as np 
import math
from autotransformer import *

"""
==========================================================================================
******************************************************************************************
                                STRIP CLASS

Proporties:
        => k_f
        => k_u
        => frequency
        => input_voltage
        => output_voltage
        => ouput_power
        => efficiency
        => regulation
        => lamination_data
        => swg_data
        => current_density

Methods:
        => __init__ 
        => find_swg
        => cost(s, t, wl, ww)
******************************************************************************************
"""

class Strip(AutoTransformer):
    
    super(AutoTransformer).__init__

    insulation_thickness = 0.2  # mm
    bobbin_thickness = 1.5  # mm
    Resistivity_conductor = 1.68 * 10**-6 # ohm cm
    Density_of_core = 7.65 # g/cm^3
    stack_data = []

    # let's define the constructor
    def __init__(self,
        frequency,
        input_voltage,
        output_voltage,
        output_power,
        efficiency,
        regulation,
        flux_density,
        current_density):
        self.frequency = frequency
        self.input_voltage = input_voltage
        self.output_voltage = output_voltage
        self.output_power = output_power
        self.efficiency = efficiency
        self.regulation = regulation
        self.flux_density = flux_density
        self.current_density = current_density 

        # apparent power
        self.apparent_power = self.apparent_power(self.output_power,  self.efficiency)
        # area product 
        self.area_product = self.area_product(self.apparent_power, self.flux_density, self.current_density, self.frequency, self.k_f, self.k_u)
        ################# primary wire #############################
        # calculate the input current
        self.input_Current = self.output_power / self.input_voltage
        # bare area in mm2
        self.a_wp = self.bare_area(self.input_Current, self.current_density)
        # for primary wire
        self.required_swg_primary, self.diameter_of_primary_wire, self.actual_a_wp = self.find_swg(self.a_wp)
        self.d_wp = self.diameter_of_primary_wire
        ################## secondary wire ###########################
        # calculate secondary current
        self.secondary_current = self.output_power / self.output_voltage
        # bare area secondary in mm2
        self.a_ws = self.bare_area(self.secondary_current, self.current_density)
        # for secondary wire
        self.required_swg_secondary, self.diameter_of_secondary_wire, self.actual_a_ws = self.find_swg(self.a_ws)
        self.d_ws = self.diameter_of_secondary_wire
        


    def total_cost(self, stack, tongue, winding_width, winding_length):
        # self.stack = stack
        # self.tongue = tongue 
        # self.winding_width = winding_width
        # self.winding_length = winding_length 
        wl = winding_length
        ww = winding_width
        
        if stack < 5 * tongue:
            self.core_area_A_c = self.core_area(stack, tongue)
            # ***************** primary wire *****************************
            self.Np = self.primary_turns(self.input_voltage, self.flux_density, self.frequency, self.core_area_A_c)
            self.Np = round(self.Np)
            self.tpl_Primary = math.floor(self.turns_per_layer(wl, self.d_wp))
            self.nlp_Primary = math.ceil(self.number_of_layers(self.Np, self.tpl_Primary))
            self.built_Primary = self.built_primary(self.nlp_Primary, self.d_wp, self.bobbin_thickness)
            self.mtl_Primary = self.mtl_primary(tongue, stack, self.bobbin_thickness, self.built_Primary)
            self.length_primary = self.length(self.mtl_Primary, self.Np)
            self.resistance_P = self.resistance(self.Resistivity_conductor, self.length_primary, self.actual_a_wp)
            self.primaryCopperLoss = self.conductor_loss(self.input_Current, self.resistance_P)
            # ***************** primary wire *****************************
            # ***************** secondary wire ****************************
            self.Ns = self.secondary_turns(self.Np, self.output_voltage, self.regulation, self.input_voltage)
            self.Ns = round(self.Ns)
            self.tpl_Secondary = math.floor(self.turns_per_layer(winding_length, self.d_ws))
            self.nlp_Secondary = math.ceil(self.number_of_layers(self.Ns, self.tpl_Secondary))
            self.built_Secondary = self.built_secondary(self.Ns, self.d_ws, self.insulation_thickness)
            self.mtl_Secondary = self.mtl_secondary(tongue, stack, self.built_Primary, self.built_Secondary, self.bobbin_thickness)
            self.length_secondary = self.length(self.mtl_Secondary, self.Ns)
            self.resistance_S = self.resistance(self.Resistivity_conductor, self.length_secondary, self.actual_a_ws)
            self.secondaryCopperLoss = self.conductor_loss(self.secondary_current, self.resistance_S)
            # ***************** secondary wire *****************************
            # core loss factor
            self.coreLossFactor = self.core_loss_factor(self.frequency, self.flux_density)
            # total built
            self.total_Built = self.total_built(self.built_Primary, self.built_Secondary)
            # winding width condition 
            if (ww * 0.9 > self.total_Built):
                # copper weight in kg
                weight_copper_primary = self.length_primary * self.required_swg_primary['Conductor Weight for 1000m/Kg'].max() / 10**5
                weight_copper_secondary = self.length_secondary * self.required_swg_secondary['Conductor Weight for 1000m/Kg'].max()  / 10**5 
                self.weight_copper_kg  = weight_copper_primary + weight_copper_secondary
                # for core weight in kg
                self.total_cu_loss = self.total_copper_loss(self.primaryCopperLoss, self.secondaryCopperLoss)
                self.Volume_of_core = self.volume_of_core(stack, tongue, winding_width, winding_length)
                self.weight_of_core_kg = self.weight_of_core(self.Density_of_core, self.Volume_of_core) / 1000  # kg
                # for core loss
                self.Core_loss = self.core_loss(self.coreLossFactor, self.weight_of_core_kg)
                self.total_loss = self.total_loss(self.total_cu_loss, self.Core_loss)
                # surface area and volume
                self.conductorSurfaceArea = self.conductor_surface_area(self.total_Built, tongue, winding_length)  # cm2
                self.coreSurfaceArea = self.core_surface_area(stack, tongue, winding_length, winding_width)
                self.totalSurfaceArea = self.total_surface_area(stack, tongue, winding_length, winding_width, self.total_Built)
                # calculate temperature rise in copper and core
                psi_copper = self.psi(self.total_cu_loss, self.conductorSurfaceArea)
                psi_core = self.psi(self.Core_loss, self.coreSurfaceArea)
                self.copperTemperatureRise = self.temperature_rise(psi_copper)
                self.coreTemperatureRise = self.temperature_rise(psi_core)
                # calculate cost of the design
                self.Cost = self.cost(self.weight_of_core_kg, self.weight_copper_kg, rate_copper=950, rate_fe=250)
                # return self.cost
                # preparing list for return for the method
                results_data = {
                    'Area product': stack * tongue * wl * ww,
                    'Stack mm': stack,
                    'Tongue mm': tongue,
                    'Cu surface area': self.conductorSurfaceArea,
                    'Core surface area': self.coreSurfaceArea,
                    'Temperature rise Cu': self.copperTemperatureRise,
                    'Temperature rise Fe': self.coreTemperatureRise,
                    'Cost': self.Cost,
                }
                self.stack_data(results_data) 
                return results_data
                # return self.cost


                

