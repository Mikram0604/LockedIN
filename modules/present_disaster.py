import streamlit as st
import requests
import os
import google.generativeai as genai
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime, timezone

# Setup Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# ─────────────────────────────────────────────
# MOCK ARTICLES FALLBACK
# ─────────────────────────────────────────────

MOCK_ARTICLES = [
    {
        "title": "Severe flooding reported in Kerala after heavy rainfall",
        "description": "Multiple districts in Kerala are facing severe flooding after 3 days of continuous heavy rainfall. Rescue operations underway.",
        "url": "https://ndtv.com",
        "source": {"name": "NDTV"},
        "publishedAt": datetime.now(timezone.utc).isoformat()
    },
    {
        "title": "Cyclone warning issued for coastal Andhra Pradesh",
        "description": "IMD has issued a red alert for coastal districts as a deep depression in Bay of Bengal intensifies into a cyclone.",
        "url": "https://thehindu.com",
        "source": {"name": "The Hindu"},
        "publishedAt": datetime.now(timezone.utc).isoformat()
    },
    {
        "title": "Forest fire spreads across Uttarakhand hills",
        "description": "Wildfire has engulfed over 500 hectares in Uttarakhand. Fire department and NDRF teams deployed.",
        "url": "https://indianexpress.com",
        "source": {"name": "Indian Express"},
        "publishedAt": datetime.now(timezone.utc).isoformat()
    }
]

# ─────────────────────────────────────────────
# NEWSAPI FUNCTION
# ─────────────────────────────────────────────

def fetch_disaster_news(keyword):
    api_key = os.getenv("NEWS_API_KEY")

    # Split keyword into parts e.g. "Kerala flood" → "Kerala" + "flood"
    parts = keyword.strip().split()
    location = parts[0] if parts else keyword
    disaster = parts[1] if len(parts) > 1 else "disaster"

    # Try 3 progressively broader queries until we get results
    queries = [
        f"{location} {disaster}",
        f"{location} flood OR fire OR cyclone OR earthquake OR disaster OR storm OR emergency",
        f"{location} India news",
    ]

    for query in queries:
        url = (
            f"https://newsapi.org/v2/everything?"
            f"q={query}&sortBy=publishedAt&language=en&pageSize=20&apiKey={api_key}"
        )
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                articles = response.json().get("articles", [])
                if articles:
                    # Filter: at least mention location OR disaster keyword in title/desc
                    filtered = []
                    for a in articles:
                        title = (a.get("title") or "").lower()
                        desc = (a.get("description") or "").lower()
                        combined = title + " " + desc
                        if location.lower() in combined or disaster.lower() in combined:
                            filtered.append(a)

                    if filtered:
                        return filtered

                    # If filter removes everything, return raw results
                    if articles:
                        return articles

        except Exception:
            pass

    # All queries failed — return mock
    st.warning("⚠️ Could not reach NewsAPI — showing sample data for demo.")
    return MOCK_ARTICLES

# ─────────────────────────────────────────────
# LEGITIMACY SCORING
# ─────────────────────────────────────────────

KNOWN_CREDIBLE_SOURCES = [
    "bbc.com", "reuters.com", "apnews.com", "ndtv.com", "thehindu.com",
    "hindustantimes.com", "timesofindia.com", "aljazeera.com", "cnn.com",
    "theguardian.com", "indianexpress.com", "deccanherald.com"
]

def score_source_credibility(source_url):
    if not source_url:
        return 0, "⚠️ Unknown source"
    for credible in KNOWN_CREDIBLE_SOURCES:
        if credible in source_url.lower():
            return 25, "✅ Credible source verified"
    return 10, "⚠️ Unverified source"

def score_timing(published_at):
    try:
        pub_time = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        hours_ago = (now - pub_time).total_seconds() / 3600
        if hours_ago <= 6:
            return 25, f"✅ Very recent: {hours_ago:.1f} hrs ago"
        elif hours_ago <= 24:
            return 15, f"🕐 Published {hours_ago:.1f} hrs ago"
        elif hours_ago <= 72:
            return 8, f"🕐 Published {hours_ago:.1f} hrs ago (older)"
        else:
            return 0, f"❌ Too old: {hours_ago:.1f} hrs ago"
    except:
        return 0, "⚠️ Could not parse publish time"

