import hopsworks
import os
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
import joblib
from dotenv import load_dotenv

load_dotenv()

# 1. Login
project = hopsworks.login(api_key_value=os.getenv("HOPSWORKS_API_KEY"))
fs = project.get_feature_store()

# 2. Get Feature View
view_name = "aqi_data_view"
feature_view = fs.get_feature_view(name=view_name, version=1)

# 3. Fetch Training Data (The Professional Way)
print("Fetching 361 rows for training...")
try:
    # training_data() use karne se features (X) aur labels (y) alag milte hain
    X_data, y_data = feature_view.training_data(description="Lahore AQI Dataset")
    
    if X_data is not None:
        print(f"✅ Data Ready: {len(X_data)} rows.")
        
        # Hopsworks column names ko hamesha lowercase rakhta hai
        # Hum sirf zaroori features select kar rahe hain
        features = ['hour', 'day_of_week', 'month', 'temp', 'humidity', 'wind_speed']
        X = X_data[features]
        y = y_data
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # 4. Model Training
        print("Training Random Forest Model...")
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        mae = mean_absolute_error(y_test, model.predict(X_test))
        print(f"🚀 SUCCESS: Model Trained! MAE: {mae:.2f}")

        # 5. Register Model in Registry
        model_dir = "aqi_model_dir"
        if not os.path.exists(model_dir): os.makedirs(model_dir)
        joblib.dump(model, os.path.join(model_dir, "aqi_model.pkl"))

        mr = project.get_model_registry()
        aqi_model = mr.python.create_model(
            name="aqi_forecaster", 
            metrics={"mae": mae},
            description="Final Lahore AQI Prediction Model"
        )
        aqi_model.save(model_dir)
        print("🌟 EXCELLENT: Model is now in Model Registry!")
    else:
        print("❌ Dataset empty.")

except Exception as e:
    print(f"❌ Detailed Training Error: {e}")