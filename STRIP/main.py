# %%
# import libraries
from decimal import ROUND_DOWN, ROUND_UP
from tkinter import *
import tkinter as tk 
import pandas as pd
import numpy as np
import math 
from strip_test import *

# %%
# Data
lamination_data = pd.read_csv("https://raw.githubusercontent.com/yaswanthbandaru/transformer-design/main/DATA/EI-Laminations.csv")
swg_data = pd.read_csv("https://raw.githubusercontent.com/yaswanthbandaru/transformer-design/main/DATA/EMD%20-%20Sheet1.csv")

# program

# %%
# Initial variables for the calculation and validation
Frequency = 47 # Hz
Temperature_rise_goal = 30 # degree Celcius
Output_power = 250 # watts
Efficiency = 95 # %
Input_voltage = 115 # volts
Ouptut_voltage = 115 # volts
Regulation = 5 # in a scale of 100
Bobbin_thickness = 1.5 
K_f = 4.44
K_u = 0.4
B_ac = 1.6
J = 235
insulation_thickness = 0.2 #mm

pi = np.pi #pi
a = 1.68 # coefficients for core loss
b = 1.86 # coefficients for core loss 
Rate_of_Cu = 950 # Rs / Kg
Rate_of_Fe = 250 # Rs / Kg
Resistivity_Cu =  1.68 * 10**-6 # ohm cm

# %%
# strip = Strip(
#     frequency= Frequency,
#     input_voltage= Input_voltage,
#     output_voltage= Ouptut_voltage,
#     output_power= Output_power,
#     efficiency= Efficiency,
#     regulation= Regulation,
#     flux_density= B_ac,
#     current_density= J
#     )
# # %%

# %%
from autotransformer import *

spt = AutoTransformer()
# %%
Apparent_power = spt.apparent_power(Output_power, Efficiency)
Area_product = spt.area_product(Apparent_power, B_ac, J, Frequency, spt.k_f, spt.k_u)
print(Apparent_power)
# %%