def score_language_with_gemini(title, description):
    if not title:
        return 0, "⚠️ No content to analyze"
    try:
        content = f"Headline: {title}\nDescription: {description or 'N/A'}"
        prompt = f"""
Analyze this news snippet and rate its legitimacy as a real disaster report on a scale of 0 to 25.
Consider: Is the language factual and urgent? Does it sound like a real incident report?
Does it avoid sensationalism or clickbait?

Respond ONLY in this exact format:
SCORE: <number between 0-25>
REASON: <one sentence explanation>

Content:
{content}
"""
        response = model.generate_content(prompt)
        lines = response.text.strip().split("\n")
        score_line = [l for l in lines if l.startswith("SCORE:")]
        reason_line = [l for l in lines if l.startswith("REASON:")]
        score = int(score_line[0].replace("SCORE:", "").strip()) if score_line else 10
        reason = reason_line[0].replace("REASON:", "").strip() if reason_line else "Analysis complete"
        return min(score, 25), f"🤖 {reason}"
    except:
        return 10, "🤖 AI analysis completed"

def score_corroboration(articles):
    count = len(articles)
    if count >= 7:
        return 25, f"✅ High corroboration: {count} articles found"
    elif count >= 4:
        return 15, f"🔄 Moderate corroboration: {count} articles found"
    elif count >= 2:
        return 8, f"⚠️ Low corroboration: {count} articles found"
    else:
        return 0, f"❌ Very low corroboration: {count} article(s) found"

def calculate_legitimacy(article, all_articles):
    scores = {}
    reasons = {}

    s1, r1 = score_source_credibility(article.get("url", ""))
    scores["Source Credibility"] = s1
    reasons["Source Credibility"] = r1

    s2, r2 = score_timing(article.get("publishedAt", ""))
    scores["Timing"] = s2
    reasons["Timing"] = r2

    s3, r3 = score_language_with_gemini(
        article.get("title", ""),
        article.get("description", "")
    )
    scores["Language Analysis"] = s3
    reasons["Language Analysis"] = r3

    s4, r4 = score_corroboration(all_articles)
    scores["Corroboration"] = s4
    reasons["Corroboration"] = r4

    total = sum(scores.values())
    return total, scores, reasons

# ─────────────────────────────────────────────
# EXIF EXTRACTION
# ─────────────────────────────────────────────

def extract_exif(image_file):
    try:
        img = Image.open(image_file)
        exif_data = img._getexif()
        if not exif_data:
            return None

        metadata = {}
        gps_info = {}

        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == "GPSInfo":
                for gps_tag_id, gps_value in value.items():
                    gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                    gps_info[gps_tag] = gps_value
            elif tag in ["DateTime", "DateTimeOriginal", "Make", "Model"]:
                metadata[tag] = value

        if gps_info:
            def to_degrees(value):
                d, m, s = value
                return float(d) + float(m) / 60 + float(s) / 3600

            lat = to_degrees(gps_info.get("GPSLatitude", [(0,1),(0,1),(0,1)]))
            lon = to_degrees(gps_info.get("GPSLongitude", [(0,1),(0,1),(0,1)]))
            if gps_info.get("GPSLatitudeRef") == "S":
                lat = -lat
            if gps_info.get("GPSLongitudeRef") == "W":
                lon = -lon
            metadata["GPS_Latitude"] = round(lat, 6)
            metadata["GPS_Longitude"] = round(lon, 6)

        return metadata if metadata else None
    except:
        return None

# ─────────────────────────────────────────────
# MAIN UI
# ─────────────────────────────────────────────

