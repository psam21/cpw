"""
A Streamlit application to display cryptocurrency data.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime
# Import API modules
from api.bitfinex_exchange_api import get_btc_ohlc_data, fetch_and_update_data
from api.mempool_network_api import get_mempool_info, get_mempool_stats
from api.binance_exchange_api import get_binance_price

# Import utilities
from utils.system_logger import debug_log, debug_log_api_call, debug_log_data_processing, debug_log_user_action, clear_debug_logs
from utils.data_cache_manager import cached_get_mempool_info, cached_get_mempool_stats, cached_get_crypto_prices, cached_get_binance_prices, cached_get_btc_ohlc_data
from utils.portfolio_session_manager import initialize_portfolio_session, reset_to_default_portfolio, clear_portfolio
from utils.data_validation import is_valid_data  # added unified data validator

# Import page modules
from pages.bitcoin_education import render_why_bitcoin_page
from pages.bitcoin_technical_analysis import render_bitcoin_ohlc_page
from pages.mempool_network_dashboard import render_mempool_page
from pages.portfolio_calculator import render_portfolio_page
from pages.bitcoin_metrics_dashboard import render_bitcoin_metrics_page
from pages.system_debug_viewer import render_debug_logs_page

# Legacy functions have been moved to utils modules

def main():
    """Main function to run the Streamlit app with full session instrumentation."""
    st.set_page_config(
        page_title="Bitcoin Crypto Dashboard",
        page_icon="₿",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize portfolio session state
    initialize_portfolio_session()
    
    # Initialize debug logs storage
    if 'debug_logs' not in st.session_state:
        st.session_state.debug_logs = []
    
    # Initialize debug mode
    if 'debug_mode' not in st.session_state:
        st.session_state.debug_mode = False  # Off by default, use logs tab instead
    
    # Log application startup
    debug_log("🚀 Application startup initiated", "SYSTEM", "app_lifecycle")
    debug_log(f"📱 Page config set: Bitcoin Crypto Dashboard", "INFO", "app_config")
    debug_log(f"🔧 Session state initialized", "INFO", "session_management")
    
    # Add custom CSS for consistent font sizing and styling
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Consistent font sizes */
    h1 { font-size: 2.5rem !important; }
    h2 { font-size: 2rem !important; }
    h3 { font-size: 1.5rem !important; }
    
    /* Custom metric styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .fee-high { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); }
    .fee-medium { background: linear-gradient(135deg, #ffa726 0%, #fb8c00 100%); }
    .fee-low { background: linear-gradient(135deg, #4ecdc4 0%, #26a69a 100%); }
    .fee-economy { background: linear-gradient(135deg, #45b7d1 0%, #2980b9 100%); }
    
    .crypto-btc { background: linear-gradient(135deg, #f7931a 0%, #e67e22 100%); }
    .crypto-eth { background: linear-gradient(135deg, #627eea 0%, #3742fa 100%); }
    .crypto-bnb { background: linear-gradient(135deg, #f3ba2f 0%, #f39c12 100%); }
    .crypto-pol { background: linear-gradient(135deg, #8247e5 0%, #5f27cd 100%); }
    
    /* Better spacing */
    .stMetric > div { margin-bottom: 0.5rem; }
    </style>
    """, unsafe_allow_html=True)

    # Pre-fetch all data at startup with transparent error reporting
    with st.spinner("🔄 Loading cryptocurrency data..."):
        import time
        app_start_time = time.time()
        debug_log("Starting comprehensive data loading process...", "SYSTEM", "data_loading_start")
        
        try:
            debug_log("Clearing price caches...", "INFO", "cache_management")
            
            # Force fresh API calls - clear cache first
            cached_get_crypto_prices.clear()  # Use new function name
            cached_get_binance_prices.clear()  # Clear legacy cache too
            
            debug_log("Caches cleared successfully", "SUCCESS", "cache_management")
            
            # Load mempool data with timing
            mempool_start = time.time()
            debug_log("Loading mempool data...", "INFO", "mempool_loading")
            mempool_data = cached_get_mempool_info()
            mempool_time = int((time.time() - mempool_start) * 1000)
            debug_log_data_processing("Mempool Info", "API Request", mempool_data, mempool_time)
            debug_log(f"Mempool data loaded in {mempool_time}ms", "SUCCESS", "mempool_loading")
            
            # Load mempool stats
            stats_start = time.time()
            debug_log("Loading mempool stats...", "INFO", "stats_loading")
            mempool_stats = cached_get_mempool_stats()
            stats_time = int((time.time() - stats_start) * 1000)
            debug_log_data_processing("Mempool Stats", "API Request", mempool_stats, stats_time)
            debug_log(f"Mempool stats loaded in {stats_time}ms", "SUCCESS", "stats_loading")
            
            # Load crypto prices
            prices_start = time.time()
            debug_log("Loading cryptocurrency prices...", "INFO", "prices_loading")
            crypto_prices = cached_get_crypto_prices()
            prices_time = int((time.time() - prices_start) * 1000)
            debug_log_data_processing("Crypto Prices", "API Request", crypto_prices, prices_time)
            debug_log(f"Crypto prices loaded in {prices_time}ms", "SUCCESS", "prices_loading")
            
            # Load Binance prices (legacy support)
            binance_start = time.time()
            debug_log("Loading Binance prices...", "INFO", "binance_loading")
            binance_prices = cached_get_binance_prices()
            binance_time = int((time.time() - binance_start) * 1000)
            debug_log_data_processing("Binance Prices", "API Request", binance_prices, binance_time)
            debug_log(f"Binance prices loaded in {binance_time}ms", "SUCCESS", "binance_loading")
            
            # Load Bitcoin OHLC data
            ohlc_start = time.time()
            debug_log("Loading Bitcoin OHLC data...", "INFO", "ohlc_loading")
            btc_data = cached_get_btc_ohlc_data()
            ohlc_time = int((time.time() - ohlc_start) * 1000)
            debug_log_data_processing("Bitcoin OHLC", "API Request", btc_data, ohlc_time)
            debug_log(f"Bitcoin OHLC data loaded in {ohlc_time}ms", "SUCCESS", "ohlc_loading")
            
            total_time = int((time.time() - app_start_time) * 1000)
            debug_log(f"✅ All data loaded successfully in {total_time}ms", "SUCCESS", "data_loading_complete")
            debug_log(f"Timing breakdown:", "DATA", "timing_breakdown")
            debug_log(f"- Mempool data: {mempool_time}ms", "DATA", "timing_breakdown")
            debug_log(f"- Mempool stats: {stats_time}ms", "DATA", "timing_breakdown")
            debug_log(f"- Crypto prices: {prices_time}ms", "DATA", "timing_breakdown")
            debug_log(f"- Binance prices: {binance_time}ms", "DATA", "timing_breakdown")
            debug_log(f"- Bitcoin OHLC: {ohlc_time}ms", "DATA", "timing_breakdown")
            debug_log(f"- Total: {total_time}ms", "DATA", "timing_breakdown")
            
            # Log data availability
            debug_log("Data availability check:", "INFO", "data_availability")
            debug_log(f"- Mempool data: {'✅' if is_valid_data(mempool_data) else '❌'}", "INFO", "data_availability")
            debug_log(f"- Mempool stats: {'✅' if is_valid_data(mempool_stats) else '❌'}", "INFO", "data_availability")
            debug_log(f"- Crypto prices: {'✅' if is_valid_data(crypto_prices) else '❌'}", "INFO", "data_availability")
            debug_log(f"- Binance prices: {'✅' if is_valid_data(binance_prices) else '❌'}", "INFO", "data_availability")
            
            # Unified Bitcoin OHLC validity check
            btc_data_valid = is_valid_data(btc_data)
             
            debug_log(f"- Bitcoin OHLC: {'✅' if btc_data_valid else '❌'}", "INFO", "data_availability")
             
            # Data loading success display
            if all([
                is_valid_data(mempool_data),
                is_valid_data(mempool_stats),
                is_valid_data(crypto_prices),
                is_valid_data(binance_prices),
                btc_data_valid
            ]):
                st.success(f"✅ All cryptocurrency data loaded successfully! ({total_time}ms)")
                # Success is logged but not displayed to user (already in debug logs)
            else:
                # Show partial success
                loaded_services = []
                failed_services = []

                if is_valid_data(mempool_data):
                    loaded_services.append("Mempool")
                else:
                    failed_services.append("Mempool")

                if is_valid_data(crypto_prices):
                    loaded_services.append("CoinGecko")
                else:
                    failed_services.append("CoinGecko")

                if is_valid_data(binance_prices):
                    loaded_services.append("Binance")
                else:
                    failed_services.append("Binance")

                if btc_data_valid:
                    loaded_services.append("Bitcoin OHLC")
                else:
                    failed_services.append("Bitcoin OHLC")

                if loaded_services:
                    st.success(f"✅ Loaded: {', '.join(loaded_services)}")

                if failed_services:
                    st.warning(f"⚠️ Failed: {', '.join(failed_services)}")
            
            st.info("💡 Check the 'Debug Logs' tab for detailed error information.")
            
        except ImportError as e:
            debug_log(f"❌ Import error during data loading: {str(e)}", "ERROR", "import_error")
            st.error(f"🔧 Import Error: {str(e)}")
            st.code(f"Raw error: {repr(e)}", language="python")
            st.info("💡 This may be due to missing dependencies. Check the 'Debug Logs' tab for details.")
            mempool_data = {'error': 'Import error'}
            mempool_stats = {'error': 'Import error'}
            binance_prices = {'BTC': None, 'ETH': None, 'BNB': None, 'POL': None}
            btc_data = pd.DataFrame()
            
        except requests.exceptions.RequestException as e:
            debug_log(f"❌ Network error during data loading: {str(e)}", "ERROR", "network_error")
            st.error(f"🌐 Network Error: {str(e)}")
            st.code(f"Raw error: {repr(e)}", language="python")
            st.info("💡 Check your internet connection and try refreshing the page.")
            mempool_data = {'error': 'Network error'}
            mempool_stats = {'error': 'Network error'}
            binance_prices = {'BTC': None, 'ETH': None, 'BNB': None, 'POL': None}
            btc_data = pd.DataFrame()
            
        except Exception as e:
            debug_log(f"❌ Critical error during data loading: {str(e)}", "ERROR", "data_loading_error")
            debug_log(f"Error type: {type(e).__name__}", "ERROR", "error_details")
            debug_log(f"Error details: {repr(e)}", "ERROR", "error_details")
            st.error(f"❌ Critical Error: {str(e)}")
            st.code(f"Error type: {type(e).__name__}\nRaw error: {repr(e)}", language="python")
            st.info("💡 Check the 'Debug Logs' tab for detailed error information.")
            mempool_data = {'error': 'Data unavailable'}
            mempool_stats = {'error': 'Data unavailable'}
            binance_prices = {'BTC': None, 'ETH': None, 'BNB': None, 'POL': None}
            btc_data = pd.DataFrame()

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    tabs = [
        "Why Bitcoin?",
        "Bitcoin OHLC",
        "Mempool Data",
        "Portfolio Value",
        "Bitcoin Metrics",
        "Debug Logs",
    ]
    page = st.sidebar.radio("Go to", tabs)
    
    # Log user navigation
    debug_log_user_action(f"Navigation to '{page}' tab", {'tab_name': page, 'available_tabs': tabs})

    if page == "Why Bitcoin?":
        render_why_bitcoin_page()

    elif page == "Bitcoin OHLC":
        render_bitcoin_ohlc_page()

    elif page == "Mempool Data":
        render_mempool_page()

    elif page == "Portfolio Value":
        render_portfolio_page()

    elif page == "Bitcoin Metrics":
        render_bitcoin_metrics_page()

    elif page == "Debug Logs":
        render_debug_logs_page()


if __name__ == "__main__":
    main()
