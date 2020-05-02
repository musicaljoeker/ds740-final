import os
import pathlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
#import seaborn as sns

# Importing Tensorflow
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# tf version check
print(tf.__version__)

# getting the data into python
cols_to_keep = [
    "DAY_OF_MONTH",
    "DAY_OF_WEEK",
    "OP_CARRIER",
    "ORIGIN",
    "DEST",
    "DEP_DEL15",
    "DEP_TIME_BLK",
    "CANCELLED",
    "DIVERTED",
    "DISTANCE"
]
raw_jan19 = pd.read_csv("data/Jan_2019_ontime.csv")
print(raw_jan19[cols_to_keep].tail())