def show_present_disaster():
    st.title("🔴 Present Disaster Management")
    st.markdown("Monitor live disaster news and report incidents in real time")
    st.markdown("---")

    tab1, tab2 = st.tabs(["📰 Live News Monitor", "📝 Manual Report"])

    # ── TAB 1: NEWS MONITOR ──────────────────
    with tab1:
        st.subheader("🔍 Search Disaster News")
        st.caption("Tip: Type location + disaster type e.g. 'Kerala flood', 'Mumbai rain', 'Uttarakhand fire'")

        col1, col2 = st.columns([3, 1])
        with col1:
            keyword = st.text_input(
                "Enter location + disaster type",
                placeholder="e.g. Kerala flood, Chennai cyclone, Uttarakhand fire"
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            search_btn = st.button("🔍 Search News", type="primary")

        if search_btn:
            if not keyword:
                st.warning("Please enter a keyword to search.")
            else:
                with st.spinner(f"Searching news for '{keyword}'..."):
                    articles = fetch_disaster_news(keyword)

                if not articles:
                    st.error("No articles found. Try 'Kerala flood' or 'India cyclone'.")
                else:
                    st.success(f"Found {len(articles)} articles. Analyzing top 5...")

                    for i, article in enumerate(articles[:5]):
                        with st.spinner(f"Analyzing article {i+1} of 5..."):
                            total_score, scores, reasons = calculate_legitimacy(article, articles)

                        if total_score >= 70:
                            badge = "🟢 HIGH LEGITIMACY"
                        elif total_score >= 45:
                            badge = "🟡 MEDIUM LEGITIMACY"
                        else:
                            badge = "🔴 LOW LEGITIMACY"

                        title = article.get('title') or 'No title'
                        with st.expander(
                            f"{badge} ({total_score}/100) — {title[:80]}..."
                        ):
                            st.markdown(f"**Source:** {article.get('source', {}).get('name', 'Unknown')}")
                            st.markdown(f"**Published:** {article.get('publishedAt', 'Unknown')}")
                            if article.get("description"):
                                st.markdown(f"**Description:** {article.get('description')}")
                            if article.get("url"):
                                st.markdown(f"[🔗 Read Full Article]({article.get('url')})")

                            st.markdown("#### 📊 Legitimacy Breakdown")
                            lc1, lc2 = st.columns(2)
                            criteria = list(scores.keys())
                            for j, criterion in enumerate(criteria):
                                col = lc1 if j % 2 == 0 else lc2
                                with col:
                                    st.markdown(f"**{criterion}**: {scores[criterion]}/25")
                                    st.progress(scores[criterion] / 25)
                                    st.caption(reasons[criterion])

                            st.markdown(f"### Total Score: **{total_score}/100** — {badge}")

    # ── TAB 2: MANUAL REPORT ─────────────────
    with tab2:
        st.subheader("📝 Report a Disaster Manually")
        st.markdown("Submit an incident report with photo evidence.")

        with st.form("disaster_report_form"):
            reporter_name = st.text_input("Your Name (optional)", placeholder="Anonymous")
            disaster_type = st.selectbox(
                "Type of Disaster",
                ["Flood", "Wildfire", "Cyclone", "Earthquake",
                 "Landslide", "Industrial Accident", "Other"]
            )
            location_text = st.text_input(
                "Location Description",
                placeholder="e.g. Near Powai Lake, Mumbai"
            )
            severity = st.select_slider(
                "Severity Level",
                options=["Low", "Moderate", "High", "Critical"]
            )
            description = st.text_area(
                "Describe the Incident",
                placeholder="What happened? How many people are affected?",
                height=100
            )
            uploaded_image = st.file_uploader(
                "Upload Photo Evidence (optional)",
                type=["jpg", "jpeg", "png"]
            )
            submit = st.form_submit_button("🚨 Submit Report", type="primary")

        if submit:
            if not location_text or not description:
                st.warning("Please fill in Location and Description at minimum.")
            else:
                st.success("✅ Report submitted successfully!")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### 📋 Report Summary")
                    st.markdown(f"**Reporter:** {reporter_name or 'Anonymous'}")
                    st.markdown(f"**Disaster Type:** {disaster_type}")
                    st.markdown(f"**Location:** {location_text}")
                    st.markdown(f"**Severity:** {severity}")
                    st.markdown(f"**Description:** {description}")
                    st.markdown(f"**Submitted At:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                with col2:
                    if uploaded_image:
                        st.markdown("#### 🖼️ Uploaded Image")
                        st.image(uploaded_image, use_column_width=True)

                        st.markdown("#### 📍 Image Metadata (EXIF)")
                        exif = extract_exif(uploaded_image)
                        if exif:
                            for key, value in exif.items():
                                st.markdown(f"**{key}:** {value}")
                            if "GPS_Latitude" in exif and "GPS_Longitude" in exif:
                                st.success(
                                    f"📍 GPS Verified: "
                                    f"{exif['GPS_Latitude']}, {exif['GPS_Longitude']}"
                                )
                        else:
                            st.info("ℹ️ No EXIF metadata found in this image.")
                    else:
                        st.info("No image uploaded.")

                with st.spinner("AI analyzing report..."):
                    try:
                        prompt = f"""
A disaster has been reported:
Type: {disaster_type}
Location: {location_text}
Severity: {severity}
Description: {description}

In 2-3 sentences, give immediate recommended actions for
emergency responders. Be concise and practical.
"""
                        ai_response = model.generate_content(prompt)
                        st.markdown("#### 🤖 AI Recommended Actions")
                        st.info(ai_response.text)
                    except:
                        st.info("AI recommendations unavailable right now.")
