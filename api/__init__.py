"""
API Module Package

This package contains all cryptocurrency API data fetching modules.
Each module is responsible for interfacing with specific external services.
"""

# Import all API modules for easy access
from .bitcoin_metrics_api import BitcoinMetrics, bitcoin_metrics
from .binance_exchange_api import get_binance_price
from .bitfinex_exchange_api import get_btc_ohlc_data, fetch_and_update_data
from .coinbase_exchange_api import *
from .kucoin_exchange_api import *
from .mempool_network_api import get_mempool_info, get_mempool_stats
from .multi_exchange_aggregator import *

__all__ = [
    'BitcoinMetrics', 'bitcoin_metrics',
    'get_binance_price',
    'get_btc_ohlc_data', 'fetch_and_update_data',
    'get_mempool_info', 'get_mempool_stats'
]
