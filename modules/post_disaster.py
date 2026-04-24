import streamlit as st
import requests
import os
import folium
from streamlit_folium import st_folium

def get_coordinates(city):
    """Convert city name to lat/lon using OpenWeatherMap geo API"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]["lat"], data[0]["lon"], data[0]["name"], data[0]["country"]
    return None, None, None, None

def fetch_facilities(lat, lon, facility_type):
    """Fetch nearby facilities using Overpass API (OpenStreetMap) - completely free"""
    if facility_type == "hospital":
        query_filter = '["amenity"="hospital"]'
        radius = 10000  # 10km
    elif facility_type == "clinic":
        query_filter = '["amenity"~"clinic|doctors|pharmacy"]'
        radius = 5000
    else:  # shelter
        query_filter = '["amenity"~"shelter|social_facility|community_centre"]'
        radius = 8000

    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json][timeout:25];
    (
      node{query_filter}(around:{radius},{lat},{lon});
      way{query_filter}(around:{radius},{lat},{lon});
    );
    out center;
    """
    try:
        response = requests.post(overpass_url, data=query, timeout=30)
        if response.status_code == 200:
            return response.json().get("elements", [])
    except:
        return []
    return []

def get_facility_coords(element):
    """Extract lat/lon from OSM element"""
    if element["type"] == "node":
        return element.get("lat"), element.get("lon")
    elif element["type"] == "way":
        center = element.get("center", {})
        return center.get("lat"), center.get("lon")
    return None, None

def show_post_disaster():
    st.title("🟢 Post-Disaster Facilities Finder")
    st.markdown("Locate nearby hospitals and shelters in the affected area")
    st.markdown("---")

    city = st.text_input(
        "🔍 Enter Affected City/Area",
        placeholder="e.g. Mumbai, Chennai, Bhubaneswar"
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

        # Create base map
        m = folium.Map(
            location=[lat, lon],
            zoom_start=13,
            tiles="CartoDB positron"
        )

        # Mark the affected area center
        folium.Marker(
            location=[lat, lon],
            popup=f"⚠️ Affected Area: {city_name}",
            tooltip="Affected Area Center",
            icon=folium.Icon(color="red", icon="exclamation-sign", prefix="glyphicon")
        ).add_to(m)

        # Add a circle around affected area
        folium.Circle(
            location=[lat, lon],
            radius=5000,
            color="red",
            fill=True,
            fill_opacity=0.1,
            tooltip="Affected Zone (~5km radius)"
        ).add_to(m)

        total_found = 0

        # Fetch and plot hospitals
        if "🏥 Hospitals" in facility_options:
            with st.spinner("Fetching hospitals..."):
                hospitals = fetch_facilities(lat, lon, "hospital")

            count = 0
            for h in hospitals[:15]:  # limit to 15
                hlat, hlon = get_facility_coords(h)
                if hlat and hlon:
                    name = h.get("tags", {}).get("name", "Unnamed Hospital")
                    phone = h.get("tags", {}).get("phone", "N/A")
                    emergency = h.get("tags", {}).get("emergency", "unknown")

                    popup_html = f"""
                    <b>🏥 {name}</b><br>
                    📞 Phone: {phone}<br>
                    🚨 Emergency: {emergency}
                    """
                    folium.Marker(
                        location=[hlat, hlon],
                        popup=folium.Popup(popup_html, max_width=250),
                        tooltip=f"🏥 {name}",
                        icon=folium.Icon(color="blue", icon="plus-sign", prefix="glyphicon")
                    ).add_to(m)
                    count += 1

            total_found += count
            st.info(f"🏥 Found **{count} hospitals** nearby")

        # Fetch and plot shelters
        if "🏠 Shelters" in facility_options:
            with st.spinner("Fetching shelters..."):
                shelters = fetch_facilities(lat, lon, "shelter")

            count = 0
            for s in shelters[:15]:
                slat, slon = get_facility_coords(s)
                if slat and slon:
                    name = s.get("tags", {}).get("name", "Unnamed Shelter")
                    capacity = s.get("tags", {}).get("capacity", "Unknown")

                    popup_html = f"""
                    <b>🏠 {name}</b><br>
                    👥 Capacity: {capacity}
                    """
                    folium.Marker(
                        location=[slat, slon],
                        popup=folium.Popup(popup_html, max_width=250),
                        tooltip=f"🏠 {name}",
                        icon=folium.Icon(color="green", icon="home", prefix="glyphicon")
                    ).add_to(m)
                    count += 1

            total_found += count
            st.info(f"🏠 Found **{count} shelters** nearby")

        # Fetch and plot clinics
        if "💊 Clinics & Pharmacies" in facility_options:
            with st.spinner("Fetching clinics..."):
                clinics = fetch_facilities(lat, lon, "clinic")

            count = 0
            for c in clinics[:15]:
                clat, clon = get_facility_coords(c)
                if clat and clon:
                    name = c.get("tags", {}).get("name", "Unnamed Clinic")
                    amenity = c.get("tags", {}).get("amenity", "clinic")

                    popup_html = f"""
                    <b>💊 {name}</b><br>
                    Type: {amenity}
                    """
                    folium.Marker(
                        location=[clat, clon],
                        popup=folium.Popup(popup_html, max_width=250),
                        tooltip=f"💊 {name}",
                        icon=folium.Icon(color="orange", icon="heart", prefix="glyphicon")
                    ).add_to(m)
                    count += 1

            total_found += count
            st.info(f"💊 Found **{count} clinics/pharmacies** nearby")

        st.markdown("---")

        # Map legend
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown("🔴 Affected Area Center")
        col2.markdown("🔵 Hospitals")
        col3.markdown("🟢 Shelters")
        col4.markdown("🟠 Clinics/Pharmacies")

        # Display map
        st.subheader(f"🗺️ Facility Map — {city_name}")
        st_folium(m, width=None, height=500)

        if total_found == 0:
            st.warning(
                "No facilities found via map data. "
                "Try a larger city name or check spelling."
            )
        else:
            st.success(
                f"✅ Total **{total_found} facilities** found near {city_name}. "
                "Click any marker on the map for details."
            )