import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

social = pd.read_csv("Aggregated_reddit_twitter.csv")
social = social.rename(columns={"date": "timestamp"})
social["timestamp"] = pd.to_datetime(social["timestamp"])

social = social[social.content != "u/circular360"]
social = social[social.content != "There you go"]
social = social[
    social.content != "Why force the other player to stay around? Just give the winning player the option to continue the game with a perma passing AI controlling the surrendering player."]
# crypto = pd.read_csv("transformed_crypto.csv")
# crypto["timestamp"] = pd.to_datetime(crypto["timestamp"]).dt.tz_localize(None)
crypto = pd.read_csv("crypto_differences.csv")
crypto["timestamp"] = pd.to_datetime(crypto["timestamp"]).dt.tz_localize(None)

social = social.sort_values(by="timestamp")
# social.dtypes
sr = social.resample("T", on="timestamp").size()
freq = sr.reset_index()

freq = freq.rename(columns={0: "n_comments"})

freq["hour"] = freq["timestamp"].dt.hour
freq["day"] = freq["timestamp"].dt.dayofweek
freq["month"] = freq["timestamp"].dt.month
freq

mg = pd.merge(crypto, freq, on="timestamp", how="inner")

import torch
import torch.nn as nn
from torch.utils.data import Dataset

shortmg = mg.loc[0:20000]
shortmg.dropna()


class TimeSeriesDataset(Dataset):
    def __init__(self, X_data, y_data):
        self.X_data = X_data
        self.y_data = y_data

    def __getitem__(self, index):
        return self.X_data[index], self.y_data[index]

    def __len__(self):
        return len(self.X_data)


class MyTimeSeriesDataset(Dataset):
    def __init__(self, X_data, y_data):
        self.X_data = X_data
        self.y_data = y_data

    def __getitem__(self, index):
        return self.X_data.loc[index], self.y_data[index]

    def __len__(self):
        return len(self.X_data)

# data = MyTimeSeriesDataset(X_data=shortmg[['n_comments', 'XRP-PERP', 'ETH-PERP']], y_data=shortmg['BTC-PERP'])


# Load your dataset into a pandas DataFrame called 'data'
from sklearn.preprocessing import MinMaxScaler, StandardScaler

# Scale the features using MinMaxScaler
cs = ['BTC-PERP', 'XRP-PERP', 'ETH-PERP', 'SOL-PERP', 'DOGE-PERP']
scaled_data = shortmg[cs + ["hour", "day", "month", "n_comments"]]
# scaled_data = shortmg[['XRP-PERP', 'ETH-PERP', 'BTC-PERP', 'SOL-PERP', 'DOGE-PERP', 'n_comments']].to_numpy()

# scaled_data = abs(scaled_data)


# scaled_data = scaled_data.to_numpy()
#
scaler = StandardScaler()
#
scaled_data = scaled_data.to_numpy()
# scaled_data = scaler.fit_transform(scaled_data)


# Create sequences and targets for the RNN model
seq_length = 60
X_data = []
y_data = []

future = 5

for i in range(len(scaled_data) - seq_length - future):
    X_data.append(scaled_data[i:i + seq_length].flatten())
    y_data.append(scaled_data[i + seq_length + future])

x_data = scaler.fit_transform(X_data)
# y_data = np.delete(y_data, [-1, -2, -3, -4], axis=1)
y_data = np.delete(y_data, [-1, -2, -3, -4, -5, -6, -7, -8], axis=1)
# to make classifier
epsilon = 0.002


def f(x):
    if x > epsilon:
        return 1
    elif x < -epsilon:
        return 2
    else:
        return 0


[0, 0, 1]
[0, 1, 0]
[1, 0, 0]
y_data = list(map(f, y_data))

print(y_data[1:10])
X_data, y_data = np.array(X_data), np.array(y_data)

y_data = y_data.astype(np.int64)

train_size = int(len(X_data) * 0.8)
X_train, X_test = X_data[:train_size], X_data[train_size:]
y_train, y_test = y_data[:train_size], y_data[train_size:]