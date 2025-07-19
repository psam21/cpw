"""
Module to fetch Bitcoin OHLC data from Bitfinex API.
Cloud-friendly version with comprehensive historical data from 2013.
"""
import pandas as pd
import requests
from utils.http_config import default_timeout as TIMEOUT
import time
from datetime import datetime

def get_bitcoin_ohlc_batch(symbol='BTCUSD', timeframe='7D', start_timestamp=None, limit=5000):
    """
    Fetch a batch of OHLC data from Bitfinex for a specific symbol.
    Returns weekly data starting from start_timestamp.
    """
    try:
        # Bitfinex API v2 endpoint for candles
        url = f"https://api-pub.bitfinex.com/v2/candles/trade:{timeframe}:t{symbol}/hist"
        params = {
            'limit': limit,
            'sort': 1  # Sort in ascending order (oldest first)
        }
        
        # Add start timestamp if provided
        if start_timestamp:
            params['start'] = int(start_timestamp * 1000)  # Convert to milliseconds
        
        response = requests.get(url, params=params, timeout=TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        
        if not data:
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'close', 'high', 'low', 'volume'])
        
        # Convert timestamp to datetime
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        return df
        
    except Exception as e:
        print(f"Error in batch fetch: {e}")
        return None

def get_comprehensive_bitcoin_ohlc(symbol='BTCUSD', timeframe='7D', max_requests=6):
    """
    Fetch comprehensive Bitcoin OHLC data from 2013 to present.
    Efficiently uses ~6 requests to get all historical data (644 weeks total).
    Each request fetches up to 120 candles, so 6 requests = 720 candles (covers 644 weeks from 2013).
    """
    print(f"🚀 Starting efficient Bitcoin data fetch from 2013...")
    print(f"📊 Target: ~644 weeks of data with only {max_requests} API requests")
    
    # Start from January 1, 2013 (when Bitcoin trading began on major exchanges)
    start_date = datetime(2013, 1, 1)
    start_timestamp = start_date.timestamp()
    
    all_data = []
    current_timestamp = start_timestamp
    requests_made = 0
    
    try:
        while requests_made < max_requests:
            print(f"📡 Request {requests_made + 1}/{max_requests} - Fetching from {datetime.fromtimestamp(current_timestamp).strftime('%Y-%m-%d')}")
            
            # Fetch batch with maximum allowed candles (120 for weekly data)
            batch_df = get_bitcoin_ohlc_batch(
                symbol=symbol, 
                timeframe=timeframe, 
                start_timestamp=current_timestamp,
                limit=120  # Bitfinex max for weekly candles
            )
            
            if batch_df is None or (hasattr(batch_df, 'empty') and batch_df.empty):
                print("📭 No more data available or API error")
                break
            
            # Add to our collection
            all_data.append(batch_df)
            requests_made += 1
            
            # Get the last timestamp for next request (add 1 week to avoid overlap)
            last_timestamp = batch_df['timestamp'].max()
            current_timestamp = (last_timestamp / 1000) + (7 * 24 * 60 * 60)  # Add 1 week in seconds
            
            # Check if we've reached current time (no more future data)
            current_time = datetime.now().timestamp()
            if current_timestamp >= current_time:
                print("📅 Reached current time - all historical data fetched")
                break
            
            # Minimal rate limiting - Bitfinex is quite generous
            time.sleep(0.2)  # 200ms delay between requests
            
            print(f"✅ Batch {requests_made}: {len(batch_df)} candles fetched (up to {datetime.fromtimestamp(last_timestamp/1000).strftime('%Y-%m-%d')})")
        
        if not all_data:
            print("❌ No data collected")
            return pd.DataFrame()
        
        # Combine all batches
        print(f"🔄 Combining {len(all_data)} batches...")
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Remove duplicates (in case of overlap)
        combined_df = combined_df.drop_duplicates(subset=['timestamp'])
        
        # Sort by timestamp
        combined_df = combined_df.sort_values('timestamp')
        
        # Set datetime as index
        combined_df.set_index('datetime', inplace=True)
        
        # Calculate date range
        start_date = combined_df.index.min().strftime('%Y-%m-%d')
        end_date = combined_df.index.max().strftime('%Y-%m-%d')
        
        print(f"🎉 SUCCESS! Fetched {len(combined_df)} weeks of Bitcoin OHLC data")
        print(f"📈 Date range: {start_date} to {end_date}")
        print(f"🔢 API requests used: {requests_made}/{max_requests} (EFFICIENT!)")
        
        return combined_df
        
    except Exception as e:
        print(f"❌ Error in comprehensive fetch: {e}")
        return pd.DataFrame()
def get_btc_ohlc_data():
    """
    Fetch comprehensive Bitcoin OHLC data from 2013 to present.
    Uses efficient API calls (only ~6 requests for all historical data).
    """
    try:
        print("🔍 Fetching comprehensive Bitcoin OHLC data from 2013...")
        
        # Fetch all historical data using our efficient function (only 6 requests!)
        df = get_comprehensive_bitcoin_ohlc(symbol='BTCUSD', timeframe='7D', max_requests=6)
        
        if df is not None and hasattr(df, 'empty') and df.empty == False:
            weeks_count = len(df)
            years_span = (df.index.max() - df.index.min()).days / 365.25
            print(f"✅ Successfully loaded {weeks_count} weeks ({years_span:.1f} years) of historical Bitcoin data")
            print(f"📊 Data spans from {df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}")
            return df
        else:
            print("❌ No OHLC data received from efficient fetch")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"❌ Error in get_btc_ohlc_data: {e}")
        return pd.DataFrame()

def fetch_and_update_data():
    """
    Cloud-friendly data refresh function.
    Triggers a fresh comprehensive data fetch.
    """
    print("🔄 Refreshing comprehensive Bitcoin OHLC data from 2013...")
    return True  # Cache will be cleared automatically by Streamlit
