import pandas as pd

stock = pd.read_csv("data/raw/dirty_stock_daily_ohlcv.csv")
stock.head()
expected_columns={"ticker","date","open","close","high","low","volume"}
actual_columns = set(stock.columns)
unexpected_columns = actual_columns-expected_columns
missing_columns = expected_columns-actual_columns