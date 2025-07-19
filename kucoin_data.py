"""
Module to fetch data from KuCoin as an alternative to Binance.
KuCoin often has better reliability on cloud platforms.
"""
import requests

def get_kucoin_price(symbol):
    """
    Fetches the latest price for a symbol from KuCoin.
    Symbol format: BTC-USDT, ETH-USDT, BNB-USDT, MATIC-USDT
    Optimized for Streamlit Community Cloud deployment.
    """
    try:
        # KuCoin uses different symbol format (BTC-USDT instead of BTCUSDT)
        url = f"https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={symbol}"
        
        # Cloud-optimized settings
        headers = {
            'User-Agent': 'StreamlitApp/1.0',
            'Accept': 'application/json',
            'Connection': 'close'
        }
        
        response = requests.get(
            url, 
            timeout=5,
            headers=headers
        )
        
        print(f"🌐 KuCoin {symbol} API Response: Status={response.status_code}, Content-Length={len(response.text)}")
        
        response.raise_for_status()
        
        try:
            data = response.json()
        except Exception as json_err:
            raise Exception(f"JSON parse failed - Raw response: {response.text[:100]}")
        
        if data.get('code') != '200000':
            raise Exception(f"KuCoin API error: {data.get('msg', 'Unknown error')}")
            
        if 'data' not in data or not data['data']:
            raise Exception(f"No data in KuCoin API response: {data}")
            
        price_data = data['data']
        if 'price' not in price_data:
            raise Exception(f"Missing 'price' field in KuCoin response: {price_data}")
        
        try:
            price = float(price_data['price'])
        except (ValueError, TypeError) as conv_err:
            raise Exception(f"Price conversion failed - Raw price: '{price_data['price']}' ({type(price_data['price'])})")
        
        if price <= 0:
            raise Exception(f"Invalid price value: {price}")
            
        print(f"✅ KuCoin {symbol}: ${price:,.2f}")
        return price
        
    except requests.exceptions.Timeout:
        raise Exception(f"{symbol} KuCoin API timeout after 5s (cloud limit)")
    except requests.exceptions.ConnectionError:
        raise Exception(f"{symbol} KuCoin network connection failed (cloud connectivity issue)")
    except requests.exceptions.HTTPError as e:
        status_code = getattr(e.response, 'status_code', 'unknown')
        response_text = getattr(e.response, 'text', 'no response text')[:100]
        raise Exception(f"{symbol} KuCoin HTTP error {status_code} - Response: {response_text}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"{symbol} KuCoin request failed: {str(e)}")
    except Exception as e:
        raise Exception(f"{symbol} KuCoin unexpected error: {str(e)}")

def get_kucoin_prices():
    """
    Fetch prices for multiple symbols from KuCoin.
    Returns a dictionary with prices and error information.
    """
    # KuCoin symbol format: BASE-QUOTE
    symbols = [
        ("BTC", "BTC-USDT"), 
        ("ETH", "ETH-USDT"), 
        ("BNB", "BNB-USDT"),  # This is the main reason to use KuCoin
        ("POL", "MATIC-USDT")  # POL is still MATIC on some exchanges
    ]
    
    prices = {}
    errors = []
    
    for symbol, pair in symbols:
        try:
            price = get_kucoin_price(pair)
            prices[symbol] = price
        except Exception as e:
            error_msg = f"❌ {symbol}: KuCoin API failed - {str(e)}"
            errors.append(error_msg)
            print(error_msg)
            prices[symbol] = None
    
    return {
        'prices': prices,
        'errors': errors,
        'success_count': len([p for p in prices.values() if p is not None]),
        'total_count': len(symbols),
        'source': 'KuCoin'
    }

def test_kucoin_api():
    """
    Test KuCoin API endpoints to verify connectivity.
    """
    symbols = ["BTC-USDT", "ETH-USDT", "BNB-USDT", "MATIC-USDT"]
    results = {}
    
    for symbol in symbols:
        try:
            url = f"https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={symbol}"
            response = requests.get(url, timeout=5)
            
            results[symbol] = {
                'status_code': response.status_code,
                'content_length': len(response.text),
                'url': url
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    results[symbol]['api_code'] = data.get('code')
                    results[symbol]['has_data'] = 'data' in data
                    if data.get('data'):
                        results[symbol]['price'] = data['data'].get('price')
                except:
                    results[symbol]['json_error'] = 'Failed to parse JSON'
            
        except Exception as e:
            results[symbol] = {'error': str(e)}
    
    return results
