# imports for training
import pytorch_lightning as pl
from pytorch_lightning.loggers import TensorBoardLogger
from pytorch_lightning.callbacks import EarlyStopping, LearningRateMonitor
# import dataset, network to train and metric to optimize
from pytorch_forecasting import TimeSeriesDataSet, TemporalFusionTransformer, QuantileLoss

import pandas as pd

print("Importing")
df = pd.read_csv("BTC_ETH_SOL_XRP_DOGE_APE_2021_2022_1M.csv")

btc = df.loc[df['symbol'].str.contains("BTC")]
btc = pd.Series(btc.close_mid_price)
btc = btc.to_frame("value")

