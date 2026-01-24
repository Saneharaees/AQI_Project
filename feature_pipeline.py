import os
import requests
import pandas as pd
import hopsworks
from datetime import datetime
from dotenv import load_dotenv

# 1. Environment variables (.env file) load karein
load_dotenv()
OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")
AQICN_TOKEN = os.getenv("AQICN_TOKEN")
HOPSWORKS_KEY = os.getenv("HOPSWORKS_API_KEY")
CITY = "Lahore"

def get_aqi_data():
    """APIs se live data fetch karne ka function"""
    # AQICN API se Air Quality data
    a_url = f"https://api.waqi.info/feed/{CITY}/?token={AQICN_TOKEN}"
    a_res = requests.get(a_url).json()
    
    # OpenWeather API se Weather data
    w_url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={OPENWEATHER_KEY}&units=metric"
    w_res = requests.get(w_url).json()

    if a_res['status'] == 'ok' and 'main' in w_res:
        data = {
            'date': [datetime.now().strftime('%Y-%m-%d')],
            'hour': [int(datetime.now().hour)],
            'temp': [float(w_res['main']['temp'])],
            'humidity': [int(w_res['main']['humidity'])],
            'wind_speed': [float(w_res['wind']['speed'])],
            'aqi': [int(a_res['data']['aqi'])],
            'pm25': [float(a_res['data']['iaqi'].get('pm25', {}).get('v', 0))]
        }
        return pd.DataFrame(data)
    else:
        print("Error: APIs se data nahi mil saka. Keys check karein.")
        return None

# --- MAIN EXECUTION ---
# 1. Pehle data fetch karein
df = get_aqi_data()

if df is not None:
    print("\n--- Terminal mein data mil gaya, ab Cloud par bhej rahe hain ---")
    print(df)

    try:
        # 2. Hopsworks mein login karein
        # Note: Project name wahi hai jo aapke dashboard par nazar aa raha tha
        project = hopsworks.login(
            api_key_value=HOPSWORKS_KEY,
            project="AQI_Forecasting_Saneha"
        )
        
        # 3. Feature Store ka access hasil karein
        fs = project.get_feature_store()

        # 4. Cloud par Table (Feature Group) banayein
        aqi_fg = fs.get_or_create_feature_group(
            name="aqi_data",
            version=1,
            primary_key=['date', 'hour'],
            description="Lahore live AQI and Weather data",
            online_enabled=True
        )

        # 5. Data ko Cloud Table mein dalkar upload karein
        aqi_fg.insert(df)
        
        print("\n--- Mubarak ho! Data Hopsworks Cloud par upload ho gaya ---")

    except Exception as e:
        print(f"Hopsworks Error: {e}")