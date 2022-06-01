# libraries for class
import pandas as pd
import numpy as np
# import math


class AutoTransformer:
    """
    AT - AutoTransformer
    """
    pi = np.pi
    a = 1.68  # coefficients for core loss
    b = 1.86  # coefficients for core loss
    k_f = 4.44
    k_u = 0.4
    # lamination data and swg data
    lamination_data = pd.read_csv(
        "https://raw.githubusercontent.com/yaswanthbandaru/transformer-design/main/DATA/EI-Laminations.csv")
    swg_data = pd.read_csv(
        "https://raw.githubusercontent.com/yaswanthbandaru/transformer-design/main/DATA/EMD%20-%20Sheet1.csv")

    """
    ===================================================================================================
                                           Methods of AutoTransformer
    
    => apparent_power
    => area_product
    => bare_area
    => input_current
    => bare_area
    => find_swg
    => calculate_stack
    => rounding_stack_as_multiple_of_five
    => conductor_loss
    => core_area
    => primary_turns
    => secondary_turns
    => turns_per_layer
    => number_of_layers
    => built_primary
    => built_secondary
    => total_built
    => mtl_primary
    => mtl_secondary
    => length
    => resistance
    => total_copper_loss
    => volume_of_core
    => weight_of_core
    => core_loss_factor
    => core_loss
    => total_loss
    => conductor_surface_area
    => core_surface_area
    => total_surface_area
    => psi
    => temperature_rise
    => leakage_inductance
    => cost
    =======================================================================================================
    """

    @staticmethod
    def apparent_power(outputpower, efficiency):
        return outputpower * (1 / (0.01 * efficiency) + 1)

    @staticmethod
    def area_product(apparent_power, b_ac, currentdensity, frequency, k_f, k_u):
        """
        Area Product = P * 10^4 / ( K_f * K_u * B_ac * J * frequency)

        Output Power [watts], Efficiency in percentage, K_f, K_u, Operational flux density B_ac,
        Current density J, Frequency [Hz], Apparent power [watts],
        """
        area_product = (apparent_power * (10 ** 4) / (k_f * k_u * b_ac * currentdensity * frequency))
        return area_product

    @staticmethod
    def input_current(outputpower, inputvoltage):
        """"""
        return outputpower / inputvoltage

    @staticmethod
    def bare_area(inputcurrent, currentdensity):
        """

        :param inputcurrent: amp
        :param currentdensity: amp/cm^2
        :return bare area: mm^2
        """
        a_wp = inputcurrent / currentdensity
        return a_wp * 100

    def find_swg(self, Bare_area):
        swg_data = self.swg_data
        higher_data = swg_data[Bare_area < swg_data['Normal Conductor Area mm²']]
        required_swg = higher_data.iloc[(higher_data['Normal Conductor Area mm²'] - Bare_area).abs().argsort()[:1]]
        diameter_of_insulated_wire = required_swg['Medium Covering Max']
        a_wp = required_swg['Normal Conductor Area mm²'].max() / 100  # cm^2
        return required_swg, diameter_of_insulated_wire.max(), a_wp

    @staticmethod
    def calculate_stack(area_product, k_ratio):
        stack_in_cm = area_product * 1000 / k_ratio
        return stack_in_cm * 10

    @staticmethod
    def rounding_stack_as_multiple_of_five(stack):
        # for approximating for stack
        if stack < 5:
            stack = 5.0
        elif stack % 5 == 0:
            stack = stack
        elif stack % 5 <= 2.5:
            stack = stack - stack % 5
        elif stack % 5 > 2.5:
            stack = stack - stack % 5 + 5
        return stack

    @staticmethod
    def conductor_loss(current, resistance):
        """
        It can be applied to Secondary and Primary wires 
        with their respective resistances -> 'priamry' &
        'secondary'

        :param current:
        :param primary_resistance:
        :return: current**2 * resistance
        """
        return current ** 2 * resistance

    @staticmethod
    def core_area(stack, tongue):
        """

        :param stack: mm
        :param tongue: mm
        :return: stack * tongue  cm^2
        """
        return stack * tongue / 100

    def primary_turns(self, Input_voltage, flux_density, frequency, core_area):
        """
            Calculate number of primary turns
            Np = (Input_voltage* 10**4) / (K_f * B_ac * Frequency * A_c)
        """
        return (Input_voltage * 10 ** 4) / (self.k_f * flux_density * frequency * core_area)

    @staticmethod
    def secondary_turns(primary_turns, output_voltage, regulation, input_voltage):
        """
        Ns = Np * Ouptut_voltage * (1 + Regulation / 100) / Input_voltage
        Ns - secondary turns
        :return:
        """
        return primary_turns * output_voltage * (1 + regulation / 100) / input_voltage

    @staticmethod
    def turns_per_layer(winding_length, diameter):
        """
          Turns_per_layer_primary = wl / dw_p
          Turns_per_layer_secondary = wl / diameter_of_wire_secondary_insulated
        """
        return winding_length / diameter

    @staticmethod
    def number_of_layers(number_of_turns, turns_per_layer):
        """
        Number_of_layer_primary = Np / Turns_per_layer_primary
        Number_of_layer_secondary = Ns /  Turns_per_layer_secondary

        :param number_of_turns:
        :param turns_per_layer:
        :return:
        """
        return number_of_turns / turns_per_layer

    @staticmethod
    def built_primary(number_of_layers_primary, diameter_of_primary_wire, bobbin_thickness):
        """

        :param number_of_layers_primary:
        :param diameter_of_primary_wire:
        :param bobbin_thickness:
        :return: bobbin_thickness + number_of_layers_primary * diameter_of_primary_wire
        """
        return bobbin_thickness + number_of_layers_primary * diameter_of_primary_wire

    @staticmethod
    def built_secondary(number_of_layers_secondary,
                        diameter_of_secondary_wire,
                        insulation_thickness):
        """

        :param number_of_layers_secondary:
        :param diameter_of_secondary_wire:
        :param insulation_thickness:
        :return: insulation_thickness + number_of_layers_secondary * diameter_of_secondary_wire
        """
        return insulation_thickness + number_of_layers_secondary * diameter_of_secondary_wire

    @staticmethod
    def total_built(built_primary, built_secondary):
        """

        :param built_primary:
        :param built_secondary:
        :return: built_primary + built_secondary
        """
        return built_primary + built_secondary

    @staticmethod
    def mtl_primary(tongue, stack, bobbin_thickness, built_primary):
        return 2 * (tongue + stack + 2 * built_primary + 4 * bobbin_thickness) / 10  # cm

    @staticmethod
    def mtl_secondary(tongue,
                      stack,
                      built_primary,
                      built_secondary,
                      bobbin_thickness):
        """

        :param tongue:
        :param stack:
        :param built_primary:
        :param built_secondary:
        :param bobbin_thickness:
        :return: cm
        """
        return 2 * (tongue + stack + 4 * built_primary + 2 * built_secondary + 4 * bobbin_thickness) / 10  # cm

    @staticmethod
    def length(mtl, number_of_turns):
        """

        :param mtl:
        :param number_of_turns:
        :return: cm
        """
        return mtl * number_of_turns

    # @staticmethod
    # def weight_of_copper_kg(
    #     length_primary,
    #     weight_rate_of_primary_swg,
    #     length_scondary,
    #     weight_rate_of_secondary_swg,
    #     ):
    #     weight_primary = length_primary * weight_rate_of_primary_swg 
    #     weight_secondary = length_scondary  + weight_rate_of_secondary_swg
    #     return (weight_primary + weight_secondary) / 10**5 

    @staticmethod
    def resistance(resistivity, length, bare_area):
        """
        For calculating the primary resistance and secondary resistance we are
        going to use this method. In this method resistivity is same for both
        primary and secondary. However, the length and bare are of primary and
        secondary differs.

        :param resistivity:
        :param length:
        :param bare_area:
        :return:
        """
        return resistivity * length / bare_area

    @staticmethod
    def total_copper_loss(primary_copper_loss, secondary_copper_loss):
        return primary_copper_loss + secondary_copper_loss

    @staticmethod
    def volume_of_core(stack, tongue, winding_width, winding_length):
        """
        B = 2 * (t + ww)
        C = wl + t
        """
        ww = winding_width
        wl = winding_length
        B = 2 * (tongue + ww)
        C = wl + tongue 
        volume = stack * ( B * C - 2 * ww * wl )  # mm3
        volume = volume / 1000  # cm3
        return volume 

    @staticmethod
    def weight_of_core(density_of_core, volume_of_core_cm3):
        weight_gm = density_of_core * volume_of_core_cm3 * 0.97  # staking factor
        return weight_gm

    def core_loss_factor(self, frequency, flux_density):
        """

        :param frequency:
        :param flux_density:
        :return: core_loss_factor
        """
        b_ac = flux_density
        return 0.000557 * frequency ** self.a * b_ac ** self.b

    @staticmethod
    def core_loss(core_loss_factor, weight_of_core_in_kg):
        """

        :param core_loss_factor: constant
        :param weight_of_core_in_kg: kg
        :return:
        """
        return core_loss_factor * weight_of_core_in_kg

    @staticmethod
    def total_loss(total_copper_loss, core_loss):
        """

        :param total_copper_loss:
        :param core_loss:
        :return: total_loss
        """
        return total_copper_loss + core_loss

    @staticmethod
    def conductor_surface_area(total_built, tongue, winding_length):
        """
        Cu_surface_area = pi * Total_Built * wl + (pi/2)* Total_Built**2 - (pi/2)* tongue**2

        """
        # pi = self.pi
        # surface_area = pi * total_built * winding_length + (pi / 2) * (total_built ** 2 - tongue ** 2)
        surface_area = 2 * winding_length * (tongue + 4 * total_built)
        return surface_area

    @staticmethod
    def core_surface_area(stack, tongue, winding_length, widning_width):
        """
        To calculate core surface area we need 'stack', 'total built',
        'tongue', 'wl', 'ww'.
        
        Core_surface_area = 2 * ( (B * C - 2 * ww * wl) + stack * (B+C) )

        A = tongue
        B = 2 * ( tongue + winding_width)
        C = winding length + tongue
        """
        t = tongue 
        wl = winding_length
        ww = widning_width
        B = 2 * (t + wl)
        C = wl + t 
        area = 2 * ( (B * C - 2 * ww * wl) + stack * (B+C) )
        return area 
    
    @staticmethod
    def total_surface_area(stack, tongue, winding_length, winding_width, total_built):
        """
        Total_surface_area = 2 * ( B * C + B * (stack + 2 * Total_Built) + C * (stack + 2 * Total_Built) ) / 100 #cm2

        A = tongue
        B = 2 * (tongue + winding_width)
        C = winding_length + tongue
        """
        t = tongue 
        B = 2 * (t + winding_width)
        C = winding_length + t 
        area = 2 * (B * C + B * (stack + 2 * total_built) + C * (stack + 2 * total_built)) / 100  # cm2
        return area  # cm2
    
    @staticmethod
    def psi(loss, surface_area):
        """
        loss -> total cu loss for pis copper & core_loss for psi core
        psi copper <- cu surface area & total cu loss
        psi core <- core surface area & core loss
        """
        psi = loss / surface_area
        return psi 

    @staticmethod
    def temperature_rise(psi):
        """
        Respective psi's are to used for the calculation of temperature rise 
        psi copper -> temperature rise in cu
        psi core   -> temperature rise in core
        """
        temperature = 450 * psi**0.826
        return temperature 

    def leakage_inductance(self):
        pass

    @staticmethod
    def cost(weight_core_kg, weight_copper_kg, rate_copper, rate_fe):
        return weight_copper_kg*rate_copper + weight_core_kg*rate_fe





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
