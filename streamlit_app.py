"""
Eskiin Creative Performance Dashboard
Interactive visualization for creative team reports

Usage:
    # Local mode (reads from data/ads/)
    streamlit run creative_dashboard.py
    
    # Cloud mode (file upload or demo)
    Deploy to Streamlit Cloud - users upload their own reports

Deploy to Streamlit Cloud:
    1. Push this file to GitHub (public repo)
    2. Make sure data/ads/ is in .gitignore
    3. Connect repo to Streamlit Cloud
    4. Users can upload reports or view demo data
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path
import re
from datetime import datetime
import io

# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="Eskiin Creative Performance",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# Check if running locally or on Streamlit Cloud
# ============================================================================

def is_local_mode():
    """Check if data directory exists (local mode)"""
    return Path("data/ads").exists()

# ============================================================================
# Sample/Demo Data Generator
# ============================================================================

def generate_demo_report():
    """Generate a demo markdown report for testing"""
    return """# 🎬 Eskiin - Creative Performance Report

**Date Range:** January 1 - March 31, 2024 (90 days)  
**Generated:** April 1, 2024 at 10:00 AM  

---

## 📊 Executive Summary

- **1500 ads** analyzed  
- **$500,000.00** total spend  
- **22.5%** hook rate (3,000,000 plays / 13,333,333 impressions)  
- **20 videos** analyzed with AI  

### 💰 Conversion Performance

- **Content Views:** 25,000 ($20.00 per view)  
- **Adds to Cart:** 8,000 ($62.50 per add)  
- **Initiate Checkout:** 20,000 ($25.00 per checkout)  
- **Purchases:** 5,000 ($100.00 per purchase)  
- **ROAS:** 1.50x  

---

## 🏆 Top Performers Deep Dive

### #1. Lowest Cost Per Purchase: $75.00

**Demo Product Showcase _ VIDEO _ Amazing Results _ LIFESTYLE _ SHOP NOW**

