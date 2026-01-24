import streamlit as st
import hopsworks
import joblib
import os
from dotenv import load_dotenv

# 1. Setup & Connection
load_dotenv()
st.set_page_config(page_title="Lahore AQI Predictor", page_icon="🌤️")

@st.cache_resource
def get_model():
    project = hopsworks.login(api_key_value=os.getenv("HOPSWORKS_API_KEY"), project="AQI_Forecasting_Saneha")
    mr = project.get_model_registry()
    # Cloud se model download karna
    model_obj = mr.get_model("aqi_model", version=1)
    model_dir = model_obj.download()
    model = joblib.load(os.path.join(model_dir, "aqi_model.pkl"))
    return model

# 2. UI Design
st.title("Lahore AQI Real-time Predictor 🇵🇰")
st.write("Is app ke zariye aap moosam ki soorat-e-haal daal kar Air Quality Index (AQI) maloom kar sakte hain.")

model = get_model()

with st.sidebar:
    st.header("Input Parameters")
    temp = st.slider("Temperature (°C)", 0, 50, 25)
    humidity = st.slider("Humidity (%)", 0, 100, 50)
    wind_speed = st.slider("Wind Speed (m/s)", 0.0, 10.0, 2.5)

# 3. Prediction Logic
if st.button("Predict AQI"):
    prediction = model.predict([[temp, humidity, wind_speed]])
    aqi_val = round(prediction[0])
    
    # Result Display
    st.subheader(f"Predicted AQI: {aqi_val}")
    
    if aqi_val <= 50:
        st.success("Good (Achi Sehat)")
    elif aqi_val <= 100:
        st.info("Satisfactory (Theek hai)")
    elif aqi_val <= 200:
        st.warning("Moderate (Thoda Nuqsan-deh)")
    else:
        st.error("Poor/Hazardous (Khatarnak)")