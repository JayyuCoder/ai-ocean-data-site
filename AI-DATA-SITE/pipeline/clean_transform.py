def clean_noaa(df):
    df = df.dropna()
    df["sst"] = df["sst"].clip(lower=0)
    if "dhw" not in df.columns:
        df["dhw"] = 0.0
    df["dhw"] = df["dhw"].clip(lower=0)
    return df

def clean_allen(df):
    df = df.dropna()
    if "reef_health_baseline" in df.columns:
        df["reef_health_baseline"] = df["reef_health_baseline"].clip(0, 100)
    else:
        # Default baseline if not provided by WFS layer
        df["reef_health_baseline"] = 80
    return df
