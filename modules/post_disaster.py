import streamlit as st
import requests
import os
import folium
from streamlit_folium import st_folium
import time

def get_coordinates(city):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                return data[0]["lat"], data[0]["lon"], data[0]["name"], data[0]["country"]
    except:
        pass
    return None, None, None, None

def search_nominatim(lat, lon, query, city_name, radius_km=10):
    url = "https://nominatim.openstreetmap.org/search"
    delta = radius_km / 111.0
    bbox = f"{lon-delta},{lat-delta},{lon+delta},{lat+delta}"
    params = {
        "q": f"{query} {city_name}",
        "format": "json",
        "limit": 20,
        "viewbox": bbox,
        "bounded": 1,
        "addressdetails": 1
    }
    headers = {"User-Agent": "DisasterSense-HackathonApp/1.0"}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

def build_map(lat, lon, city_name, facility_options):
    m = folium.Map(location=[lat, lon], zoom_start=13, tiles="CartoDB positron")

    folium.Marker(
        location=[lat, lon],
        popup=f"⚠️ Affected Area: {city_name}",
        tooltip="Affected Area Center",
        icon=folium.Icon(color="red", icon="exclamation-sign", prefix="glyphicon")
    ).add_to(m)

    folium.Circle(
        location=[lat, lon],
        radius=5000,
        color="red",
        fill=True,
        fill_opacity=0.1,
        tooltip="Affected Zone (~5km radius)"
    ).add_to(m)

    counts = {"hospitals": 0, "shelters": 0, "clinics": 0}

    if "🏥 Hospitals" in facility_options:
        results = search_nominatim(lat, lon, "hospital", city_name)
        time.sleep(1)
        for h in results[:15]:
            hlat = float(h.get("lat", 0))
            hlon = float(h.get("lon", 0))
            name = h.get("display_name", "Hospital").split(",")[0]
            address = ", ".join(h.get("display_name", "").split(",")[:3])
            if hlat and hlon:
                folium.Marker(
                    location=[hlat, hlon],
                    popup=folium.Popup(f"<b>🏥 {name}</b><br>📍 {address}", max_width=250),
                    tooltip=f"🏥 {name}",
                    icon=folium.Icon(color="blue", icon="plus-sign", prefix="glyphicon")
                ).add_to(m)
                counts["hospitals"] += 1

    if "🏠 Shelters" in facility_options:
        results = search_nominatim(lat, lon, "shelter community centre", city_name)
        time.sleep(1)
        for s in results[:15]:
            slat = float(s.get("lat", 0))
            slon = float(s.get("lon", 0))
            name = s.get("display_name", "Shelter").split(",")[0]
            address = ", ".join(s.get("display_name", "").split(",")[:3])
            if slat and slon:
                folium.Marker(
                    location=[slat, slon],
                    popup=folium.Popup(f"<b>🏠 {name}</b><br>📍 {address}", max_width=250),
                    tooltip=f"🏠 {name}",
                    icon=folium.Icon(color="green", icon="home", prefix="glyphicon")
                ).add_to(m)
                counts["shelters"] += 1

    if "💊 Clinics & Pharmacies" in facility_options:
        results = search_nominatim(lat, lon, "pharmacy clinic", city_name)
        time.sleep(1)
        for c in results[:15]:
            clat = float(c.get("lat", 0))
            clon = float(c.get("lon", 0))
            name = c.get("display_name", "Clinic").split(",")[0]
            address = ", ".join(c.get("display_name", "").split(",")[:3])
            if clat and clon:
                folium.Marker(
                    location=[clat, clon],
                    popup=folium.Popup(f"<b>💊 {name}</b><br>📍 {address}", max_width=250),
                    tooltip=f"💊 {name}",
                    icon=folium.Icon(color="orange", icon="heart", prefix="glyphicon")
                ).add_to(m)
                counts["clinics"] += 1

    return m, counts

def show_post_disaster():
    st.title("🟢 Post-Disaster Facilities Finder")
    st.markdown("Locate nearby hospitals and shelters in the affected area")
    st.markdown("---")

    # Initialize session state
    if "post_map" not in st.session_state:
        st.session_state.post_map = None
    if "post_counts" not in st.session_state:
        st.session_state.post_counts = None
    if "post_city_name" not in st.session_state:
        st.session_state.post_city_name = None

    city = st.text_input(
        "🔍 Enter Affected City/Area",
        placeholder="e.g. Mumbai, Chennai, Bengaluru"
    )

    facility_options = st.multiselect(
        "Select Facilities to Find",
        ["🏥 Hospitals", "🏠 Shelters", "💊 Clinics & Pharmacies"],
        default=["🏥 Hospitals", "🏠 Shelters"]
    )

    if st.button("🔍 Find Facilities", type="primary"):
        if not city:
            st.warning("Please enter a city name.")
            return
        if not facility_options:
            st.warning("Please select at least one facility type.")
            return

        with st.spinner("Locating city..."):
            lat, lon, city_name, country = get_coordinates(city)

        if not lat:
            st.error("City not found. Try a different name.")
            return

        st.success(f"📍 Located: {city_name}, {country} ({lat:.4f}, {lon:.4f})")

        with st.spinner("Finding facilities... this takes ~15 seconds"):
            m, counts = build_map(lat, lon, city_name, facility_options)

        # Save to session state so map doesn't disappear on rerun
        st.session_state.post_map = m
        st.session_state.post_counts = counts
        st.session_state.post_city_name = city_name

    # Display map from session state — persists across reruns
    if st.session_state.post_map is not None:
        counts = st.session_state.post_counts
        city_name = st.session_state.post_city_name

        total_found = sum(counts.values())

        col1, col2, col3 = st.columns(3)
        col1.metric("🏥 Hospitals", counts["hospitals"])
        col2.metric("🏠 Shelters", counts["shelters"])
        col3.metric("💊 Clinics", counts["clinics"])

        st.markdown("---")

        lcol1, lcol2, lcol3, lcol4 = st.columns(4)
        lcol1.markdown("🔴 Affected Area")
        lcol2.markdown("🔵 Hospitals")
        lcol3.markdown("🟢 Shelters")
        lcol4.markdown("🟠 Clinics")

        st.subheader(f"🗺️ Facility Map — {city_name}")
        st_folium(
            st.session_state.post_map,
            width=None,
            height=500,
            returned_objects=[]  # prevents rerun trigger
        )

        if total_found == 0:
            st.error("No facilities found. Try Mumbai, Chennai, Bengaluru, Hyderabad or Kolkata.")
        else:
            st.success(f"✅ {total_found} facilities found near {city_name}. Click any marker for details.")