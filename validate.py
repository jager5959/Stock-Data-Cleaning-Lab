import pandas as pd

def check_required_columns(df:pd.DataFrame) -> None:
    if not isinstance(df,pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame.")
    required_columns={"ticker","date","open","high","low","close","volume"}
    missing_columns = required_columns-set(df.columns)
    if(missing_columns):
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )
    
def drop_invalid_dates(df:pd.DataFrame) -> pd.DataFrame:
    dates = pd.read_csv("./data/useful/2025_US_Stock_Market_Trading_Days.csv")
    expected_dates = set(dates["Date"])
    invaild_rows=[]
    for i in range(0,len(df)):
        if df.loc[i]["date"] not in expected_dates:
            invaild_rows.append(i)
    df.drop(index=invaild_rows,inplace=True)
    df.reset_index(drop=True,inplace=True)
    return df

def drop_missing_values(df:pd.DataFrame) -> pd.DataFrame:
    missing_mask = df.isna().any(axis=1)
    missing_rows=[]
    for i in range(0,len(missing_mask)):
        if missing_mask.loc[i] == True:
            missing_rows.append(i)
    df.drop(index=missing_rows,inplace=True)
    df.reset_index(drop=True,inplace=True)
    return df

def drop_and_mark_duplicate_rows(df:pd.DataFrame) -> pd.DataFrame:
    completely_duplicate_mask = df.duplicated(subset=["ticker","date","open","high","low","close","volume"],keep="first",)
    completely_duplicate_rows=[]
    for i in range(0,len(completely_duplicate_mask)):
        if completely_duplicate_mask.loc[i] == True:
            completely_duplicate_rows.append(i)
            # print(i)
    df.drop(index=completely_duplicate_rows,inplace=True)
    df.reset_index(drop=True,inplace=True)
    controversial_mask = df.duplicated(subset=["ticker","date"],keep=False,)
    for i in range(0,len(controversial_mask)):
        if controversial_mask.loc[i] == True:
            df.loc[i,"warning"]="controversial"
    return df

def drop_non_positive_prices(df:pd.DataFrame) -> pd.DataFrame:
    non_positive_rows=[]
    for i in range(0,len(df)):
        if (df.loc[i]["open"]<=0) | (df.loc[i]["close"]<=0) | (df.loc[i]["high"]<=0) | (df.loc[i]["low"]<=0):
            non_positive_rows.append(i)
    df.drop(index=non_positive_rows,inplace=True)
    df.reset_index(drop=True,inplace=True)
    return df

def drop_negative_volume(df:pd.DataFrame) -> pd.DataFrame:
    negative_rows=[]
    for i in range(0,len(df)):
        if df.loc[i]["volume"]<0:
            negative_rows.append(i)
    df.drop(index=negative_rows,inplace=True)
    df.reset_index(drop=True,inplace=True)
    return df

def check_ohlc_relationships(df:pd.DataFrame) -> pd.DataFrame:
    weird_marks = (df["close"]>df["high"]) | (df["close"]<df["low"]) | (df["open"]>df["high"]) | (df["open"]<df["low"])
    weird_rows=[]
    for i in range(0,len(weird_marks)):
        if weird_marks.loc[i] == True:
            weird_rows.append(i)
    df.drop(index=weird_rows,inplace=True)
    df.reset_index(drop=True,inplace=True)
    return df

def mark_suspicious_price_jumps(df:pd.DataFrame, threshold=0.30)->pd.DataFrame:
    df=df.sort_values(["ticker","date"])
    df.reset_index(drop=True,inplace=True)  
    daily_returns = df.groupby("ticker")["close"].pct_change(fill_method=None)
    suspicious_mask = daily_returns.abs() > threshold
    for i in range(0,len(suspicious_mask)):
        if suspicious_mask.loc[i] == True:
            if pd.isna(df.loc[i,"warning"]) == True:
                df.loc[i,"warning"]="suspicious_price_jumps"
            else:
                df.loc[i,"warning"]="controversial and suspicious_price_jumps"
    return df
    
stock = pd.read_csv("./data/raw/dirty_stock_daily_ohlcv.csv")
check_required_columns(stock)
stock=drop_invalid_dates(stock)
stock=drop_missing_values(stock)
stock["warning"]=pd.NA
stock=drop_and_mark_duplicate_rows(stock)
stock=drop_non_positive_prices(stock)
stock=drop_negative_volume(stock)
stock=check_ohlc_relationships(stock)
stock=mark_suspicious_price_jumps(stock)
stock.to_csv("./data/final/clean_stock_daily_ohlcv.csv",index=False)
