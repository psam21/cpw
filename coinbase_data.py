"""
Module to fetch data from Coinbase Pro API as an alternative to Binance.
Coinbase often has excellent reliability on cloud platforms.
"""
import requests

def get_coinbase_price(symbol):
    """
    Fetches the latest price for a symbol from Coinbase Pro.
    Symbol format: BTC-USD, ETH-USD, etc.
    Optimized for Streamlit Community Cloud deployment.
    """
    try:
        url = f"https://api.exchange.coinbase.com/products/{symbol}/ticker"
        
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
        
        print(f"🌐 Coinbase {symbol} API Response: Status={response.status_code}, Content-Length={len(response.text)}")
        
        response.raise_for_status()
        
        try:
            data = response.json()
        except Exception as json_err:
            raise Exception(f"JSON parse failed - Raw response: {response.text[:100]}")
        
        if 'price' not in data:
            raise Exception(f"Missing 'price' field in Coinbase response: {data}")
        
        try:
            price = float(data['price'])
        except (ValueError, TypeError) as conv_err:
            raise Exception(f"Price conversion failed - Raw price: '{data['price']}' ({type(data['price'])})")
        
        if price <= 0:
            raise Exception(f"Invalid price value: {price}")
            
        print(f"✅ Coinbase {symbol}: ${price:,.2f}")
        return price
        
    except requests.exceptions.Timeout:
        raise Exception(f"{symbol} Coinbase API timeout after 5s (cloud limit)")
    except requests.exceptions.ConnectionError:
        raise Exception(f"{symbol} Coinbase network connection failed (cloud connectivity issue)")
    except requests.exceptions.HTTPError as e:
        status_code = getattr(e.response, 'status_code', 'unknown')
        response_text = getattr(e.response, 'text', 'no response text')[:100]
        raise Exception(f"{symbol} Coinbase HTTP error {status_code} - Response: {response_text}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"{symbol} Coinbase request failed: {str(e)}")
    except Exception as e:
        raise Exception(f"{symbol} Coinbase unexpected error: {str(e)}")

def get_coinbase_prices():
    """
    Fetch prices for multiple symbols from Coinbase Pro.
    Returns a dictionary with prices and error information.
    Note: Coinbase may not have all tokens (like BNB)
    """
    # Coinbase symbol format: BASE-USD
    symbols = [
        ("BTC", "BTC-USD"), 
        ("ETH", "ETH-USD"),
        # Note: Coinbase doesn't list BNB, so we'll skip it
        ("POL", "MATIC-USD")  # POL might be listed as MATIC
    ]
    
    prices = {}
    errors = []
    
    for symbol, pair in symbols:
        try:
            price = get_coinbase_price(pair)
            prices[symbol] = price
        except Exception as e:
            error_msg = f"❌ {symbol}: Coinbase API failed - {str(e)}"
            errors.append(error_msg)
            print(error_msg)
            prices[symbol] = None
    
    # Coinbase doesn't have BNB, so mark it as unavailable
    prices['BNB'] = None
    errors.append("❌ BNB: Not available on Coinbase")
    
    return {
        'prices': prices,
        'errors': errors,
        'success_count': len([p for p in prices.values() if p is not None]),
        'total_count': 4,  # Still count BNB in total even though unavailable
        'source': 'Coinbase'
    }

def test_coinbase_api():
    """
    Test Coinbase API endpoints to verify connectivity.
    """
    symbols = ["BTC-USD", "ETH-USD", "MATIC-USD"]
    results = {}
    
    for symbol in symbols:
        try:
            url = f"https://api.exchange.coinbase.com/products/{symbol}/ticker"
            response = requests.get(url, timeout=5)
            
            results[symbol] = {
                'status_code': response.status_code,
                'content_length': len(response.text),
                'url': url
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    results[symbol]['has_price'] = 'price' in data
                    results[symbol]['price'] = data.get('price')
                except:
                    results[symbol]['json_error'] = 'Failed to parse JSON'
            
        except Exception as e:
            results[symbol] = {'error': str(e)}
    
    return results
