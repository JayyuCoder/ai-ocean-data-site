def clean_noaa(df):
    df = df.dropna()
    df["sst"] = df["sst"].clip(lower=0)
    df["dhw"] = df["dhw"].clip(lower=0)
    return df

def clean_allen(df):
    df = df.dropna()
    df["reef_health_baseline"] = df["reef_health_baseline"].clip(0, 100)
    return df
