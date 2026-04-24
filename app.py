import streamlit as st
from dotenv import load_dotenv
import os

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
    .stApp {
        background-color: #0f1117;
    }
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
    .streamlit-expanderHeader {
        background-color: #1e2130;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 15px;
    }
    .stProgress > div > div {
        background-color: #4e8df5;
    }
    .stAlert {
        border-radius: 10px;
    }
    h1 { color: #ffffff; }
    h2 { color: #e0e0e0; }
    h3 { color: #c0c0c0; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 10px 0 20px 0;'>
        <h1 style='font-size: 2rem; margin-bottom: 0;'>🌍</h1>
        <h2 style='font-size: 1.4rem; color: #ffffff; margin-top: 5px;'>DisasterSense</h2>
        <p style='color: #888; font-size: 0.85rem; margin-top: -5px;'>
            AI-Powered Disaster Intelligence
        </p>
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
- **🟡 Pre-Disaster** — Check real-time risk levels for floods, wildfires & cyclones before they hit
- **🔴 Present Disaster** — Monitor live news & report incidents happening right now  
- **🟢 Post-Disaster** — Find nearby hospitals & shelters in affected areas
    """)

    st.markdown("---")

    st.markdown("""
    <div style='text-align: center; color: #555; font-size: 0.78rem;'>
        Built for Nexora Hackathon<br>
        Powered by Gemini AI · OpenWeatherMap · NewsAPI · OpenStreetMap
    </div>
    """, unsafe_allow_html=True)

# ── Page Routing ─────────────────────────────────────────
if page == "🏠 Home":
    st.markdown("""
    <div style='text-align: center; padding: 40px 0 30px 0;'>
        <h1 style='font-size: 3rem;'>🌍 DisasterSense</h1>
        <h3 style='color: #888; font-weight: 400;'>
            AI-Powered Disaster Intelligence Platform
        </h3>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style='background:#1e2130; border:1px solid #2e3250;
                    border-radius:12px; padding:20px; text-align:center; min-height:240px;'>
            <h1 style='font-size:2.5rem;'>🟡</h1>
            <h3 style='color:#ffffff; font-size:1rem;'>Pre-Disaster</h3>
            <p style='color:#888; font-size:0.82rem;'>Real-time flood, wildfire & cyclone risk using live weather data</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='background:#1e2130; border:1px solid #2e3250;
                    border-radius:12px; padding:20px; text-align:center; min-height:240px;'>
            <h1 style='font-size:2.5rem;'>🔴</h1>
            <h3 style='color:#ffffff; font-size:1rem;'>Present Disaster</h3>
            <p style='color:#888; font-size:0.82rem;'>Live news monitoring with AI legitimacy scoring & manual reporting</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style='background:#1e2130; border:1px solid #2e3250;
                    border-radius:12px; padding:20px; text-align:center; min-height:240px;'>
            <h1 style='font-size:2.5rem;'>🟢</h1>
            <h3 style='color:#ffffff; font-size:1rem;'>Post-Disaster</h3>
            <p style='color:#888; font-size:0.82rem;'>Find nearby hospitals, shelters & clinics in affected areas</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown("""
    <div style='background:#1e2130; border:1px solid #2e3250;
                border-radius:12px; padding:25px; text-align:center;'>
        <h3 style='color:#ffffff;'>⚡ Powered By</h3>
        <p style='color:#888;'>
            🤖 Gemini AI &nbsp;·&nbsp; 🌤️ OpenWeatherMap &nbsp;·&nbsp; 
            📰 NewsAPI &nbsp;·&nbsp; 🗺️ OpenStreetMap
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("👈 Select a section from the sidebar to get started")

elif page == "🟡 Pre-Disaster":
    show_pre_disaster()

elif page == "🔴 Present Disaster":
    show_present_disaster()

elif page == "🟢 Post-Disaster":
    show_post_disaster()