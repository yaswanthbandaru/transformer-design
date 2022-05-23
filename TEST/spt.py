import pandas as pd
import numpy as np

from autotransformer import *

# Define the constructor
spt = AutoTransformer()

# Inputs for the function
frequency = 47  # Hz
temperature_rise_goal = 30  # celcius
output_power = 250  # watts
input_voltage = 115  # volts
output_voltage = 115  # volts
efficiency = 95  # %
regulation = 5
b_ac = 1.6  # flux density
current_density = 250  # amp/cm2
bobbin_thickness = 1.5  # mm
insulation_thickness = 0.2  # mm
Resistivity_conductor = 1.68 * 10**-6 # ohm cm

# from auto transformer
k_f = spt.k_f
k_u = spt.k_u
lamination_data = spt.lamination_data
swg_data = spt.swg_data

# calculate the apparent power
apparent_power = spt.apparent_power(output_power, efficiency)
# area product
area_product = spt.area_product(apparent_power,b_ac, current_density,frequency, k_f, k_u)

##############################################################
#                       Primary wire
# calculate the input current
input_current = output_power / input_voltage
# bare area in mm2
a_wp = spt.bare_area(input_current, current_density)
# for primary wire
required_swg_primary, diameter_of_primary_wire, actual_a_wp = spt.find_swg(a_wp)

d_wp = diameter_of_primary_wire


##############################################################
#                     Secondary Wire
# calculate secondary current
secondary_current = output_power / output_voltage
# bare area secondary in mm2
a_ws = spt.bare_area(secondary_current, current_density)
# for secondary wire
required_swg_secondary, diameter_of_secondary_wire, actual_a_ws = spt.find_swg(a_ws)

d_ws = diameter_of_secondary_wire
