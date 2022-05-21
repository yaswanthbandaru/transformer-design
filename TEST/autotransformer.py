# libraries for class
import pandas as pd
import numpy as np
import math


class AT:
    """
    AT - AutoTransformer
    """
    pi = np.pi
    k_f = 4.44
    k_u = 0.4
    # lamination data and swg data
    lamination_data = pd.read_csv(
        "https://raw.githubusercontent.com/yaswanthbandaru/transformer-design/main/DATA/EI-Laminations.csv")
    swg_data = pd.read_csv(
        "https://raw.githubusercontent.com/yaswanthbandaru/transformer-design/main/DATA/EMD%20-%20Sheet1.csv")

    def __init__(self, frequency,
                 temperature,
                 outputpower,
                 regulation,
                 inputvoltage,
                 outputvoltage,
                 currentdensity,
                 b_ac):
        self.frequency = frequency
        self.temperature = temperature
        self.outputpower = outputpower
        self.regulation = regulation
        self.inputvoltage = inputvoltage
        self.outputvoltage = outputvoltage
        self.J = currentdensity
        self.b_ac = b_ac

    # def apparent_power(self, outputpower, efficiency):
    #     apparent_power = outputpower
    #     pass

    @staticmethod
    def apparent_power(self):
        pass

    @staticmethod
    def area_product(apparent_power, b_ac, currentdensity, frequency, k_f, k_u):
        """
        Area Product = P * 10^4 / ( K_f * K_u * B_ac * J * frequency)

        Output Power [watts], Efficiency in percentage, K_f, K_u, Operational flux density B_ac,
        Current density J, Frequency [Hz], Apparent power [watts],
        """
        area_product = (apparent_power*(10**4) / (k_f * k_u * b_ac * currentdensity * frequency))
        return area_product

    def bare_area(self):
        pass

    def find_swg(self):
        pass

    def calculate_stack(self):
        pass

    def rounding_stack_as_multiple_of_five(self):
        pass

    def conductor_loss(self):
        pass

    def core_loss(self):
        pass

    def core_area(self):
        pass

    def primary_turns(self):
        pass

    def secondary_turns(self):
        pass

    def turns_per_layer(self):
        pass

    def number_of_layers(self):
        pass

    def built_primary(self):
        pass

    def built_secondary(self):
        pass

    def total_built(self):
        pass

    def mtl_primary(self):
        pass

    def mtl_secondary(self):
        pass

    def length(self):
        pass

    def resistance(self):
        pass

    def total_copper_loss(self):
        pass

    def volume_of_core(self):
        pass

    def weight_of_core(self):
        pass

    def core_loss_factor(self):
        pass

    def core_loss(self):
        pass

    def total_loss(self):
        pass

    def conductor_surface_area(self):
        pass

    def core_surface_area(self):
        pass

    def psi(self):
        pass

    def temperature_rise(self):
        pass

    def leakage_inductance(self):
        pass
