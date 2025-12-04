# 🎬 Eskiin Creative Performance Dashboard

Interactive Streamlit dashboard for visualizing creative performance reports.

## 🚀 Quick Start

### View Online
👉 **[Live Dashboard](https://your-app-url.streamlit.app)** _(coming soon)_

### Run Locally
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 📊 Features

- **Executive Summary** - Total ads, spend, hook rate, videos analyzed
- **Conversion Funnel** - Visual funnel showing drop-off at each stage
- **Top Performers** - Compare cost per purchase, ROAS, hook rate
- **Location Analysis** - Which shooting locations perform best
- **Interactive Charts** - Hover for details, zoom, pan

## 📤 How to Use

### Option 1: Upload Your Report (Recommended)
1. Visit the dashboard URL
2. Click "Upload Report" in the sidebar
3. Upload your creative team report (.md file)
4. Explore interactive visualizations

**Privacy:** Your data is processed in your browser session only. Nothing is stored on the server.

### Option 2: View Demo Data
Select "View Demo" to see sample visualizations with fake data.

### Option 3: Run Locally
If you have the full Eskiin repo with your data:
```bash
cd /path/to/eskiin
streamlit run streamlit_app.py
# Automatically loads from data/ads/ directory
```

## 📋 Report Format

The dashboard expects markdown reports in this format:

```markdown
# 🎬 Eskiin - Creative Performance Report

**Date Range:** Month DD - Month DD, YYYY (XX days)
**Generated:** Month DD, YYYY at HH:MM AM/PM

## 📊 Executive Summary
- **XXXX ads** analyzed
- **$XXX,XXX.XX** total spend
- **XX.X%** hook rate (X,XXX,XXX plays / XX,XXX,XXX impressions)
- **XX videos** analyzed with AI

### 💰 Conversion Performance
- **Content Views:** XX,XXX ($XX.XX per view)
- **Adds to Cart:** X,XXX ($XX.XX per add)
- **Initiate Checkout:** XX,XXX ($XX.XX per checkout)
- **Purchases:** X,XXX ($XXX.XX per purchase)
- **ROAS:** X.XXx

## 🏆 Top Performers Deep Dive
... (see demo-report.md for full example)
```

## 🛠️ Tech Stack

- **[Streamlit](https://streamlit.io/)** - Dashboard framework
- **[Plotly](https://plotly.com/)** - Interactive charts
- **[Pandas](https://pandas.pydata.org/)** - Data manipulation

## 📝 License

MIT License - Feel free to use and modify for your own projects.

## 🔗 Related

This dashboard is part of the [Eskiin](https://github.com/OuCodes/eskiin) marketing analytics toolkit.

