import pandas as pd
import numpy as np
import hopsworks
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import time

load_dotenv()

def generate_historical_lahore_data(days=15):
    data_list = []
    end_date = datetime.now()
    print(f"Generating data for last {days} days...")
    
    for i in range(days * 24):
        current_time = end_date - timedelta(hours=i)
        base_aqi = 250 if (current_time.hour < 8 or current_time.hour > 20) else 180
        aqi = int(base_aqi + np.random.normal(0, 30))
        temp = 12 + np.random.normal(0, 4)
        humidity = 60 + np.random.normal(0, 10)
        
        data_list.append({
            'city': 'Lahore',
            'date': current_time.strftime('%Y-%m-%d'),
            'timestamp': int(current_time.timestamp()),
            'hour': current_time.hour,
            'day_of_week': current_time.weekday(),
            'month': current_time.month,
            'temp': round(temp, 2),
            'humidity': int(humidity),
            'wind_speed': round(np.random.uniform(0.5, 3.5), 2),
            'aqi': max(aqi, 50)
        })
    return pd.DataFrame(data_list)

# Execution
df_history = generate_historical_lahore_data(15)

try:
    project = hopsworks.login(api_key_value=os.getenv("HOPSWORKS_API_KEY"))
    fs = project.get_feature_store()
    aqi_fg = fs.get_feature_group(name="aqi_data_real", version=1)

    print("Uploading 360 rows to Hopsworks (with wait logic)...")
    # write_options ka use connection timeout ko rokne ke liye
    aqi_fg.insert(df_history, write_options={"wait_for_job": False}) 
    
    print("✅ Success! Data upload process started.")
    print("Dashboard check karein, materialization job background mein chal rahi hogi.")

except Exception as e:
    print(f"Error occurred: {e}")