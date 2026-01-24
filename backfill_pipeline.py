import os
import pandas as pd
import numpy as np
import hopsworks
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 1. Environment variables load karein
load_dotenv()
HOPSWORKS_KEY = os.getenv("HOPSWORKS_API_KEY")

def generate_historical_data(days=30):
    """Pichlay kuch dinon ka Lahore ka AQI aur Weather data simulate karna"""
    data_list = []
    end_date = datetime.now()
    
    print(f"Generating data for last {days} days...")
    
    for i in range(days):
        current_date = end_date - timedelta(days=i)
        date_str = current_date.strftime('%Y-%m-%d')
        
        # Lahore ke January weather ke mutabiq random values
        # Raat ko AQI zyada hota hai, din mein thoda kam
        for hour in range(0, 24, 6): # Har 6 ghante ka data (4 rows per day)
            temp = np.random.uniform(8, 18)        # 8°C se 18°C ke darmiyan
            humidity = np.random.uniform(40, 90)   # 40% se 90% humidity
            wind_speed = np.random.uniform(0.5, 4.0)
            
            # AQI simulation (Lahore mein aksar 150-350 ke darmiyan hota hai)
            aqi = int(np.random.uniform(150, 350))
            pm25 = aqi * 0.8 # Rough estimation
            
            data_list.append({
                'date': date_str,
                'hour': hour,
                'temp': round(temp, 2),
                'humidity': int(humidity),
                'wind_speed': round(wind_speed, 2),
                'aqi': aqi,
                'pm25': round(pm25, 2)
            })
            
    return pd.DataFrame(data_list)

# --- EXECUTION ---
df_history = generate_historical_data(30) # 30 din ka data

try:
    # 2. Hopsworks login
    project = hopsworks.login(
        api_key_value=HOPSWORKS_KEY,
        project="AQI_Forecasting_Saneha"
    )
    fs = project.get_feature_store()

    # 3. Existing Feature Group hasil karein
    aqi_fg = fs.get_feature_group(name="aqi_data", version=1)

    # 4. Historical data insert karein
    print("Uploading historical data to Hopsworks...")
    aqi_fg.insert(df_history)
    
    print(f"\n--- Mubarak ho! {len(df_history)} rows upload ho gayi hain ---")
    print(df_history.head())

except Exception as e:
    print(f"Error: {e}")