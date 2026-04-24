import streamlit as st
import requests
import os

def get_weather_data(city):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_forecast_data(city):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def calculate_flood_risk(weather, forecast):
    score = 0
    reasons = []

    # Check current rain
    rain = weather.get("rain", {}).get("1h", 0)
    if rain > 10:
        score += 40
        reasons.append(f"🌧️ Heavy rainfall right now: {rain}mm/hr")
    elif rain > 5:
        score += 20
        reasons.append(f"🌧️ Moderate rainfall: {rain}mm/hr")

    # Check humidity
    humidity = weather["main"]["humidity"]
    if humidity > 90:
        score += 20
        reasons.append(f"💧 Very high humidity: {humidity}%")
    elif humidity > 75:
        score += 10
        reasons.append(f"💧 High humidity: {humidity}%")

    # Check forecast for upcoming rain
    rain_in_forecast = 0
    for item in forecast["list"][:8]:  # next 24 hours
        rain_in_forecast += item.get("rain", {}).get("3h", 0)
    if rain_in_forecast > 30:
        score += 30
        reasons.append(f"⛈️ Heavy rain expected in next 24hrs: {rain_in_forecast:.1f}mm total")
    elif rain_in_forecast > 15:
        score += 15
        reasons.append(f"🌦️ Rain expected in next 24hrs: {rain_in_forecast:.1f}mm total")

    # Weather condition codes for storms
    condition_id = weather["weather"][0]["id"]
    if condition_id < 300:  # Thunderstorm
        score += 10
        reasons.append("⛈️ Thunderstorm conditions detected")

    return min(score, 100), reasons

def calculate_wildfire_risk(weather):
    score = 0
    reasons = []

    temp = weather["main"]["temp"]
    humidity = weather["main"]["humidity"]
    wind_speed = weather["wind"]["speed"]  # m/s

    # Temperature check
    if temp > 40:
        score += 40
        reasons.append(f"🌡️ Extreme temperature: {temp}°C")
    elif temp > 35:
        score += 25
        reasons.append(f"🌡️ Very high temperature: {temp}°C")
    elif temp > 30:
        score += 10
        reasons.append(f"🌡️ High temperature: {temp}°C")

    # Low humidity = dry = fire risk
    if humidity < 20:
        score += 35
        reasons.append(f"🏜️ Very low humidity: {humidity}% (extremely dry)")
    elif humidity < 35:
        score += 20
        reasons.append(f"🏜️ Low humidity: {humidity}% (dry conditions)")

    # Wind speed
    if wind_speed > 10:
        score += 25
        reasons.append(f"💨 Strong winds: {wind_speed * 3.6:.1f} km/h (spreads fire fast)")
    elif wind_speed > 6:
        score += 10
        reasons.append(f"💨 Moderate winds: {wind_speed * 3.6:.1f} km/h")

    return min(score, 100), reasons

def calculate_cyclone_risk(weather, forecast):
    score = 0
    reasons = []

    wind_speed = weather["wind"]["speed"]  # m/s
    pressure = weather["main"]["pressure"]  # hPa
    temp = weather["main"]["temp"]
    humidity = weather["main"]["humidity"]

    # Wind speed (m/s → km/h)
    wind_kmh = wind_speed * 3.6
    if wind_kmh > 90:
        score += 50
        reasons.append(f"🌀 Extremely high wind speed: {wind_kmh:.1f} km/h")
    elif wind_kmh > 60:
        score += 35
        reasons.append(f"🌀 Very high wind speed: {wind_kmh:.1f} km/h")
    elif wind_kmh > 40:
        score += 15
        reasons.append(f"💨 Elevated wind speed: {wind_kmh:.1f} km/h")

    # Low pressure = storm system
    if pressure < 970:
        score += 35
        reasons.append(f"📉 Very low atmospheric pressure: {pressure} hPa (storm system)")
    elif pressure < 990:
        score += 20
        reasons.append(f"📉 Low atmospheric pressure: {pressure} hPa")

    # High temp + humidity = cyclone-favorable
    if temp > 28 and humidity > 80:
        score += 15
        reasons.append(f"🌊 Warm & humid conditions: {temp}°C, {humidity}% humidity (cyclone-favorable)")

    # Check forecast wind trend
    max_forecast_wind = 0
    for item in forecast["list"][:8]:
        fw = item.get("wind", {}).get("speed", 0) * 3.6
        if fw > max_forecast_wind:
            max_forecast_wind = fw
    if max_forecast_wind > wind_kmh + 20:
        score += 10
        reasons.append(f"📈 Winds expected to intensify to {max_forecast_wind:.1f} km/h in next 24hrs")

    return min(score, 100), reasons

