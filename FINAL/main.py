# import libraries
from decimal import ROUND_DOWN, ROUND_UP
from tkinter import *
import tkinter as tk 
import pandas as pd
import numpy as np
import math 

# Data
lamination_data = pd.read_csv("https://raw.githubusercontent.com/yaswanthbandaru/transformer-design/main/DATA/EI-Laminations.csv")
swg_data = pd.read_csv("https://raw.githubusercontent.com/yaswanthbandaru/transformer-design/main/DATA/EMD%20-%20Sheet1.csv")




# GUI part

app = tk.Tk()
app.title("Single Phase Transformer")


app.mainloop()