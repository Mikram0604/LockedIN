import streamlit as st

# Page config — always first line
st.set_page_config(
    page_title="Disaster Response Allocator",
    page_icon="🚨",
    layout="wide"
)

# Title
st.title("🚨 Disaster Response Resource Allocator")
st.markdown("Paste social media posts below to classify emergencies and allocate resources.")

# Test that it works
st.success("App is running!")