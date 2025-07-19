"""
Multi-exchange API fallback system for cryptocurrency prices.
Tries multiple exchanges in order until successful.
Optimized for Streamlit Community Cloud reliability.
"""

def get_multi_exchange_prices():
    """
    Attempts to fetch prices from multiple exchanges with fallback.
    Priority order: Binance -> KuCoin -> Coinbase -> CoinGecko
    Returns the best available price data.
    """
    import sys
    import os
    
    print("🔍 DEBUG: Starting get_multi_exchange_prices() function")
    print(f"🔍 DEBUG: Python executable: {sys.executable}")
    print(f"🔍 DEBUG: Working directory: {os.getcwd()}")
    print(f"🔍 DEBUG: Python path: {sys.path[:3]}...")  # Show first 3 paths
    
    # Add current directory to path for imports
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
        print(f"✅ DEBUG: Added {current_dir} to sys.path")
    
    results = {
        'prices': {'BTC': None, 'ETH': None, 'BNB': None, 'POL': None},
        'errors': [],
        'success_count': 0,
        'total_count': 4,
        'sources_used': []
    }
    
    print("🔍 DEBUG: Initialized results dictionary")
    
    # Try exchanges in order of preference
    exchanges = [
        ('Binance', try_binance),
        ('KuCoin', try_kucoin),
        ('Coinbase', try_coinbase),
        ('CoinGecko', try_coingecko)
    ]
    
    print(f"🔍 DEBUG: Will try {len(exchanges)} exchanges: {[ex[0] for ex in exchanges]}")
    
    for i, (exchange_name, exchange_func) in enumerate(exchanges):
        print(f"🔄 DEBUG: Trying exchange {i+1}/{len(exchanges)}: {exchange_name}")
        
        try:
            print(f"🔍 DEBUG: Calling {exchange_name} function...")
            exchange_result = exchange_func()
            
            print(f"📊 DEBUG: {exchange_name} returned: {type(exchange_result)}")
            print(f"📊 DEBUG: {exchange_name} success_count: {exchange_result.get('success_count', 'MISSING')}")
            print(f"📊 DEBUG: {exchange_name} prices: {exchange_result.get('prices', {})}")
            
            if exchange_result['success_count'] > 0:
                results['sources_used'].append(exchange_name)
                print(f"✅ DEBUG: {exchange_name} had {exchange_result['success_count']} successful prices")
                
                # Fill in any missing prices
                for symbol in ['BTC', 'ETH', 'BNB', 'POL']:
                    if (results['prices'][symbol] is None and 
                        exchange_result['prices'].get(symbol) is not None):
                        results['prices'][symbol] = exchange_result['prices'][symbol]
                        print(f"✅ DEBUG: Got {symbol} price from {exchange_name}: {exchange_result['prices'][symbol]}")
                
                # Update success count
                results['success_count'] = len([p for p in results['prices'].values() if p is not None])
                print(f"📊 DEBUG: Updated total success_count to: {results['success_count']}")
                
                # If we have all prices, we can stop
                if results['success_count'] == 4:
                    print(f"🎉 DEBUG: All prices obtained! Sources: {', '.join(results['sources_used'])}")
                    break
            else:
                print(f"❌ DEBUG: {exchange_name} had 0 successful prices")
                    
        except Exception as e:
            error_msg = f"❌ {exchange_name} failed: {str(e)}"
            results['errors'].append(error_msg)
            print(f"❌ DEBUG: {error_msg}")
            print(f"📋 DEBUG: Exception type: {type(e)}")
            print(f"📋 DEBUG: Exception details: {repr(e)}")
    
    # Add any remaining errors for missing prices
    for symbol in ['BTC', 'ETH', 'BNB', 'POL']:
        if results['prices'][symbol] is None:
            error_msg = f"❌ {symbol}: All exchanges failed"
            results['errors'].append(error_msg)
            print(f"❌ DEBUG: {error_msg}")
    
    print(f"🏁 DEBUG: Final results - Success: {results['success_count']}/4, Sources: {results['sources_used']}")
    return results

