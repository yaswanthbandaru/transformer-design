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
        print(f'Apparent power : {self.apparent_power}')
        # area product 
        self.area_product = self.area_product(self.apparent_power, self.flux_density, self.current_density, self.frequency, self.k_f, self.k_u)
        print(f'Area product : {self.area_product}')
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

        ###########checking outputs
        print(f'Input current : {self.input_Current}')
        print(f'a_wp : {self.a_wp}')
        print(f'a_ws : {self.a_ws}')
        print(f'primary swg : swg {self.required_swg_primary}')
        print(f'secondary swg : swg {self.required_swg_secondary}')
        
        


    def total_cost(self, stack, tongue, winding_width, winding_length):
        wl = winding_length
        ww = winding_width
        
        # if stack < 5 * tongue:
        A_c = self.core_area(stack, tongue)  # cm2

        # ************************ Primary Wire ******************************** 
        Number_of_primary_turns = self.primary_turns(self.input_voltage, self.flux_density, self.frequency, A_c)
        Number_of_primary_turns = round(Number_of_primary_turns)
        Turns_per_layer_primary = math.floor(self.turns_per_layer(wl, self.d_wp))
        Number_of_layers_primary = math.ceil(self.number_of_layers(Number_of_primary_turns, Turns_per_layer_primary))
        Built_primary = self.built_primary(Number_of_layers_primary, self.d_wp, self.bobbin_thickness)
        MTL_primary = self.mtl_primary(tongue, stack, self.bobbin_thickness, Built_primary)
        Length_primary = self.length(MTL_primary, Number_of_primary_turns)
        Primary_resistance = self.resistance(self.Resistivity_conductor, Length_primary, self.actual_a_wp)
        Primary_copper_loss = self.conductor_loss(self.input_Current, Primary_resistance)
        # ************************ Primary Wire ******************************** 

        # ************************ Secondary Wire ******************************
        Number_of_secondary_turns = self.secondary_turns(Number_of_primary_turns, self.output_voltage, self.regulation, self.input_voltage)
        Number_of_secondary_turns = round(Number_of_secondary_turns)
        Turns_per_layer_secondary = math.floor(self.turns_per_layer(wl, self.d_ws))
        Number_of_layers_secondary = math.ceil(self.number_of_layers(Number_of_secondary_turns, Turns_per_layer_secondary))
        Built_secondary = self.built_secondary(Number_of_layers_secondary, self.d_ws, self.insulation_thickness)
        MTL_secondary = self.mtl_secondary(tongue, stack, Built_primary, Built_secondary, self.bobbin_thickness)
        Length_secondary = self.length(MTL_secondary, Number_of_secondary_turns)
        Secondary_resistance = self.resistance(self.Resistivity_conductor, Length_secondary, self.actual_a_ws)
        Secondary_copper_loss = self.conductor_loss(self.secondary_current, Secondary_resistance)
        # ************************ Secondary Wire ******************************

        Weight_of_copper_kg = (Length_primary * self.required_swg_primary['Conductor Weight for 1000m/Kg'].max() + Length_secondary * self.required_swg_secondary['Conductor Weight for 1000m/Kg'].max() ) / 10**5  #kg
        Total_Built = self.total_built(Built_primary, Built_secondary)

        if (ww * 0.9 > Total_Built):

            Total_Cu_loss = self.total_copper_loss(Primary_copper_loss, Secondary_copper_loss)
            Core_loss_factor = self.core_loss_factor(self.frequency, self.flux_density) 
            volume_of_core = self.volume_of_core(stack, tongue, ww, wl)
            Density_of_core = 7.65 # g/cm^3
            weight_of_core = self.weight_of_core(Density_of_core, volume_of_core)
            weight_of_core_kg = weight_of_core / 1000  # kg
            core_loss = self.core_loss(Core_loss_factor, weight_of_core_kg) 
            total_loss = self.total_loss(Total_Cu_loss, core_loss)
            conductor_surface_area = self.conductor_surface_area(Total_Built, tongue, wl)  # cm2
            core_surface_area = self.core_surface_area(stack, tongue, wl, ww)  # cm2
            total_surface_area = self.total_surface_area(stack, tongue, wl, ww, Total_Built)  # cm2
            psi_copper = self.psi(Total_Cu_loss, conductor_surface_area)
            temperature_rise_copper = self.temperature_rise(psi_copper)
            psi_core = self.psi(core_loss, core_surface_area)
            temperature_rise_core = self.temperature_rise(psi_core)
            cost = self.cost(weight_of_core_kg, Weight_of_copper_kg, rate_copper=950, rate_fe=250)
            results_data = {
                'Area product': stack * tongue * wl * ww,
                'Stack mm': stack,
                'Tongue mm': tongue,
                'wl mm': wl,
                'ww mm': ww,
                'Cu surface area': conductor_surface_area,
                'Core surface area': core_surface_area,
                'Temperature rise Cu': temperature_rise_copper,
                'Temperature rise Fe': temperature_rise_core,
                'Cost': cost
            }
            return results_data
            # return cost 


    def built_calculation(self,stack, tongue, ww, wl):
        pass 
