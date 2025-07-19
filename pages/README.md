# Pages Module

This directory contains all Streamlit page rendering modules for the Bitcoin Crypto Dashboard.

## 📊 Dashboard Pages

Each module renders a specific page of the dashboard with its own functionality:

### Core Dashboard Pages
- **`bitcoin_metrics_dashboard.py`** - Main Bitcoin metrics page with price, market cap, Fear & Greed Index, and comprehensive Bitcoin statistics
- **`bitcoin_technical_analysis.py`** - Advanced technical analysis with OHLC charts, RSI, MACD, Bollinger Bands, and volatility indicators
- **`mempool_network_dashboard.py`** - Bitcoin network monitoring with mempool analysis, fee recommendations, and transaction statistics
- **`portfolio_calculator.py`** - Multi-asset portfolio tracking with performance analytics, profit/loss calculations, and allocation charts

### Utility Pages
- **`system_debug_viewer.py`** - Comprehensive debug interface with API logs, system information, and performance monitoring
- **`bitcoin_education.py`** - Educational content about Bitcoin fundamentals, technology, and investment principles

## 🎯 Page Function Pattern

Each page module follows a consistent pattern:

```python
def render_[page_name]_page():
    """Render the [Page Name] page"""
    # Page implementation
```

## 🔧 Dependencies

All page modules depend on:
- `streamlit` - Core dashboard framework
- `plotly.graph_objects` - Interactive charts and visualizations
- `utils.system_logger` - Logging and debugging
- Various API modules from `/api/` for data fetching

## 📱 Usage

Pages are automatically loaded by the main application (`app.py`) and accessible via the sidebar navigation.
