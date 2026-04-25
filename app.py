import streamlit as st
from dotenv import load_dotenv
import os
import folium
from streamlit_folium import st_folium
import requests

load_dotenv()

from modules.pre_disaster import show_pre_disaster
from modules.present_disaster import show_present_disaster
from modules.post_disaster import show_post_disaster

st.set_page_config(
    page_title="DisasterSense",
    page_icon="🌍",
    layout="wide"
)

# ── Custom CSS ──────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    section[data-testid="stSidebar"] {
        background-color: #1a1d27;
        border-right: 1px solid #2e3250;
    }
    div[data-testid="metric-container"] {
        background-color: #1e2130;
        border: 1px solid #2e3250;
        border-radius: 10px;
        padding: 15px;
    }
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: 0.2s;
    }
    .streamlit-expanderHeader { background-color: #1e2130; border-radius: 8px; }
    .stTabs [data-baseweb="tab"] { font-weight: 600; font-size: 15px; }
    .stProgress > div > div { background-color: #4e8df5; }
    .stAlert { border-radius: 10px; }
    h1 { color: #ffffff; }
    h2 { color: #e0e0e0; }
    h3 { color: #c0c0c0; }

    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .hero {
        background: linear-gradient(-45deg, #0f3460, #16213e, #1a1d27, #1a4a6b);
        background-size: 400% 400%;
        animation: gradient 8s ease infinite;
        padding: 35px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 25px;
    }
    .feature-card {
        background: #1e2130;
        border: 1px solid #2e3250;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        min-height: 160px;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:10px 0 20px 0;'>
        <h1 style='font-size:2rem; margin-bottom:0;'>🌍</h1>
        <h2 style='font-size:1.4rem; color:#ffffff; margin-top:5px;'>DisasterSense</h2>
        <p style='color:#888; font-size:0.85rem; margin-top:-5px;'>AI-Powered Disaster Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    page = st.radio(
        "Navigate",
        ["🏠 Home", "🟡 Pre-Disaster", "🔴 Present Disaster", "🟢 Post-Disaster"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("#### 📖 How to Use")
    st.markdown("""
- **🟡 Pre-Disaster** — Real-time flood, wildfire & cyclone risk
- **🔴 Present Disaster** — Live news + AI legitimacy scoring
- **🟢 Post-Disaster** — Hospitals & shelters near affected area
    """)
    st.markdown("---")
    st.markdown("""
    <div style='text-align:center; color:#555; font-size:0.78rem;'>
        Built for Nexora Hackathon<br>
        Gemini AI · OpenWeatherMap · NewsAPI · OSM
    </div>
    """, unsafe_allow_html=True)

# ── HOME PAGE ────────────────────────────────────────────
if page == "🏠 Home":

    # Hero banner
    st.markdown("""
    <div class='hero'>
        <h1 style='color:white; font-size:2.8rem; margin-bottom:5px;'>🌍 DisasterSense</h1>
        <p style='color:#aaa; font-size:1.05rem; margin:0;'>
            Predict Before · Monitor During · Recover After
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Feature cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class='feature-card'>
            <h2 style='font-size:2rem;'>🟡</h2>
            <h3 style='color:#fff; font-size:1rem;'>Pre-Disaster</h3>
            <p style='color:#888; font-size:0.82rem;'>
                Real-time flood, wildfire & cyclone risk using live weather data
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='feature-card'>
            <h2 style='font-size:2rem;'>🔴</h2>
            <h3 style='color:#fff; font-size:1rem;'>Present Disaster</h3>
            <p style='color:#888; font-size:0.82rem;'>
                Live news monitoring with AI legitimacy scoring & manual reporting
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class='feature-card'>
            <h2 style='font-size:2rem;'>🟢</h2>
            <h3 style='color:#fff; font-size:1rem;'>Post-Disaster</h3>
            <p style='color:#888; font-size:0.82rem;'>
                Find nearby hospitals, shelters & clinics in affected areas
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── LIVE MAP DASHBOARD ──────────────────────────────
    st.markdown("### 🗺️ Live Global Disaster Risk Map")
    st.caption("Real-time weather-based risk indicators across major Indian cities")

    # Major Indian cities to monitor
    CITIES = [
        {"name": "Mumbai",     "lat": 19.0760, "lon": 72.8777},
        {"name": "Chennai",    "lat": 13.0827, "lon": 80.2707},
        {"name": "Kolkata",    "lat": 22.5726, "lon": 88.3639},
        {"name": "Delhi",      "lat": 28.6139, "lon": 77.2090},
        {"name": "Bengaluru",  "lat": 12.9716, "lon": 77.5946},
        {"name": "Hyderabad",  "lat": 17.3850, "lon": 78.4867},
        {"name": "Bhubaneswar","lat": 20.2961, "lon": 85.8245},
        {"name": "Kochi",      "lat": 9.9312,  "lon": 76.2673},
        {"name": "Ahmedabad",  "lat": 23.0225, "lon": 72.5714},
        {"name": "Guwahati",   "lat": 26.1445, "lon": 91.7362},
    ]

    def get_city_weather(lat, lon):
        api_key = os.getenv("OPENWEATHER_API_KEY")
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        try:
            r = requests.get(url, timeout=8)
            if r.status_code == 200:
                return r.json()
        except:
            pass
        return None

    def compute_risk(weather):
        if not weather:
            return "LOW", "green", "⚪"
        
        score = 0
        humidity = weather["main"]["humidity"]
        wind = weather["wind"]["speed"] * 3.6
        pressure = weather["main"]["pressure"]
        temp = weather["main"]["temp"]
        rain = weather.get("rain", {}).get("1h", 0)
        condition = weather["weather"][0]["id"]

        if rain > 10: score += 35
        elif rain > 5: score += 20
        if humidity > 90: score += 20
        elif humidity > 75: score += 10
        if wind > 60: score += 30
        elif wind > 40: score += 15
        if pressure < 990: score += 15
        if temp > 38 and humidity < 30: score += 20
        if condition < 300: score += 10

        if score >= 55:
            return "HIGH", "red", "🔴"
        elif score >= 30:
            return "MEDIUM", "orange", "🟠"
        else:
            return "LOW", "green", "🟢"

    # Build the map
    m = folium.Map(
        location=[20.5937, 78.9629],
        zoom_start=5,
        tiles="CartoDB dark_matter"
    )

    with st.spinner("Loading live weather data for Indian cities..."):
        city_risks = []
        for city in CITIES:
            weather = get_city_weather(city["lat"], city["lon"])
            risk_level, color, emoji = compute_risk(weather)

            temp = weather["main"]["temp"] if weather else "N/A"
            humidity = weather["main"]["humidity"] if weather else "N/A"
            wind = round(weather["wind"]["speed"] * 3.6, 1) if weather else "N/A"
            condition = weather["weather"][0]["description"].title() if weather else "N/A"

            popup_html = f"""
            <div style='font-family:Arial; min-width:160px;'>
                <b style='font-size:14px;'>{emoji} {city['name']}</b><br>
                <hr style='margin:4px 0;'>
                🌡️ Temp: <b>{temp}°C</b><br>
                💧 Humidity: <b>{humidity}%</b><br>
                💨 Wind: <b>{wind} km/h</b><br>
                🌤️ {condition}<br>
                <hr style='margin:4px 0;'>
                ⚠️ Risk: <b style='color:{"red" if risk_level=="HIGH" else "orange" if risk_level=="MEDIUM" else "green"};'>{risk_level}</b>
            </div>
            """

            # Pulse effect for high risk cities
            if risk_level == "HIGH":
                folium.CircleMarker(
                    location=[city["lat"], city["lon"]],
                    radius=20,
                    color="red",
                    fill=True,
                    fill_opacity=0.15,
                    weight=2
                ).add_to(m)

            folium.CircleMarker(
                location=[city["lat"], city["lon"]],
                radius=12,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.8,
                popup=folium.Popup(popup_html, max_width=200),
                tooltip=f"{emoji} {city['name']} — {risk_level} RISK"
            ).add_to(m)

            city_risks.append({
                "city": city["name"],
                "risk": risk_level,
                "emoji": emoji,
                "color": color
            })

    # Show map
    st_folium(m, width=None, height=450, returned_objects=[])

    # Risk summary below map
    st.markdown("#### 📊 City Risk Summary")
    cols = st.columns(5)
    for i, cr in enumerate(city_risks):
        with cols[i % 5]:
            color_map = {"HIGH": "#e94560", "MEDIUM": "#f0a500", "LOW": "#2ecc71"}
            st.markdown(f"""
            <div style='background:#1e2130; border:1px solid #2e3250;
                        border-radius:8px; padding:10px; text-align:center; margin-bottom:8px;'>
                <p style='margin:0; font-size:1.1rem;'>{cr['emoji']}</p>
                <p style='margin:0; color:#fff; font-size:0.85rem; font-weight:600;'>{cr['city']}</p>
                <p style='margin:0; color:{color_map[cr["risk"]]}; font-size:0.78rem;'>{cr['risk']}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background:#1e2130; border:1px solid #2e3250;
                border-radius:12px; padding:20px; text-align:center;'>
        <p style='color:#888; margin:0;'>
            🤖 Gemini AI &nbsp;·&nbsp; 🌤️ OpenWeatherMap
            &nbsp;·&nbsp; 📰 NewsAPI &nbsp;·&nbsp; 🗺️ OpenStreetMap
        </p>
    </div>
    """, unsafe_allow_html=True)

# ── OTHER PAGES ──────────────────────────────────────────
elif page == "🟡 Pre-Disaster":
    show_pre_disaster()

elif page == "🔴 Present Disaster":
    show_present_disaster()

elif page == "🟢 Post-Disaster":
    show_post_disaster()