"""
Data fetching utilities with caching for the Bitcoin dashboard.
"""
import streamlit as st
import time
from datetime import datetime
from utils.debug_logger import debug_log, debug_log_api_call, debug_log_data_processing


@st.cache_data(ttl=300)
def cached_get_mempool_info():
    from mempool_data import get_mempool_info
    return get_mempool_info()


@st.cache_data(ttl=300)
def cached_get_mempool_stats():
    from mempool_data import get_mempool_stats
    return get_mempool_stats()


@st.cache_data(ttl=300)
def cached_get_crypto_prices():
    """
    Fetch crypto prices using multi-exchange fallback system.
    Tries multiple exchanges for maximum Community Cloud reliability.
    """
    start_time = time.time()
    debug_log("Starting multi-exchange price fetch...", "INFO", "price_fetch_start")
    
    try:
        from multi_exchange import get_multi_exchange_prices
        debug_log("Successfully imported multi_exchange module", "SUCCESS", "module_import")
        
        debug_log_api_call("Multi-Exchange", "get_multi_exchange_prices()", "STARTING")
        result = get_multi_exchange_prices()
        
        processing_time = round((time.time() - start_time) * 1000, 2)
        
        debug_log_data_processing("Multi-exchange price aggregation", 
                                  f"Exchanges: {result.get('sources_used', [])}", 
                                  f"Prices: {list(result.get('prices', {}).keys())}", 
                                  processing_time)
        
        # Log detailed results
        debug_log(f"Multi-exchange result received:", "INFO", "price_fetch_result")
        debug_log(f"- Success count: {result.get('success_count', 'MISSING')}", "DATA", "success_metrics")
        debug_log(f"- Total count: {result.get('total_count', 'MISSING')}", "DATA", "total_metrics")
        debug_log(f"- Sources used: {result.get('sources_used', 'MISSING')}", "DATA", "source_metrics")
        debug_log(f"- Errors count: {len(result.get('errors', []))}", "DATA", "error_metrics")
        debug_log(f"- Prices keys: {list(result.get('prices', {}).keys())}", "DATA", "price_keys")
        
        # Log each price individually with validation
        prices = result.get('prices', {})
        for symbol, price in prices.items():
            price_status = "VALID" if price and price > 0 else "INVALID"
            debug_log(f"- {symbol}: {price} (type: {type(price).__name__}, status: {price_status})", 
                     "DATA" if price_status == "VALID" else "WARNING", f"price_{symbol.lower()}")
        
        # Add source information to the result
        if result.get('sources_used'):
            sources_info = f"📡 Data sources: {', '.join(result['sources_used'])}"
            debug_log(sources_info, "SUCCESS", "source_summary")
            
            # Add this info to errors for user visibility
            if 'sources_info' not in result:
                result['sources_info'] = sources_info
        
        debug_log_api_call("Multi-Exchange", "get_multi_exchange_prices()", "SUCCESS", processing_time, 
                          f"Got {len(prices)} prices from {len(result.get('sources_used', []))} sources")
        
        return result
            
    except Exception as e:
        error_msg = f"Critical error in multi-exchange price fetching: {str(e)}"
        debug_log(error_msg, "ERROR")
        debug_log(f"Exception type: {type(e).__name__}", "ERROR")
        debug_log(f"Exception details: {repr(e)}", "ERROR")
        
        # Try to get more details about the import error
        try:
            import multi_exchange
            debug_log("multi_exchange module import successful on retry", "INFO")
        except Exception as import_err:
            debug_log(f"multi_exchange import failed: {import_err}", "ERROR")
        
        return {
            'prices': {'BTC': None, 'ETH': None, 'BNB': None, 'POL': None},
            'errors': [error_msg],
            'success_count': 0,
            'total_count': 4,
            'sources_used': []
        }


# Keep the old function name for backward compatibility
@st.cache_data(ttl=300)
def cached_get_binance_prices():
    """Legacy function name - now uses multi-exchange system"""
    return cached_get_crypto_prices()


@st.cache_data(ttl=300)
def cached_get_btc_ohlc_data():
    from bitfinex_data import get_btc_ohlc_data
    return get_btc_ohlc_data()
