import streamlit as st
import hopsworks
import joblib
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Environment variables load karein
load_dotenv()

# Page Configuration
st.set_page_config(page_title="Lahore AQI Forecast", page_icon="🌬️", layout="wide")

st.title("🌬️ Lahore Air Quality Forecast Dashboard")
st.write("### Professional ML Pipeline: Hopsworks ↔️ Random Forest")

# Model Loading Logic
@st.cache_resource
def load_model_from_hopsworks():
    project = hopsworks.login(api_key_value=os.getenv("HOPSWORKS_API_KEY"))
    mr = project.get_model_registry()
    model_obj = mr.get_model("aqi_forecaster", version=1)
    model_dir = model_obj.download()
    model_path = os.path.join(model_dir, "aqi_model.pkl")
    return joblib.load(model_path)

try:
    with st.spinner("🔄 Fetching model..."):
        model = load_model_from_hopsworks()
    st.success("✅ Model Loaded Successfully!")

    # --- Sidebar for Inputs ---
    st.sidebar.header("📍 Weather Parameters")
    temp = st.sidebar.slider("Temperature (°C)", 5, 45, 20)
    hum = st.sidebar.slider("Humidity (%)", 10, 100, 60)
    wind = st.sidebar.slider("Wind Speed (m/s)", 0.0, 10.0, 3.0)

    # --- Prediction Logic ---
    now = datetime.now()
    forecast_data = []
    for i in range(1, 4):
        future_date = now + timedelta(days=i)
        input_df = pd.DataFrame([[
            future_date.hour, future_date.weekday(), future_date.month, temp, hum, wind
        ]], columns=['hour', 'day_of_week', 'month', 'temp', 'humidity', 'wind_speed'])
        
        prediction = model.predict(input_df)[0]
        forecast_data.append({"Day": future_date.strftime('%A (%d %b)'), "Predicted AQI": int(prediction)})

    df_forecast = pd.DataFrame(forecast_data)

    # --- HAZARD ALERTS (Requirement Check) ---
    latest_aqi = df_forecast.iloc[0]['Predicted AQI']
    st.subheader("⚠️ Health Advisory")
    if latest_aqi > 300:
        st.error(f"HAZARDOUS ({latest_aqi}): Stay indoors! Air quality is extremely poor.")
    elif latest_aqi > 200:
        st.warning(f"VERY UNHEALTHY ({latest_aqi}): Wear a mask outdoors.")
    elif latest_aqi > 150:
        st.info(f"UNHEALTHY ({latest_aqi}): Sensitive groups should limit outdoor time.")
    else:
        st.success(f"GOOD/MODERATE ({latest_aqi}): Air quality is acceptable.")

    # --- Visualizations ---
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📊 3-Day Forecast")
        st.line_chart(df_forecast.set_index("Day"))
        st.table(df_forecast)

    with col2:
        # --- FEATURE IMPORTANCE (SHAP Alternative) ---
        st.markdown("### 🔍 Feature Importance")
        st.write("Which factors influenced this prediction?")
        importance = model.feature_importances_
        feature_names = ['Hour', 'Day', 'Month', 'Temp', 'Humidity', 'Wind']
        feat_df = pd.DataFrame({'Feature': feature_names, 'Importance': importance}).sort_values(by='Importance')
        
        fig, ax = plt.subplots()
        ax.barh(feat_df['Feature'], feat_df['Importance'], color='skyblue')
        st.pyplot(fig)

except Exception as e:
    st.error(f"❌ Error: {e}")

st.markdown("---")
st.caption("Developed by Saneha | Real-time Serverless ML Pipeline")