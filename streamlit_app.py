"""
Eskiin Analytics Dashboard - Home
Main entry point with dashboard selector
"""

import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Eskiin Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# Home Page
# ============================================================================

st.title("📊 Eskiin Analytics Dashboard")
st.markdown("### Choose Your Dashboard")
    
    st.markdown("---")
    
col1, col2 = st.columns(2)

with col1:
    st.markdown("## 🎬 Creative Performance")
    st.markdown("""
    **Best for:**
    - Creative team reports
    - Video performance analysis
    - Top performers with AI insights
    - Location performance tracking
    
    **Metrics:**
    - Executive summary
    - Conversion funnel
    - Hook rates & ROAS
    - Video retention
    """)
    
    if st.button("📊 Open Creative Dashboard", type="primary", use_container_width=True):
        st.switch_page("pages/1_🎬_Creative_Performance.py")

with col2:
    st.markdown("## 🧪 Ad Set Testing")
    st.markdown("""
    **Best for:**
    - Creative testing campaigns
    - Ad set performance comparison
    - Budget optimization
    - ROAS analysis
    
    **Metrics:**
    - Campaign summaries
    - Spend vs ROAS
    - Top performers
    - Conversion funnels
    """)
    
    if st.button("🧪 Open Ad Set Dashboard", type="primary", use_container_width=True):
        st.switch_page("pages/2_🧪_Ad_Set_Testing.py")

st.markdown("---")

# ============================================================================
# Quick Stats (if running locally)
# ============================================================================

if Path("data/ads").exists():
    st.markdown("### 📂 Available Reports (Local Mode)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        creative_reports = list(Path("data/ads").glob("*creative*report*.md"))
        st.metric("Creative Reports", len(creative_reports))
        if creative_reports:
            with st.expander("View files"):
                for f in creative_reports[:5]:
                    st.text(f.name)
    
    with col2:
        adset_reports = list(Path("data/ads").glob("*creative-testing*.md"))
        st.metric("Ad Set Reports", len(adset_reports))
        if adset_reports:
            with st.expander("View files"):
                for f in adset_reports[:5]:
                    st.text(f.name)
else:
    st.info("☁️ **Running in Cloud Mode** - Upload your reports in the dashboards above")

st.markdown("---")

# ============================================================================
# Help Section
# ============================================================================

with st.expander("ℹ️ How to Use"):
    st.markdown("""
    ### Cloud Mode (Streamlit Cloud)
    1. Choose a dashboard above
    2. Upload your report file (.md)
    3. View interactive visualizations
    
    ### Local Mode (Running on your computer)
    - Reports are automatically detected from `data/ads/`
    - Select from dropdown in each dashboard
    
    ### Privacy
    - Your data is never stored on servers
    - All processing happens in your browser session
    - Files uploaded are temporary and deleted after session ends
    """)

st.markdown("---")
st.caption("Built with Streamlit • Eskiin Analytics • v2.0")
