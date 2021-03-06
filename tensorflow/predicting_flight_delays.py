# -*- coding: utf-8 -*-
"""Predicting Flight Delays.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1zrpRhNVXQRnX-7WSj9xU__xQP6AVIPUg

# The problem

In this notebook, I'll be trying to predict if a **flight will be delayed by 15 or more minutes** using data from the [January US Flight Data](https://www.kaggle.com/divyansh22/flight-delay-prediction/kernels). Given that this data is captured in the month of January 2019 and January 2020, it's reasonable to expect that this model may only accurately predict flights in January in the future. In addition, because I want to predict if a flight will be delayed by 15 or more minutes _before_ takeoff, I will not be using data that is captured after the takeoff happens (ex. delayed by 15 or more minutes, diverted, etc.)
"""

!pip install -q git+https://github.com/tensorflow/docs

import os
import pathlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

import tensorflow_docs as tfdocs
import tensorflow_docs.plots
import tensorflow_docs.modeling
from sklearn.model_selection import train_test_split

# tf version check
print(tf.__version__)

# setting the random seed
tf.random.set_seed(1000)

"""# Loading the Data"""

raw_jan19 = pd.read_csv("https://media.githubusercontent.com/media/musicaljoeker/ds740-final/master/data/Jan_2019_ontime.csv")
raw_jan20 = pd.read_csv("https://media.githubusercontent.com/media/musicaljoeker/ds740-final/master/data/Jan_2020_ontime.csv")
df = pd.concat([raw_jan19, raw_jan20], ignore_index=True)
df = df.drop(columns = 'Unnamed: 21') # unnecessary

# number of rows in the combined dataframe
nrows_org = df.shape[0]
nrows_org

"""# Cleaning the Data

Does this data have any missing values?
"""

df.isna().sum()

"""There are several rows with missing values, so let's clean that up and remove them."""

df = df.dropna()
nrows_rm_na = df.shape[0]
nrows_org - nrows_rm_na # let's see how many rows we lost

"""26100 rows removed is not bad. This leaves plenty (over 1 million rows) of complete data for us to work with.

Now let's remove the columns from the dataset that don't provide much value to our purposes.
"""

cols_to_keep = [
    "DAY_OF_WEEK",
    "OP_CARRIER",
    "ORIGIN",
    "DEP_DEL15",
    "DEP_TIME_BLK",
    "DISTANCE"
]
df = df[cols_to_keep]

"""# Exploring our data

We want to look for some hints on which variables are important.

### Worst Delayed Airports

Let's see which airports have the worst ratio of flight delays to total flights.
"""

delays = df[df["DEP_DEL15"]==1]["ORIGIN"].value_counts()
total = df["ORIGIN"].value_counts()
proportion = (delays / total).sort_values(ascending = False)
ax = proportion.head(10).plot.barh()
ax.set(ylabel='Airports', xlabel='Proportion of Delayed Flights', title="Top 10 Most Likely Delayed Airports")

"""Now let's see which airports have the most delays overall."""

ax = delays.head(10).plot.barh()
ax.set(ylabel='Airports', xlabel='Count of Delayed Flights', title="Top 10 Most Delayed Airports")

"""It's not much of a surprise that these busy airports have lots of delays. Lots of flights mean a higher quantity of delays. Still, it does seem that ORD (Chicago O'Hare) has more delays than usual for it's busy counter-airports.

### Time of Day for Delays

Let's see if time of day has any association with delayed flights.
"""

ax = sns.barplot(x="DEP_DEL15", y="DEP_TIME_BLK", data=df.sort_values('DEP_TIME_BLK'))
ax.set(ylabel='Time Block', xlabel='Proportion of Delayed Flights', title="Delayed Flights by Time of Day")

"""It seems that flights are less likely to be delayed in the morning and more likely to be delayed into the afternoon and peaking in the early evening. Because flights in the afternoon are using airplanes that have already flown once or twice earlier in the day, this graph makes sense. The risk of a flight delay increases with each previous flight during the day.

# Preparing for Training

Now we'll prepare our data one last time before training the model.

Let's split the data into train, test, and validation sets.
"""

