import streamlit as st

# ── Page config (always must be first) ──────────────────────────
st.set_page_config(
    page_title="Disaster Response Allocator",
    page_icon="🚨",
    layout="wide"
)

# ── Title section ────────────────────────────────────────────────
st.title("🚨 Disaster Response Resource Allocator")
st.markdown("AI-powered emergency classification and resource allocation system.")
st.divider()

# ── SIDEBAR ──────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/emoji/96/ambulance-emoji.png", width=60)
    st.title("Control Panel")
    st.divider()

    st.subheader("📊 Resource Status")

    # These are fake numbers for now — we'll make them dynamic later
    st.metric(label="🚑 Ambulances", value="5 available")
    st.metric(label="🚒 Fire Trucks", value="3 available")
    st.metric(label="⛵ Rescue Boats", value="2 available")

    st.divider()

    st.subheader("🔍 Filter Incidents")
    filter_type = st.selectbox(
        "Emergency Type",
        ["All", "Medical", "Fire", "Flood", "Trapped", "Other"]
    )
    filter_severity = st.selectbox(
        "Severity",
        ["All", "Critical", "High", "Medium", "Low"]
    )

    st.divider()
    st.caption("Nexora Hackathon 2026 — Team Project")

# ── MAIN AREA ────────────────────────────────────────────────────

# Split into 2 columns
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📢 Submit Emergency Post")

    # Sample posts button — helps during demo
    if st.button("Load Sample Posts 📋"):
        st.session_state.sample_loaded = True

    # Text input box
    post_input = st.text_area(
        "Paste a social media post here:",
        height=120,
        placeholder='e.g. "Help! We are trapped on 3rd floor in Koramangala, water rising fast!!"',
    )

    # Submit button
    submit = st.button("🚨 Classify & Allocate Resource", type="primary")

    # Show message when submitted
    if submit:
        if post_input.strip() == "":
            st.warning("Please enter a post before submitting!")
        else:
            st.success("Post received! AI is analyzing... (AI connection coming in Step 8)")
            st.info(f"Post: {post_input}")

with col2:
    st.subheader("📋 Incident Log")

    # Placeholder table — will be replaced with real data in Step 12
    st.info("Classified incidents will appear here after submission.")

    # Sample data to show how it'll look
    import pandas as pd
    sample_data = {
        "Post Preview": ["Help trapped in Koramangala...", "Fire near MG Road...", "Medical emergency HSR..."],
        "Type": ["Flood", "Fire", "Medical"],
        "Severity": ["Critical", "High", "High"],
        "Resource Assigned": ["Rescue Boat", "Fire Truck", "Ambulance"],
        "Status": ["🔴 Active", "🔴 Active", "🟡 Responding"]
    }
    df = pd.DataFrame(sample_data)
    st.dataframe(df, use_container_width=True)

# ── BOTTOM SECTION — Map placeholder ─────────────────────────────
st.divider()
st.subheader("🗺️ Incident Map")
st.info("Live map will appear here after Step 11 — once incidents are classified with locations.")