**🔗 Video URL:** [https://www.facebook.com/demo](https://www.facebook.com/demo)  

**📍 Location:** Modern Studio  

**💰 Spend:** $15,000.00  

**🔄 Conversion Funnel:**
- **Content Views:** 800 ($18.75 cost per view)  
- **Add to Cart:** 250 ($60.00 cost per add)  
- **Initiate Checkout:** 600 ($25.00 cost per checkout)  
- **Purchases:** 200 (**$75.00 cost per purchase**)  

**📈 ROAS:** 1.80x  

**🎣 Hook Rate:** 24.0%  

---

### #2. Lowest Cost Per Purchase: $85.00

**Another Great Ad _ VIDEO _ HOOK2 _ Testimonial Style _ Beauty Select**

**🔗 Video URL:** [https://www.facebook.com/demo2](https://www.facebook.com/demo2)  

**📍 Location:** Outdoor Setting  

**💰 Spend:** $17,000.00  

**🔄 Conversion Funnel:**
- **Content Views:** 900 ($18.89 cost per view)  
- **Add to Cart:** 300 ($56.67 cost per add)  
- **Initiate Checkout:** 700 ($24.29 cost per checkout)  
- **Purchases:** 200 (**$85.00 cost per purchase**)  

**📈 ROAS:** 1.65x  

**🎣 Hook Rate:** 23.0%  

---

## 📍 Location Performance Analysis

|| Location | Videos | Purchases | Cost/Purchase | Spend |
||----------|--------|-----------|---------------|-------|
|| Modern Studio | 5 | 800 | $75.00 | $60,000 |
|| Outdoor Setting | 4 | 600 | $85.00 | $51,000 |
|| Home Interior | 3 | 400 | $95.00 | $38,000 |
"""

# ============================================================================
# Data Loading & Parsing
# ============================================================================

@st.cache_data(ttl=300)
def parse_creative_report(content):
    """
    Parse the creative team report markdown content
    Returns: dict with executive summary, top performers, and location data
    """
    data = {
        'metadata': {},
        'executive_summary': {},
        'conversion_metrics': {},
        'top_performers': [],
        'locations': []
    }
    
    # Extract metadata (date range, generated date)
    date_range_match = re.search(r'\*\*Date Range:\*\* (.+?) \((\d+) days\)', content)
    if date_range_match:
        data['metadata']['date_range'] = date_range_match.group(1)
        data['metadata']['days'] = int(date_range_match.group(2))
    
    generated_match = re.search(r'\*\*Generated:\*\* (.+?)$', content, re.MULTILINE)
    if generated_match:
        data['metadata']['generated'] = generated_match.group(1)
    
    # Extract executive summary
    ads_match = re.search(r'- \*\*(\d+) ads\*\* analyzed', content)
    if ads_match:
        data['executive_summary']['total_ads'] = int(ads_match.group(1).replace(',', ''))
    
    spend_match = re.search(r'- \*\*\$([0-9,\.]+)\*\* total spend', content)
    if spend_match:
        data['executive_summary']['total_spend'] = float(spend_match.group(1).replace(',', ''))
    
    hook_match = re.search(r'- \*\*([0-9\.]+)%\*\* hook rate \(([0-9,]+) plays / ([0-9,]+) impressions\)', content)
    if hook_match:
        data['executive_summary']['hook_rate'] = float(hook_match.group(1))
        data['executive_summary']['plays'] = int(hook_match.group(2).replace(',', ''))
        data['executive_summary']['impressions'] = int(hook_match.group(3).replace(',', ''))
    
    videos_match = re.search(r'- \*\*(\d+) videos\*\* analyzed with AI', content)
    if videos_match:
        data['executive_summary']['videos_analyzed'] = int(videos_match.group(1))
    
    # Extract conversion metrics
    conversions_section = re.search(r'### 💰 Conversion Performance\n\n(.+?)\n\n---', content, re.DOTALL)
    if conversions_section:
        conv_text = conversions_section.group(1)
        
        content_views = re.search(r'- \*\*Content Views:\*\* ([0-9,]+) \(\$([0-9,\.]+) per view\)', conv_text)
        if content_views:
            data['conversion_metrics']['content_views'] = int(content_views.group(1).replace(',', ''))
            data['conversion_metrics']['cost_per_content_view'] = float(content_views.group(2).replace(',', ''))
        
        atc = re.search(r'- \*\*Adds to Cart:\*\* ([0-9,]+) \(\$([0-9,\.]+) per add\)', conv_text)
        if atc:
            data['conversion_metrics']['adds_to_cart'] = int(atc.group(1).replace(',', ''))
            data['conversion_metrics']['cost_per_atc'] = float(atc.group(2).replace(',', ''))
        
        checkout = re.search(r'- \*\*Initiate Checkout:\*\* ([0-9,]+) \(\$([0-9,\.]+) per checkout\)', conv_text)
        if checkout:
            data['conversion_metrics']['checkouts'] = int(checkout.group(1).replace(',', ''))
            data['conversion_metrics']['cost_per_checkout'] = float(checkout.group(2).replace(',', ''))
        
        purchases = re.search(r'- \*\*Purchases:\*\* ([0-9,]+) \(\$([0-9,\.]+) per purchase\)', conv_text)
        if purchases:
            data['conversion_metrics']['purchases'] = int(purchases.group(1).replace(',', ''))
            data['conversion_metrics']['cost_per_purchase'] = float(purchases.group(2).replace(',', ''))
        
        roas = re.search(r'- \*\*ROAS:\*\* ([0-9\.]+)x', conv_text)
        if roas:
            data['conversion_metrics']['roas'] = float(roas.group(1))
    
    # Extract top performers
    performer_pattern = re.compile(
        r'### #(\d+)\. Lowest Cost Per Purchase: \$([0-9,\.]+)\n\n'
        r'\*\*(.+?)\*\*\n\n'
        r'.*?\*\*💰 Spend:\*\* \$([0-9,\.]+)\s+\n\n'
        r'\*\*🔄 Conversion Funnel:\*\*\n'
        r'- \*\*Content Views:\*\* ([0-9,]+).*?\n'
        r'- \*\*Add to Cart:\*\* ([0-9,]+).*?\n'
        r'- \*\*Initiate Checkout:\*\* ([0-9,]+).*?\n'
        r'- \*\*Purchases:\*\* ([0-9,]+).*?\n\n'
        r'\*\*📈 ROAS:\*\* ([0-9\.]+)x\s+\n\n'
        r'\*\*🎣 Hook Rate:\*\* ([0-9\.]+)%',
        re.DOTALL
    )
    
    for match in performer_pattern.finditer(content):
        performer = {
            'rank': int(match.group(1)),
            'cost_per_purchase': float(match.group(2).replace(',', '')),
            'name': match.group(3).strip(),
            'spend': float(match.group(4).replace(',', '')),
            'content_views': int(match.group(5).replace(',', '')),
            'adds_to_cart': int(match.group(6).replace(',', '')),
            'checkouts': int(match.group(7).replace(',', '')),
            'purchases': int(match.group(8).replace(',', '')),
            'roas': float(match.group(9)),
            'hook_rate': float(match.group(10))
        }
        data['top_performers'].append(performer)
    
    # Extract location performance
    location_section = re.search(
        r'\|\| Location \| Videos \| Purchases \| Cost/Purchase \| Spend \|\n'
        r'\|\|----------|--------|-----------|---------------|-------\|\n'
        r'((?:\|\|.+?\|\n)+)',
        content
    )
    
    if location_section:
        location_rows = location_section.group(1).strip().split('\n')
        for row in location_rows:
            parts = [p.strip() for p in row.split('|') if p.strip()]
            if len(parts) >= 5:
                try:
                    data['locations'].append({
                        'location': parts[0],
                        'videos': int(parts[1]),
                        'purchases': int(parts[2]),
                        'cost_per_purchase': float(parts[3].replace('$', '').replace(',', '')),
                        'spend': float(parts[4].replace('$', '').replace(',', ''))
                    })
                except ValueError:
                    continue
    
    return data

# ============================================================================
# Sidebar
# ============================================================================

with st.sidebar:
    st.header("🎬 Creative Report")
    
    # Determine mode
    local_mode = is_local_mode()
    
    if local_mode:
        st.info("📂 Running in **Local Mode**")
        
        # File selector for local files
        report_files = list(Path("data/ads").glob("*creative*report*.md"))
        
        if report_files:
            selected_source = "local_file"
            selected_file = st.selectbox(
                "Select Report",
                options=report_files,
                format_func=lambda x: x.name
            )
        else:
            st.warning("No creative reports found in data/ads/")
            selected_source = "demo"
            selected_file = None
    else:
        st.info("☁️ Running in **Cloud Mode**")
        
        # Mode selector for cloud
        mode = st.radio(
            "Data Source",
            options=["Upload Report", "View Demo"],
            help="Upload your own report or view demo data"
        )
        
        if mode == "Upload Report":
            uploaded_file = st.file_uploader(
                "Upload Creative Report (.md)",
                type=['md'],
                help="Upload your Eskiin creative team report markdown file"
            )
            
            if uploaded_file:
                selected_source = "upload"
                selected_file = uploaded_file
            else:
                st.warning("👆 Please upload a report to continue")
                selected_source = None
                selected_file = None
        else:
            selected_source = "demo"
            selected_file = None
    
    st.markdown("---")
    
    # Refresh button
    if st.button("🔄 Refresh Data", type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    
    # Mode-specific help
    if not local_mode:
        with st.expander("ℹ️ How to Use"):
            st.markdown("""
            **Upload Mode:**
            1. Generate your creative report
            2. Upload the .md file above
            3. View interactive visualizations
            
            **Demo Mode:**
            - See sample visualizations
            - Understand the format
            - Test the dashboard
            
            **Privacy:**
            - Your data stays private
            - Files are not stored
            - Processing happens in your browser session
            """)
    
    st.caption(f"⏰ Last updated: {datetime.now().strftime('%H:%M:%S')}")

# ============================================================================
# Load Data
# ============================================================================

if selected_source is None:
    st.warning("⬅️ Please select a data source from the sidebar to continue")
    st.stop()

try:
    if selected_source == "demo":
        # Load demo data
        report_content = generate_demo_report()
        st.info("📊 Viewing **Demo Data** - Upload your own report for real insights!")
    elif selected_source == "upload":
        # Read uploaded file
        report_content = selected_file.read().decode('utf-8')
        st.success(f"✅ Loaded uploaded report: **{selected_file.name}**")
    else:  # local_file
        # Read local file
        with open(selected_file, 'r', encoding='utf-8') as f:
            report_content = f.read()
    
    data = parse_creative_report(report_content)
    data_loaded = True
    
except Exception as e:
    st.error(f"❌ Error loading report: {e}")
    with st.expander("Show error details"):
        st.exception(e)
    data_loaded = False

if not data_loaded:
    st.stop()

# ============================================================================
# Header
# ============================================================================

st.title("🎬 Eskiin Creative Performance Dashboard")

if data['metadata'].get('date_range'):
    st.markdown(f"**Date Range:** {data['metadata']['date_range']}")
if data['metadata'].get('generated'):
    st.markdown(f"**Report Generated:** {data['metadata']['generated']}")

st.markdown("---")

# ============================================================================
# Executive Summary Metrics
# ============================================================================

st.subheader("📊 Executive Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Ads",
        f"{data['executive_summary'].get('total_ads', 0):,}",
        help="Total number of ads analyzed"
    )

with col2:
    st.metric(
        "Total Spend",
        f"${data['executive_summary'].get('total_spend', 0):,.2f}",
        help="Total ad spend for the period"
    )

with col3:
    st.metric(
        "Hook Rate",
        f"{data['executive_summary'].get('hook_rate', 0):.1f}%",
        help="Percentage of impressions that resulted in plays"
    )

with col4:
    st.metric(
        "Videos Analyzed",
        f"{data['executive_summary'].get('videos_analyzed', 0):,}",
        help="Number of videos with AI analysis"
    )

st.markdown("---")

# ============================================================================
# Conversion Funnel Metrics
# ============================================================================

st.subheader("💰 Conversion Performance")

col1, col2, col3, col4, col5 = st.columns(5)

conv = data['conversion_metrics']

with col1:
    st.metric(
        "Content Views",
        f"{conv.get('content_views', 0):,}",
        delta=f"${conv.get('cost_per_content_view', 0):.2f} per view",
        delta_color="inverse"
    )

with col2:
    st.metric(
        "Add to Cart",
        f"{conv.get('adds_to_cart', 0):,}",
        delta=f"${conv.get('cost_per_atc', 0):.2f} per add",
        delta_color="inverse"
    )

with col3:
    st.metric(
        "Checkouts",
        f"{conv.get('checkouts', 0):,}",
        delta=f"${conv.get('cost_per_checkout', 0):.2f} per checkout",
        delta_color="inverse"
    )

with col4:
    st.metric(
        "Purchases",
        f"{conv.get('purchases', 0):,}",
        delta=f"${conv.get('cost_per_purchase', 0):.2f} per purchase",
        delta_color="inverse"
    )

with col5:
    st.metric(
        "ROAS",
        f"{conv.get('roas', 0):.2f}x",
        help="Return on Ad Spend"
    )

# ============================================================================
# Conversion Funnel Visualization
# ============================================================================

st.markdown("---")
st.subheader("🔄 Conversion Funnel")

if conv:
    funnel_data = pd.DataFrame([
        {'Stage': 'Content Views', 'Count': conv.get('content_views', 0), 'Cost': conv.get('cost_per_content_view', 0)},
        {'Stage': 'Add to Cart', 'Count': conv.get('adds_to_cart', 0), 'Cost': conv.get('cost_per_atc', 0)},
        {'Stage': 'Checkouts', 'Count': conv.get('checkouts', 0), 'Cost': conv.get('cost_per_checkout', 0)},
        {'Stage': 'Purchases', 'Count': conv.get('purchases', 0), 'Cost': conv.get('cost_per_purchase', 0)},
    ])
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        # Funnel chart
        fig_funnel = go.Figure(go.Funnel(
            y=funnel_data['Stage'],
            x=funnel_data['Count'],
            textposition="inside",
            textinfo="value+percent initial",
            marker=dict(
                color=['#2563EB', '#10B981', '#F59E0B', '#EF4444']
            ),
            hovertemplate='<b>%{y}</b><br>Count: %{x:,}<br>%{percentInitial}<extra></extra>'
        ))
        
        fig_funnel.update_layout(
            title="Conversion Funnel Volume",
            height=400
        )
        
        st.plotly_chart(fig_funnel, use_container_width=True)
    
    with col_right:
        # Cost per stage
        fig_cost = go.Figure(go.Bar(
            x=funnel_data['Stage'],
            y=funnel_data['Cost'],
            marker_color=['#2563EB', '#10B981', '#F59E0B', '#EF4444'],
            text=funnel_data['Cost'].apply(lambda x: f'${x:.2f}'),
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Cost: $%{y:.2f}<extra></extra>'
        ))
        
        fig_cost.update_layout(
            title="Cost Per Conversion Stage",
            yaxis_title="Cost ($)",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig_cost, use_container_width=True)

# ============================================================================
# Top Performers Analysis
# ============================================================================

st.markdown("---")
st.subheader("🏆 Top Performers")

if data['top_performers']:
    # Top performers dataframe
    performers_df = pd.DataFrame(data['top_performers'])
    
    # Display top 5 comparison
    top_5 = performers_df.head(5)
    
    # Metrics comparison
    col1, col2 = st.columns(2)
    
    with col1:
        # Cost per purchase comparison
        fig_cpp = go.Figure(go.Bar(
            x=top_5['name'].apply(lambda x: x[:40] + '...' if len(x) > 40 else x),
            y=top_5['cost_per_purchase'],
            marker_color='#2563EB',
            text=top_5['cost_per_purchase'].apply(lambda x: f'${x:.2f}'),
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Cost per Purchase: $%{y:.2f}<extra></extra>'
        ))
        
        fig_cpp.update_layout(
            title="Cost Per Purchase - Top 5",
            yaxis_title="Cost ($)",
            height=400,
            xaxis_tickangle=-45
        )
        
        st.plotly_chart(fig_cpp, use_container_width=True)
    
    with col2:
        # ROAS comparison
        fig_roas = go.Figure(go.Bar(
            x=top_5['name'].apply(lambda x: x[:40] + '...' if len(x) > 40 else x),
            y=top_5['roas'],
            marker_color='#10B981',
            text=top_5['roas'].apply(lambda x: f'{x:.2f}x'),
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>ROAS: %{y:.2f}x<extra></extra>'
        ))
        
        fig_roas.update_layout(
            title="ROAS - Top 5",
            yaxis_title="ROAS (x)",
            height=400,
            xaxis_tickangle=-45
        )
        
        st.plotly_chart(fig_roas, use_container_width=True)
    
    # Hook rate vs ROAS scatter
    st.markdown("### Hook Rate vs ROAS")
    
    fig_scatter = go.Figure(go.Scatter(
        x=performers_df['hook_rate'],
        y=performers_df['roas'],
        mode='markers',
        marker=dict(
            size=performers_df['spend'] / 1000,  # Size by spend
            color=performers_df['cost_per_purchase'],
            colorscale='RdYlGn_r',
            showscale=True,
            colorbar=dict(title="Cost/Purchase")
        ),
        text=performers_df['name'].apply(lambda x: x[:50] + '...' if len(x) > 50 else x),
        hovertemplate='<b>%{text}</b><br>Hook Rate: %{x:.1f}%<br>ROAS: %{y:.2f}x<extra></extra>'
    ))
    
    fig_scatter.update_layout(
        title="Hook Rate vs ROAS (bubble size = spend)",
        xaxis_title="Hook Rate (%)",
        yaxis_title="ROAS (x)",
        height=500
    )
    
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Detailed table
    st.markdown("### Detailed Performance Table")
    
    display_df = performers_df[['rank', 'name', 'spend', 'purchases', 'cost_per_purchase', 'roas', 'hook_rate']].copy()
    display_df.columns = ['Rank', 'Ad Name', 'Spend', 'Purchases', 'Cost/Purchase', 'ROAS', 'Hook Rate']
    display_df['Spend'] = display_df['Spend'].apply(lambda x: f'${x:,.2f}')
    display_df['Cost/Purchase'] = display_df['Cost/Purchase'].apply(lambda x: f'${x:.2f}')
    display_df['ROAS'] = display_df['ROAS'].apply(lambda x: f'{x:.2f}x')
    display_df['Hook Rate'] = display_df['Hook Rate'].apply(lambda x: f'{x:.1f}%')
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=400
    )

# ============================================================================
# Location Performance
# ============================================================================

if data['locations']:
    st.markdown("---")
    st.subheader("📍 Location Performance")
    
    locations_df = pd.DataFrame(data['locations'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Purchases by location
        fig_loc_purchases = go.Figure(go.Bar(
            x=locations_df['location'],
            y=locations_df['purchases'],
            marker_color='#7C3AED',
            text=locations_df['purchases'],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Purchases: %{y:,}<extra></extra>'
        ))
        
        fig_loc_purchases.update_layout(
            title="Purchases by Location",
            yaxis_title="Purchases",
            height=400,
            xaxis_tickangle=-45
        )
        
        st.plotly_chart(fig_loc_purchases, use_container_width=True)
    
    with col2:
        # Cost per purchase by location
        fig_loc_cpp = go.Figure(go.Bar(
            x=locations_df['location'],
            y=locations_df['cost_per_purchase'],
            marker_color='#F59E0B',
            text=locations_df['cost_per_purchase'].apply(lambda x: f'${x:.2f}'),
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Cost/Purchase: $%{y:.2f}<extra></extra>'
        ))
        
        fig_loc_cpp.update_layout(
            title="Cost Per Purchase by Location",
            yaxis_title="Cost ($)",
            height=400,
            xaxis_tickangle=-45
        )
        
        st.plotly_chart(fig_loc_cpp, use_container_width=True)
    
    # Best location callout
    best_location = locations_df.loc[locations_df['cost_per_purchase'].idxmin()]
    
    st.success(
        f"🎯 **Winner:** {best_location['location']} delivers the best ROI at "
        f"${best_location['cost_per_purchase']:.2f} per purchase!"
    )

# ============================================================================
# Footer
# ============================================================================

st.markdown("---")

# Add download button for the report data
if data['top_performers']:
    performers_csv = pd.DataFrame(data['top_performers']).to_csv(index=False)
    st.download_button(
        label="📥 Download Performance Data (CSV)",
        data=performers_csv,
        file_name=f"creative_performance_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

st.caption(
    f"Built with Streamlit {st.__version__} • "
    f"Eskiin Creative Analytics • "
    f"Last refresh: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)