train, val = train_test_split(df, test_size=0.2)
print(len(train), 'train examples')
print(len(val), 'validation examples')

"""Now, we'll convert the pandas dataset into a dataset that tensorflow can use. This allows us to use feature columns."""

# A utility method to create a tf.data dataset from a Pandas Dataframe
def df_to_dataset(dataframe, shuffle=True, batch_size=32):
    dataframe = dataframe.copy()
    labels = dataframe.pop('DEP_DEL15')
    ds = tf.data.Dataset.from_tensor_slices((dict(dataframe), labels))
    if shuffle:
        ds = ds.shuffle(buffer_size=len(dataframe))
    ds = ds.batch(batch_size)
    return ds

batch_size = 5 # A small batch sized is used for demonstration purposes

train_ds = df_to_dataset(train, batch_size=batch_size)
val_ds = df_to_dataset(val, shuffle=False, batch_size=batch_size)

"""# Understand the Input

Let's the check the format of the data in the input pipeline.
"""

for feature_batch, label_batch in train_ds.take(1):
    print('Every feature:', list(feature_batch.keys()))
    print('A batch of origins:', feature_batch['ORIGIN'])
    print('A batch of delayed flights:', label_batch )

"""Now we'll construct feature columns that we'll use to pass into the model-building process. We'll also build a feature layer.

To do this, we'll use `DISTANCE` as a numerical tensor and the others set to [one-hot](https://en.wikipedia.org/wiki/One-hot) categorical tensors.
"""

feature_columns = []

# adding numeric columns
distance = tf.feature_column.numeric_column("DISTANCE")
feature_columns.append(distance)

# adding categorical columns
origin = tf.feature_column.categorical_column_with_vocabulary_list(
      "ORIGIN", pd.unique(df.ORIGIN))
origin_one_hot = tf.feature_column.indicator_column(origin)
feature_columns.append(origin_one_hot)

carrier = tf.feature_column.categorical_column_with_vocabulary_list(
      "OP_CARRIER", pd.unique(df.OP_CARRIER))
carrier_one_hot = tf.feature_column.indicator_column(carrier)
feature_columns.append(carrier_one_hot)

time_blk = tf.feature_column.categorical_column_with_vocabulary_list(
      "DEP_TIME_BLK", pd.unique(df.DEP_TIME_BLK))
time_blk_one_hot = tf.feature_column.indicator_column(time_blk)
feature_columns.append(time_blk_one_hot)

day_of_week = tf.feature_column.categorical_column_with_vocabulary_list(
      "DAY_OF_WEEK", pd.unique(df.DAY_OF_WEEK))
day_of_week_one_hot = tf.feature_column.indicator_column(day_of_week)
feature_columns.append(day_of_week_one_hot)

feature_layer = tf.keras.layers.DenseFeatures(feature_columns)

"""Now, we'll set our batch size and prepare our datasets."""

batch_size = 32
train_ds = df_to_dataset(train, batch_size=batch_size)
val_ds = df_to_dataset(val, shuffle=False, batch_size=batch_size)

"""# Train the Model

We'll train the Neural Network model with two densely connected hidden layers of 16 nodes using the Rectified Linear Unit activation function and Binary Cross-Entropy loss function (because we are issuing a single probability as our output node) with the Adam optimizer.

These settings were found with some trial and error and produced the best accuracy.
"""

model = tf.keras.Sequential([
    feature_layer,
    layers.Dense(16, activation='relu'),
    layers.Dense(16, activation='relu'),
    layers.Dense(1)
])

model.compile(optimizer='adam',
    loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
    metrics=['accuracy'])

model.fit(train_ds,
    validation_data=val_ds,
    epochs=5)

"""As you can see, we've achieved a validation accuracy of ~84% for the model. I believe the accuracy in predicting if the flight will be delayed by 15 or more minutes could be improved if we obtained additional information regarding flight operations. Some other data points that would be useful could be "average length of flight operations issue resolution.""""
