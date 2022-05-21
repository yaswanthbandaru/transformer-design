import pandas as pd
import numpy as np

from autotransformer import *

spt = AT(47, 30, 250, 5, 115, 115, 250, 1.6)

Apparent_power = spt.apparent_power(95)
Area_product = spt.area_product(Apparent_power, spt.k_f, spt.k_u)




