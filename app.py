import streamlit as st
import hopsworks
import joblib
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Lahore AQI Forecast", page_icon="🌬️")

st.title("🌬️ Lahore Air Quality Forecast Dashboard")
st.write("Professional ML Pipeline using Hopsworks & Random Forest")

@st.cache_resource
def load_model_from_hopsworks():
    project = hopsworks.login(api_key_value=os.getenv("HOPSWORKS_API_KEY"))
    mr = project.get_model_registry()
    # Model Registry se model download karna
    model_obj = mr.get_model("aqi_forecaster", version=1)
    model_dir = model_obj.download()
    model = joblib.load(os.path.join(model_dir, "aqi_model.pkl"))
    return model

try:
    with st.spinner("Fetching model from Hopsworks..."):
        model = load_model_from_hopsworks()
    st.success("✅ Model Loaded Successfully!")

    # User Input for Prediction (or auto-fetch from API)
    st.subheader("Predict Future AQI")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        temp = st.slider("Temperature (°C)", 5, 45, 18)
    with col2:
        hum = st.slider("Humidity (%)", 10, 100, 55)
    with col3:
        wind = st.slider("Wind Speed (m/s)", 0.0, 10.0, 2.5)

    # Current time features
    now = datetime.now()
    
    # Prepare data for 3 days forecast
    forecast_data = []
    for i in range(1, 4):
        future_date = now + timedelta(days=i)
        features = [[
            future_date.hour, 
            future_date.weekday(), 
            future_date.month, 
            temp, 
            hum, 
            wind
        ]]
        prediction = model.predict(features)[0]
        forecast_data.append({"Day": future_date.strftime('%A'), "Predicted AQI": int(prediction)})

    df_forecast = pd.DataFrame(forecast_data)
    
    # Display Results
    st.table(df_forecast)
    st.line_chart(df_forecast.set_index("Day"))

except Exception as e:
    st.error(f"Error: {e}")