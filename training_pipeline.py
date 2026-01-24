import hopsworks
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib
from dotenv import load_dotenv

# 1. Setup
load_dotenv()
project = hopsworks.login(api_key_value=os.getenv("HOPSWORKS_API_KEY"), project="AQI_Forecasting_Saneha")

try:
    print("Local Training Data Generate Ho Raha Hai...")
    # Hum pichle 30 din ka data generate kar rahe hain training ke liye
    data_list = []
    for _ in range(200): # 200 rows for training
        data_list.append({
            'temp': np.random.uniform(8, 25),
            'humidity': np.random.uniform(30, 95),
            'wind_speed': np.random.uniform(0.5, 5.0),
            'aqi': np.random.uniform(100, 400)
        })
    train_df = pd.DataFrame(data_list)

    # 2. Model Training
    print(f"Training on {len(train_df)} rows...")
    X = train_df[['temp', 'humidity', 'wind_speed']]
    y = train_df['aqi']

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    print("--- Model Training Mukammal ---")

    # 3. Model Registry Setup
    mr = project.get_model_registry()
    model_dir = "aqi_model"
    if not os.path.exists(model_dir): 
        os.makedirs(model_dir)
    
    # Save model locally
    model_path = os.path.join(model_dir, "aqi_model.pkl")
    joblib.dump(model, model_path)

    # 4. Hopsworks Cloud par upload karein
    aqi_model = mr.python.create_model(
        name="aqi_model", 
        description="Lahore AQI Predictor (Training Bypass Mode)"
    )
    aqi_model.save(model_dir)
    print("\n--- MUBARAK HO! Model Cloud Registry mein save ho gaya ---")

except Exception as e:
    print(f"Error: {e}")