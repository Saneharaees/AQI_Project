import streamlit as st
import hopsworks
import joblib
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Environment variables load karein
load_dotenv()

# Page Configuration
st.set_page_config(page_title="Lahore AQI Forecast", page_icon="🌬️", layout="centered")

st.title("🌬️ Lahore Air Quality Forecast Dashboard")
st.markdown("---")
st.write("### Professional ML Pipeline: Hopsworks ↔️ Random Forest")
st.info("Ye dashboard Hopsworks Model Registry se live model uthata hai aur aapke parameters par AQI predict karta hai.")

# Model Loading Logic (Cached to avoid repeated downloads)
@st.cache_resource
def load_model_from_hopsworks():
    # Hopsworks login
    project = hopsworks.login(api_key_value=os.getenv("HOPSWORKS_API_KEY"))
    mr = project.get_model_registry()
    
    # Model download karein
    model_obj = mr.get_model("aqi_forecaster", version=1)
    model_dir = model_obj.download()
    
    # Model load karein
    model_path = os.path.join(model_dir, "aqi_model.pkl")
    model = joblib.load(model_path)
    return model

try:
    # Model fetching status
    with st.spinner("🔄 Hopsworks se model fetch ho raha hai..."):
        model = load_model_from_hopsworks()
    st.success("✅ Model Loaded Successfully!")

    # --- UI Columns for Inputs ---
    st.subheader("📍 Predict Future AQI for Lahore")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        temp = st.slider("Temperature (°C)", 5, 45, 20)
    with col2:
        hum = st.slider("Humidity (%)", 10, 100, 60)
    with col3:
        wind = st.slider("Wind Speed (m/s)", 0.0, 10.0, 3.0)

    # --- Prediction Logic ---
    now = datetime.now()
    forecast_data = []
    
    # Aglay 3 din ki forecast
    for i in range(1, 4):
        future_date = now + timedelta(days=i)
        
        # DataFrame format mein data (Warning fix karne ke liye)
        input_df = pd.DataFrame([[
            future_date.hour, 
            future_date.weekday(), 
            future_date.month, 
            temp, 
            hum, 
            wind
        ]], columns=['hour', 'day_of_week', 'month', 'temp', 'humidity', 'wind_speed'])
        
        # Prediction
        prediction = model.predict(input_df)[0]
        
        forecast_data.append({
            "Day": future_date.strftime('%A (%d %b)'), 
            "Predicted AQI": int(prediction)
        })

    # Results Display
    df_forecast = pd.DataFrame(forecast_data)
    
    st.markdown("### 📊 Forecast Results")
    
    # Styled Table and Chart
    c1, c2 = st.columns([1, 2])
    with c1:
        st.dataframe(df_forecast, hide_index=True)
    with c2:
        st.line_chart(df_forecast.set_index("Day"))

    st.success(f"Lahore ka forecasted AQI range: {df_forecast['Predicted AQI'].min()} - {df_forecast['Predicted AQI'].max()}")

except Exception as e:
    st.error(f"❌ Error logic mein masla hai: {e}")
    st.write("Check karein ke aapka API Key `.env` file mein sahi hai ya nahi.")

st.markdown("---")
st.caption("Developed by Saneha | Powered by Hopsworks & Streamlit")