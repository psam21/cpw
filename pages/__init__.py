"""
Pages Package

This package contains all Streamlit page rendering modules.
Each module is responsible for rendering a specific dashboard page.
"""

# Import all page functions for easy access
from .bitcoin_education import render_why_bitcoin_page
from .bitcoin_technical_analysis import render_bitcoin_ohlc_page
from .mempool_network_dashboard import render_mempool_page
from .portfolio_calculator import render_portfolio_page
from .bitcoin_metrics_dashboard import render_bitcoin_metrics_page
from .system_debug_viewer import render_debug_logs_page

__all__ = [
    'render_why_bitcoin_page',
    'render_bitcoin_ohlc_page', 
    'render_mempool_page',
    'render_portfolio_page',
    'render_bitcoin_metrics_page',
    'render_debug_logs_page'
]