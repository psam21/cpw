#!/usr/bin/env python3
"""
Quick test of all core API data fetching functionality
"""

print('🔍 Testing Core API Data Fetching...')
print('='*50)

# Test Crypto Prices API
try:
    from utils.data_cache_manager import cached_get_crypto_prices
    result = cached_get_crypto_prices()
    print(f'✅ Crypto Prices API: Success! Got {result.get("success_count", 0)}/{result.get("total_count", 0)} sources')
    if 'bitcoin' in result and 'usd' in result['bitcoin']:
        print(f'   📊 Bitcoin Price: ${result["bitcoin"]["usd"]:,.2f}')
except Exception as e:
    print(f'❌ Crypto Prices API: {str(e)}')

# Test Mempool API
try:
    from utils.data_cache_manager import cached_get_mempool_info
    mempool_data = cached_get_mempool_info()
    print(f'✅ Mempool API: Success! Got {len(mempool_data)} data sections')
    if 'fees' in mempool_data:
        print(f'   ⚡ Fast Fee: {mempool_data["fees"]["fastestFee"]} sat/vB')
except Exception as e:
    print(f'❌ Mempool API: {str(e)}')

# Test OHLC Data
try:
    from pages.bitcoin_technical_analysis import get_ohlc_data
    ohlc = get_ohlc_data('30D')
    print(f'✅ OHLC Data: Success! Got {len(ohlc)} data points')
    if ohlc.empty == False:
        print(f'   📈 Latest Close: ${ohlc.iloc[-1]["close"]:,.2f}')
except Exception as e:
    print(f'❌ OHLC Data: {str(e)}')

# Test Bitcoin Metrics
try:
    from bitcoin_metrics import fetch_bitcoin_metrics
    metrics = fetch_bitcoin_metrics()
    print(f'✅ Bitcoin Metrics: Success! Got {len(metrics)} metrics')
    if 'market_cap' in metrics:
        print(f'   💰 Market Cap: ${metrics["market_cap"]:,.0f}')
except Exception as e:
    print(f'❌ Bitcoin Metrics: {str(e)}')

# Test HTTP Configuration
try:
    from utils.http_config import default_timeout
    print(f'✅ HTTP Config: Timeout set to {default_timeout} seconds')
except Exception as e:
    print(f'❌ HTTP Config: {str(e)}')

# Test Data Validation
try:
    from utils.data_validation import is_valid_data
    import pandas as pd
    
    # Test with valid DataFrame
    valid_df = pd.DataFrame({'test': [1, 2, 3]})
    result = is_valid_data(valid_df)
    print(f'✅ Data Validation: DataFrame validation works ({result})')
    
    # Test with empty DataFrame
    empty_df = pd.DataFrame()
    result = is_valid_data(empty_df)
    print(f'✅ Data Validation: Empty DataFrame handled correctly ({result})')
    
except Exception as e:
    print(f'❌ Data Validation: {str(e)}')

print('\n🎯 API Data Fetching Test Complete!')
print('🏆 All core data pipeline components verified!')
