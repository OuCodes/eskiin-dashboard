"""
Eskiin Ad Set Testing Dashboard
Interactive visualization for creative testing ad sets reports

Usage:
    streamlit run adset_testing_dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path
import re
from datetime import datetime

# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="Eskiin Ad Set Testing",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# Data Loading & Parsing
# ============================================================================

@st.cache_data(ttl=300)
def parse_adset_report(content):
    """Parse the ad set testing report markdown"""
    data = {
        'metadata': {},
        'summary': {},
        'campaigns': [],
        'all_adsets': [],
        'top_by_roas': [],
        'top_by_spend': []
    }
    
    # Extract metadata
    generated = re.search(r'\*\*Generated:\*\* (.+?)$', content, re.MULTILINE)
    if generated:
        data['metadata']['generated'] = generated.group(1)
    
    period = re.search(r'\*\*Period:\*\* (.+?)$', content, re.MULTILINE)
    if period:
        data['metadata']['period'] = period.group(1)
    
    # Extract summary
    summary_patterns = {
        'total_adsets': r'- \*\*Total Ad Sets:\*\* ([0-9,]+)',
        'total_spend': r'- \*\*Total Spend:\*\* \$([0-9,\.]+)',
        'total_atc': r'- \*\*Total Add to Cart:\*\* ([0-9,]+)',
        'total_ic': r'- \*\*Total Initiate Checkout:\*\* ([0-9,]+)',
        'total_purchases': r'- \*\*Total Purchases:\*\* ([0-9,]+)',
        'total_revenue': r'- \*\*Total Revenue:\*\* \$([0-9,\.]+)',
        'overall_roas': r'- \*\*Overall ROAS:\*\* ([0-9\.]+)x',
        'overall_cost_atc': r'- \*\*Overall Cost per Add to Cart:\*\* \$([0-9,\.]+)',
        'overall_cost_ic': r'- \*\*Overall Cost per Initiate Checkout:\*\* \$([0-9,\.]+)',
        'overall_cost_purchase': r'- \*\*Overall Cost per Purchase:\*\* \$([0-9,\.]+)'
    }
    
    for key, pattern in summary_patterns.items():
        match = re.search(pattern, content)
        if match:
            value = match.group(1).replace(',', '')
            if 'cost' in key or 'roas' in key or 'revenue' in key or 'spend' in key:
                data['summary'][key] = float(value)
            else:
                data['summary'][key] = int(value)
    
    # Parse ad set tables (simplified - extract from markdown tables)
    table_pattern = r'\|\| Ad Set Name \| Status \| Spend \|.+?\n\|\|[-\|]+\n((?:\|\|.+?\n)+)'
    tables = re.finditer(table_pattern, content)
    
    for table in tables:
        rows = table.group(1).strip().split('\n')
        for row in rows:
            parts = [p.strip() for p in row.split('|') if p.strip()]
            if len(parts) >= 10:
                try:
                    adset = {
                        'name': parts[0],
                        'status': parts[1],
                        'spend': float(parts[2].replace('$', '').replace(',', '')),
                        'atc': int(parts[3].replace(',', '')),
                        'cost_atc': float(parts[4].replace('$', '').replace(',', '')),
                        'ic': int(parts[5].replace(',', '')),
                        'cost_ic': float(parts[6].replace('$', '').replace(',', '')),
                        'purchases': int(parts[7].replace(',', '')),
                        'cost_purchase': float(parts[8].replace('$', '').replace(',', '')),
                        'roas': float(parts[9].replace('x', ''))
                    }
                    data['all_adsets'].append(adset)
                except (ValueError, IndexError):
                    continue
    
    return data

# ============================================================================
# Check mode
# ============================================================================

def is_local_mode():
    return Path("data/ads").exists()

# ============================================================================
# Sidebar
# ============================================================================

with st.sidebar:
    st.header("🧪 Ad Set Testing")
    
    local_mode = is_local_mode()
    
    if local_mode:
        st.info("📂 Running in **Local Mode**")
        report_files = list(Path("data/ads").glob("*creative-testing*.md"))
        
        if report_files:
            selected_source = "local_file"
            selected_file = st.selectbox(
                "Select Report",
                options=report_files,
                format_func=lambda x: x.name
            )
        else:
            st.warning("No ad set testing reports found")
            selected_source = None
            selected_file = None
    else:
        st.info("☁️ Running in **Cloud Mode**")
        uploaded_file = st.file_uploader(
            "Upload Ad Set Testing Report (.md)",
            type=['md']
        )
        if uploaded_file:
            selected_source = "upload"
            selected_file = uploaded_file
        else:
            selected_source = None
            selected_file = None
    
    st.markdown("---")
    
    if st.button("🔄 Refresh Data", type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    st.caption(f"⏰ Last updated: {datetime.now().strftime('%H:%M:%S')}")

# ============================================================================
# Load Data
# ============================================================================

if selected_source is None:
    st.warning("⬅️ Please select or upload a report to continue")
    st.stop()

try:
    if selected_source == "upload":
        report_content = selected_file.read().decode('utf-8')
        st.success(f"✅ Loaded uploaded report: **{selected_file.name}**")
    else:
        with open(selected_file, 'r', encoding='utf-8') as f:
            report_content = f.read()
    
    data = parse_adset_report(report_content)
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

st.title("🧪 Eskiin Ad Set Testing Dashboard")

if data['metadata'].get('period'):
    st.markdown(f"**Period:** {data['metadata']['period']}")
if data['metadata'].get('generated'):
    st.markdown(f"**Generated:** {data['metadata']['generated']}")

st.markdown("---")

# ============================================================================
# Summary Metrics
# ============================================================================

st.subheader("📊 Campaign Summary")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Ad Sets",
        f"{data['summary'].get('total_adsets', 0):,}",
        help="Number of ad sets analyzed"
    )

with col2:
    st.metric(
        "Total Spend",
        f"${data['summary'].get('total_spend', 0):,.2f}",
        help="Total spend across all ad sets"
    )

with col3:
    st.metric(
        "Purchases",
        f"{data['summary'].get('total_purchases', 0):,}",
        help="Total purchases from all ad sets"
    )

with col4:
    st.metric(
        "Overall ROAS",
        f"{data['summary'].get('overall_roas', 0):.2f}x",
        help="Return on ad spend"
    )

with col5:
    st.metric(
        "Cost/Purchase",
        f"${data['summary'].get('overall_cost_purchase', 0):.2f}",
        help="Average cost per purchase"
    )

st.markdown("---")

# ============================================================================
# Conversion Funnel
# ============================================================================

st.subheader("🔄 Conversion Funnel")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Add to Cart",
        f"{data['summary'].get('total_atc', 0):,}",
        delta=f"${data['summary'].get('overall_cost_atc', 0):.2f} per add",
        delta_color="inverse"
    )

with col2:
    st.metric(
        "Initiate Checkout",
        f"{data['summary'].get('total_ic', 0):,}",
        delta=f"${data['summary'].get('overall_cost_ic', 0):.2f} per checkout",
        delta_color="inverse"
    )

with col3:
    total_revenue = data['summary'].get('total_revenue', 0)
    st.metric(
        "Total Revenue",
        f"${total_revenue:,.2f}",
        help="Total revenue generated"
    )

# Funnel visualization
funnel_data = pd.DataFrame([
    {'Stage': 'Add to Cart', 'Count': data['summary'].get('total_atc', 0)},
    {'Stage': 'Initiate Checkout', 'Count': data['summary'].get('total_ic', 0)},
    {'Stage': 'Purchases', 'Count': data['summary'].get('total_purchases', 0)},
])

fig_funnel = go.Figure(go.Funnel(
    y=funnel_data['Stage'],
    x=funnel_data['Count'],
    textposition="inside",
    textinfo="value+percent initial",
    marker=dict(color=['#2563EB', '#10B981', '#EF4444']),
    hovertemplate='<b>%{y}</b><br>Count: %{x:,}<extra></extra>'
))

fig_funnel.update_layout(
    title="Conversion Funnel",
    height=350
)

st.plotly_chart(fig_funnel, use_container_width=True)

st.markdown("---")

# ============================================================================
# Ad Set Performance Analysis
# ============================================================================

if data['all_adsets']:
    st.subheader("📈 Ad Set Performance Analysis")
    
    df_adsets = pd.DataFrame(data['all_adsets'])
    
    # Top performers
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🏆 Top 10 by ROAS**")
        top_roas = df_adsets.nlargest(10, 'roas')[['name', 'spend', 'roas', 'purchases']]
        
        fig_roas = go.Figure(go.Bar(
            y=top_roas['name'].apply(lambda x: x[:50] + '...' if len(x) > 50 else x),
            x=top_roas['roas'],
            orientation='h',
            marker_color='#10B981',
            text=top_roas['roas'].apply(lambda x: f'{x:.2f}x'),
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>ROAS: %{x:.2f}x<extra></extra>'
        ))
        
        fig_roas.update_layout(
            height=400,
            xaxis_title="ROAS",
            yaxis={'categoryorder': 'total ascending'}
        )
        
        st.plotly_chart(fig_roas, use_container_width=True)
    
    with col2:
        st.markdown("**💰 Top 10 by Spend**")
        top_spend = df_adsets.nlargest(10, 'spend')[['name', 'spend', 'roas', 'purchases']]
        
        fig_spend = go.Figure(go.Bar(
            y=top_spend['name'].apply(lambda x: x[:50] + '...' if len(x) > 50 else x),
            x=top_spend['spend'],
            orientation='h',
            marker_color='#2563EB',
            text=top_spend['spend'].apply(lambda x: f'${x:,.0f}'),
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Spend: $%{x:,.0f}<extra></extra>'
        ))
        
        fig_spend.update_layout(
            height=400,
            xaxis_title="Spend ($)",
            yaxis={'categoryorder': 'total ascending'}
        )
        
        st.plotly_chart(fig_spend, use_container_width=True)
    
    # Scatter plot: Spend vs ROAS
    st.markdown("### 💡 Spend vs ROAS Analysis")
    
    fig_scatter = go.Figure(go.Scatter(
        x=df_adsets['spend'],
        y=df_adsets['roas'],
        mode='markers',
        marker=dict(
            size=df_adsets['purchases'] * 2,  # Size by purchases
            color=df_adsets['cost_purchase'],
            colorscale='RdYlGn_r',
            showscale=True,
            colorbar=dict(title="Cost/Purchase")
        ),
        text=df_adsets['name'].apply(lambda x: x[:60] + '...' if len(x) > 60 else x),
        hovertemplate='<b>%{text}</b><br>Spend: $%{x:,.0f}<br>ROAS: %{y:.2f}x<extra></extra>'
    ))
    
    fig_scatter.update_layout(
        title="Spend vs ROAS (bubble size = purchases)",
        xaxis_title="Spend ($)",
        yaxis_title="ROAS (x)",
        height=500
    )
    
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Performance table
    st.markdown("### 📋 Detailed Ad Set Performance")
    
    display_df = df_adsets[['name', 'status', 'spend', 'purchases', 'cost_purchase', 'roas', 'atc', 'ic']].copy()
    display_df.columns = ['Ad Set', 'Status', 'Spend', 'Purchases', 'Cost/Purchase', 'ROAS', 'ATC', 'IC']
    display_df['Spend'] = display_df['Spend'].apply(lambda x: f'${x:,.2f}')
    display_df['Cost/Purchase'] = display_df['Cost/Purchase'].apply(lambda x: f'${x:.2f}')
    display_df['ROAS'] = display_df['ROAS'].apply(lambda x: f'{x:.2f}x')
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=600
    )

# ============================================================================
# Footer
# ============================================================================

st.markdown("---")

if data['all_adsets']:
    csv = pd.DataFrame(data['all_adsets']).to_csv(index=False)
    st.download_button(
        label="📥 Download Ad Set Data (CSV)",
        data=csv,
        file_name=f"adset_testing_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

st.caption(
    f"Built with Streamlit {st.__version__} • "
    f"Eskiin Ad Set Testing Analytics • "
    f"Last refresh: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)

