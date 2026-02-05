import pandas as pd

def fetch_allen_coral_atlas():
    # Static / slow-changing reef dataset
    data = {
        "latitude": [15.0],
        "longitude": [80.0],
        "reef_type": ["Fringing Reef"],
        "reef_health_baseline": [85]
    }
    return pd.DataFrame(data)