def get_risk_level(score):
    if score >= 70:
        return "🔴 HIGH", "red"
    elif score >= 40:
        return "🟠 MEDIUM", "orange"
    else:
        return "🟢 LOW", "green"

def show_pre_disaster():
    st.title("🟡 Pre-Disaster Risk Monitor")
    st.markdown("Real-time risk assessment using live weather data")
    st.markdown("---")

    city = st.text_input("🔍 Enter City Name", placeholder="e.g. Mumbai, Chennai, Kolkata")

    if st.button("Analyze Risk", type="primary"):
        if not city:
            st.warning("Please enter a city name.")
            return

        with st.spinner("Fetching live weather data..."):
            weather = get_weather_data(city)
            forecast = get_forecast_data(city)

        if not weather or not forecast:
            st.error("City not found or API error. Check your city name or API key.")
            return

        # Display current conditions
        st.subheader(f"📍 Current Conditions in {weather['name']}, {weather['sys']['country']}")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🌡️ Temperature", f"{weather['main']['temp']}°C")
        col2.metric("💧 Humidity", f"{weather['main']['humidity']}%")
        col3.metric("💨 Wind Speed", f"{weather['wind']['speed'] * 3.6:.1f} km/h")
        col4.metric("📉 Pressure", f"{weather['main']['pressure']} hPa")

        st.markdown("---")
        st.subheader("⚠️ Risk Assessment")

        # Calculate all 3 risks
        flood_score, flood_reasons = calculate_flood_risk(weather, forecast)
        wildfire_score, wildfire_reasons = calculate_wildfire_risk(weather)
        cyclone_score, cyclone_reasons = calculate_cyclone_risk(weather, forecast)

        col1, col2, col3 = st.columns(3)

        with col1:
            level, color = get_risk_level(flood_score)
            st.markdown(f"### 🌊 Flood Risk")
            st.markdown(f"**Risk Level: {level}**")
            st.progress(flood_score / 100)
            st.markdown(f"**Score: {flood_score}/100**")
            if flood_reasons:
                with st.expander("Why this score?"):
                    for r in flood_reasons:
                        st.markdown(f"- {r}")
            else:
                st.success("No flood indicators detected")

        with col2:
            level, color = get_risk_level(wildfire_score)
            st.markdown(f"### 🔥 Wildfire Risk")
            st.markdown(f"**Risk Level: {level}**")
            st.progress(wildfire_score / 100)
            st.markdown(f"**Score: {wildfire_score}/100**")
            if wildfire_reasons:
                with st.expander("Why this score?"):
                    for r in wildfire_reasons:
                        st.markdown(f"- {r}")
            else:
                st.success("No wildfire indicators detected")

        with col3:
            level, color = get_risk_level(cyclone_score)
            st.markdown(f"### 🌀 Cyclone Risk")
            st.markdown(f"**Risk Level: {level}**")
            st.progress(cyclone_score / 100)
            st.markdown(f"**Score: {cyclone_score}/100**")
            if cyclone_reasons:
                with st.expander("Why this score?"):
                    for r in cyclone_reasons:
                        st.markdown(f"- {r}")
            else:
                st.success("No cyclone indicators detected")

        st.markdown("---")

        # Overall alert
        max_score = max(flood_score, wildfire_score, cyclone_score)
        if max_score >= 70:
            st.error("🚨 HIGH RISK DETECTED — Immediate precautionary measures recommended for this region.")
        elif max_score >= 40:
            st.warning("⚠️ MEDIUM RISK — Monitor the situation closely. Stay prepared.")
        else:
            st.success("✅ All risk levels are LOW — No immediate disaster threat detected.")