def try_binance():
    """Try to get prices from Binance"""
    print("🔍 DEBUG: Starting try_binance() function")
    
    try:
        print("🔍 DEBUG: Attempting to import binance_data module...")
        from binance_data import get_binance_price
        print("✅ DEBUG: Successfully imported get_binance_price from binance_data")
        
        symbols = [("BTC", "BTCUSDT"), ("ETH", "ETHUSDT"), ("BNB", "BNBUSDT"), ("POL", "POLUSDT")]
        prices = {}
        errors = []
        
        print(f"🔍 DEBUG: Will process {len(symbols)} symbols: {[s[0] for s in symbols]}")
        
        for i, (symbol, pair) in enumerate(symbols):
            print(f"🔍 DEBUG: Processing {i+1}/{len(symbols)}: {symbol} ({pair})")
            try:
                print(f"🔍 DEBUG: Calling get_binance_price('{pair}')...")
                price = get_binance_price(pair)
                print(f"📊 DEBUG: get_binance_price returned: {price} (type: {type(price)})")
                
                if price is not None and price > 0:
                    prices[symbol] = price
                    print(f"✅ DEBUG: Binance {symbol} price accepted: {price}")
                else:
                    prices[symbol] = None
                    error_msg = f"{symbol}: Invalid price returned: {price}"
                    errors.append(error_msg)
                    print(f"❌ DEBUG: Binance {symbol} invalid price: {price}")
                    
            except Exception as e:
                prices[symbol] = None
                error_msg = f"{symbol}: {str(e)}"
                errors.append(error_msg)
                print(f"❌ DEBUG: Binance {symbol} exception: {str(e)} (type: {type(e)})")
        
        result = {
            'prices': prices,
            'errors': errors,
            'success_count': len([p for p in prices.values() if p is not None]),
            'source': 'Binance'
        }
        
        print(f"🏁 DEBUG: Binance result - Success: {result['success_count']}/4")
        print(f"🏁 DEBUG: Binance prices: {prices}")
        print(f"🏁 DEBUG: Binance errors: {errors}")
        
        return result
        
    except ImportError as import_err:
        error_msg = f"Binance module not available: {str(import_err)}"
        print(f"❌ DEBUG: Binance import error: {error_msg}")
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Binance unexpected error: {str(e)}"
        print(f"❌ DEBUG: Binance unexpected error: {error_msg}")
        raise Exception(error_msg)

def try_kucoin():
    """Try to get prices from KuCoin"""
    try:
        from kucoin_data import get_kucoin_prices
        return get_kucoin_prices()
    except ImportError:
        raise Exception("KuCoin module not available")

def try_coinbase():
    """Try to get prices from Coinbase"""
    try:
        from coinbase_data import get_coinbase_prices
        return get_coinbase_prices()
    except ImportError:
        raise Exception("Coinbase module not available")

def try_coingecko():
    """Try to get prices from CoinGecko (free API, no auth required)"""
    import requests
    
    try:
        # CoinGecko free API - very reliable for cloud deployments
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': 'bitcoin,ethereum,binancecoin,polygon',  # CoinGecko IDs
            'vs_currencies': 'usd'
        }
        
        headers = {
            'User-Agent': 'StreamlitApp/1.0',
            'Accept': 'application/json',
            'Connection': 'close'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Map CoinGecko IDs to our symbol names
        price_mapping = {
            'bitcoin': 'BTC',
            'ethereum': 'ETH', 
            'binancecoin': 'BNB',
            'polygon': 'POL'
        }
        
        prices = {}
        errors = []
        
        for coingecko_id, symbol in price_mapping.items():
            if coingecko_id in data and 'usd' in data[coingecko_id]:
                price = float(data[coingecko_id]['usd'])
                if price > 0:
                    prices[symbol] = price
                    print(f"✅ CoinGecko {symbol}: ${price:,.2f}")
                else:
                    prices[symbol] = None
                    errors.append(f"{symbol}: Invalid price {price}")
            else:
                prices[symbol] = None
                errors.append(f"{symbol}: Missing from CoinGecko response")
        
        return {
            'prices': prices,
            'errors': errors,
            'success_count': len([p for p in prices.values() if p is not None]),
            'source': 'CoinGecko'
        }
        
    except Exception as e:
        raise Exception(f"CoinGecko API failed: {str(e)}")

# Test function for the multi-exchange system
def test_all_exchanges():
    """Test all available exchanges and return detailed results"""
    print("🔍 Testing all exchange APIs...")
    
    results = {}
    
    # Test each exchange individually
    exchanges = [
        ('Binance', try_binance),
        ('KuCoin', try_kucoin), 
        ('Coinbase', try_coinbase),
        ('CoinGecko', try_coingecko)
    ]
    
    for exchange_name, exchange_func in exchanges:
        print(f"\n--- Testing {exchange_name} ---")
        try:
            result = exchange_func()
            results[exchange_name] = result
            print(f"✅ {exchange_name}: {result['success_count']}/4 prices successful")
        except Exception as e:
            results[exchange_name] = {'error': str(e)}
            print(f"❌ {exchange_name}: {str(e)}")
    
    # Test the multi-exchange fallback
    print(f"\n--- Testing Multi-Exchange Fallback ---")
    try:
        multi_result = get_multi_exchange_prices()
        results['Multi-Exchange'] = multi_result
        print(f"✅ Multi-Exchange: {multi_result['success_count']}/4 prices successful")
        print(f"Sources used: {', '.join(multi_result['sources_used'])}")
    except Exception as e:
        results['Multi-Exchange'] = {'error': str(e)}
        print(f"❌ Multi-Exchange: {str(e)}")
    
    return results
