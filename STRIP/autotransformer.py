# libraries for class
import pandas as pd
import numpy as np
import math


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
    strip_data = pd.read_csv("https://raw.githubusercontent.com/yaswanthbandaru/transformer-design/main/DATA/Strip_Wires_Combinations.csv")

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
        ## changing the higher data.iloc to swg_data.iloc for nearest one in the below line 
        required_swg = swg_data.iloc[(swg_data['Normal Conductor Area mm²'] - Bare_area).abs().argsort()[:1]]
        diameter_of_insulated_wire = required_swg['Medium Covering Max']
        a_wp = required_swg['Normal Conductor Area mm²'].max() / 100  # cm^2
        return required_swg, diameter_of_insulated_wire.max(), a_wp 

    def find_strip_lamination(self, Bare_area):
        strip_data = self.strip_data
        required_strip = strip_data.iloc[(strip_data['Normal Conductor Area mm² \t'] - Bare_area).abs().argsort()[:1]]
        a_wp = required_strip['Normal Conductor Area mm² \t'].max() / 100 # sqcm
        height = required_strip['height'].max()
        width = required_strip['weight'].max() 
        return required_strip, a_wp, height, width

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
    def turns_per_layer_strip(winding_length, width):
        return winding_length / width

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
    def built_primary_strip(number_of_layers_primary, height_primary, insulation_thickness):
        return number_of_layers_primary * height_primary + insulation_thickness * number_of_layers_primary

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
    def built_secondary_strip(number_of_layers_secondary,
                        height_secondary,
                        insulation_thickness):
        return insulation_thickness + number_of_layers_secondary * height_secondary + insulation_thickness * number_of_layers_secondary

    @staticmethod
    def total_built(built_primary, built_secondary, bobbin_thickness):
        """

        :param built_primary:
        :param built_secondary:
        :return: built_primary + built_secondary
        """
        return built_primary + built_secondary + bobbin_thickness

    @staticmethod
    def mtl_primary(tongue, stack, bobbin_thickness, built_primary):
        return 2 * (tongue + stack + 2 * built_primary + 2 * bobbin_thickness) / 10  # cm

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
        return 2 * (tongue + stack + 2 * built_primary + 2 * built_secondary + 2 * bobbin_thickness) / 10  # cm

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
        return 0.000557 * frequency**self.a * b_ac**self.b

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
    def conductor_surface_area(stack , total_built, tongue, winding_length):
        """
        Cu_surface_area = pi * Total_Built * wl + (pi/2)* Total_Built**2 - (pi/2)* tongue**2
        returns in sqcms
        """
        # pi = self.pi
        # surface_area = pi * total_built * winding_length + (pi / 2) * (total_built ** 2 - tongue ** 2)
        surface_area = 2 * winding_length * (tongue + stack + 4 * total_built)
        return surface_area / 100 # sqcm

    @staticmethod
    def core_surface_area(stack, tongue, winding_length, widning_width):
        """
        To calculate core surface area we need 'stack', 'total built',
        'tongue', 'wl', 'ww'.
        
        Core_surface_area = 2 * ( (B * C - 2 * ww * wl) + stack * (B+C) )

        A = tongue
        B = 2 * ( tongue + winding_width)
        C = winding length + tongue 

        returns in sqcm
        """
        t = tongue 
        wl = winding_length
        ww = widning_width
        B = 2 * (t + ww)
        C = wl + t 
        area = 2 * ( (B * C - 2 * ww * wl) + stack * (B+C) )
        return area / 100 # cm2
    
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
        # area product 
        self.area_product = self.area_product(self.apparent_power, self.flux_density, self.current_density, self.frequency, self.k_f, self.k_u)
        ################# primary wire #############################
        # calculate the input current
        self.input_Current = self.output_power / self.input_voltage
        # bare area in mm2
        self.a_wp = self.bare_area(self.input_Current, self.current_density)
        if self.a_wp <= 850:    
            # for primary wire
            self.required_swg_primary, self.diameter_of_primary_wire, self.actual_a_wp = self.find_swg(self.a_wp)
            self.d_wp = self.diameter_of_primary_wire
        ################## secondary wire ###########################
        # calculate secondary current
        self.secondary_current = self.output_power / self.output_voltage
        # bare area secondary in mm2
        self.a_ws = self.bare_area(self.secondary_current, self.current_density)
        if self.a_ws <= 850:
            # for secondary wire
            self.required_swg_secondary, self.diameter_of_secondary_wire, self.actual_a_ws = self.find_swg(self.a_ws)
            self.d_ws = self.diameter_of_secondary_wire

        ###########checking outputs
        print(f'Apparent power : {self.apparent_power}')
        print(f'Area product : {self.area_product}')
        print(f'Input current : {self.input_Current}')
        print(f'a_wp : {self.a_wp}')
        print(f'actual a_wp: {self.actual_a_wp}')
        print(f'a_ws : {self.a_ws}')
        print(f'actual a_ws : {self.actual_a_ws}')
        print(f'primary swg : swg \n {self.required_swg_primary}')
        print(f'secondary swg : swg \n {self.required_swg_secondary}')


    def total_cost(self, stack, tongue, winding_width, winding_length):
        """
        params: stack, tongue, winding_length, winding_length
        
        we are not using stack vs tongue condition in this method
        """
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

    def total_cost_strip(self, stack, tongue, winding_lenth, winding_width):
        pass 
