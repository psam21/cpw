"""
Bitcoin OHLC Analysis page.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
from utils.system_logger import debug_log, debug_log_user_action, debug_log_api_call
from utils.data_cache_manager import cached_get_crypto_prices
import requests


def render_bitcoin_ohlc_page():
    """Render the Bitcoin OHLC Analysis page"""
    debug_log_user_action("Viewing Bitcoin OHLC page")
    
    st.header("📈 Bitcoin OHLC Analysis")
    st.info("🔍 Candlestick charts and technical analysis")

    # Time range selector
    col_range, col_refresh = st.columns([3, 1])
    
    with col_range:
        time_range = st.selectbox(
            "📅 Select Time Range",
            options=["1D", "7D", "30D", "90D", "1Y"],
            index=2,  # Default to 30D
            help="Choose the time period for OHLC data"
        )
    
    with col_refresh:
        if st.button("🔄 Refresh Data", type="secondary"):
            # Clear all caches
            get_ohlc_data.clear()
            cached_get_crypto_prices.clear()
            debug_log("🔄 User triggered OHLC data refresh", "INFO", "user_refresh")
            st.rerun()
    
    # Get current price first
    with st.spinner("🔄 Loading current Bitcoin price..."):
        current_data = cached_get_crypto_prices()
        current_price = None
        if current_data and 'bitcoin' in current_data:
            current_price = current_data['bitcoin']['usd']
    
    # Load OHLC data
    with st.spinner(f"🔄 Loading {time_range} OHLC data..."):
        try:
            ohlc_data = get_ohlc_data(time_range)
            
            if ohlc_data is None or ohlc_data.empty:
                st.error("❌ Failed to fetch OHLC data")
                st.stop()
            
            debug_log(f"📈 OHLC data loaded successfully. Records: {len(ohlc_data)}", "SUCCESS", "ohlc_data_loaded")
            
            # === CURRENT PRICE OVERVIEW ===
            _render_current_price_overview(current_price, ohlc_data)
            
            # === MAIN CANDLESTICK CHART ===
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("🕯️ Candlestick Chart")
            _render_candlestick_chart(ohlc_data, time_range)
            
            # === TECHNICAL INDICATORS ===
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("📊 Technical Analysis")
            _render_technical_indicators(ohlc_data)
            
            # === VOLUME ANALYSIS ===
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("📊 Volume Analysis")
            _render_volume_analysis(ohlc_data)
            
            # === PRICE STATISTICS ===
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("📈 Price Statistics")
            _render_price_statistics(ohlc_data, time_range)
            
            # Data source info
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()
            col_time, col_source = st.columns(2)
            with col_time:
                st.caption(f"🕐 Data updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            with col_source:
                st.caption("📡 Source: CoinGecko API")
            
        except Exception as e:
            debug_log(f"❌ Error in OHLC page: {str(e)}", "ERROR", "ohlc_page_error")
            st.error(f"❌ Error loading OHLC data: {str(e)}")


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_ohlc_data(time_range):
    """Fetch OHLC data from CoinGecko API"""
    debug_log_api_call("CoinGecko OHLC", f"Fetching {time_range} data", "STARTING")
    
    # Map time ranges to days
    days_map = {
        "1D": 1,
        "7D": 7,
        "30D": 30,
        "90D": 90,
        "1Y": 365
    }
    
    days = days_map.get(time_range, 30)
    
    try:
        import time
        start_time = time.time()
        
        url = f"https://api.coingecko.com/api/v3/coins/bitcoin/ohlc"
        params = {
            'vs_currency': 'usd',
            'days': days
        }
        
        headers = {
            'accept': 'application/json',
            'User-Agent': 'Bitcoin Dashboard/1.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        response_time = round((time.time() - start_time) * 1000, 2)
        data = response.json()
        
        if not data:
            debug_log("⚠️ Empty OHLC data received", "WARNING", "ohlc_empty")
            debug_log_api_call("CoinGecko OHLC", f"Fetching {time_range} data", "EMPTY", response_time)
            return None
        
        debug_log_api_call("CoinGecko OHLC", f"Fetching {time_range} data", "SUCCESS", response_time, f"{len(data)} data points")
        
        # Convert to DataFrame
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('datetime')
        
        debug_log(f"✅ OHLC data fetched: {len(df)} records", "SUCCESS", "ohlc_success")
        return df
        
    except requests.exceptions.RequestException as e:
        response_time = round((time.time() - start_time) * 1000, 2) if 'start_time' in locals() else 0
        debug_log(f"❌ OHLC API request failed: {str(e)}", "ERROR", "ohlc_api_error")
        debug_log_api_call("CoinGecko OHLC", f"Fetching {time_range} data", "ERROR", response_time, None, str(e))
        return None
    except Exception as e:
        response_time = round((time.time() - start_time) * 1000, 2) if 'start_time' in locals() else 0
        debug_log(f"❌ OHLC data processing error: {str(e)}", "ERROR", "ohlc_processing_error")
        debug_log_api_call("CoinGecko OHLC", f"Fetching {time_range} data", "PROCESSING_ERROR", response_time, None, str(e))
        return None


def _render_current_price_overview(current_price, ohlc_data):
    """Render current price overview with recent changes"""
    st.subheader("💰 Current Price Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if current_price:
            st.metric("💵 Current Price", f"${current_price:,.2f}")
        else:
            st.metric("💵 Current Price", "Loading...")
    
    if not ohlc_data.empty:
        latest = ohlc_data.iloc[-1]
        previous = ohlc_data.iloc[-2] if len(ohlc_data) > 1 else latest
        
        with col2:
            daily_change = latest['close'] - previous['close']
            daily_change_pct = (daily_change / previous['close']) * 100
            delta_color = "normal" if daily_change >= 0 else "inverse"
            st.metric(
                "📈 24h Change", 
                f"${daily_change:+,.2f}",
                delta=f"{daily_change_pct:+.2f}%",
                delta_color=delta_color
            )
        
        with col3:
            period_high = ohlc_data['high'].max()
            st.metric("📊 Period High", f"${period_high:,.2f}")
        
        with col4:
            period_low = ohlc_data['low'].min()
            st.metric("📉 Period Low", f"${period_low:,.2f}")


def _render_candlestick_chart(ohlc_data, time_range):
    """Render the main candlestick chart"""
    if ohlc_data.empty:
        st.warning("⚠️ No OHLC data available for chart")
        return
    
    # Create candlestick chart
    fig = go.Figure()
    
    # Add candlestick trace
    fig.add_trace(go.Candlestick(
        x=ohlc_data['datetime'],
        open=ohlc_data['open'],
        high=ohlc_data['high'],
        low=ohlc_data['low'],
        close=ohlc_data['close'],
        name="Bitcoin OHLC",
        increasing_line_color='#00ff88',
        decreasing_line_color='#ff4444'
    ))
    
    # Add moving averages
    if len(ohlc_data) >= 20:
        ohlc_data['MA20'] = ohlc_data['close'].rolling(window=20).mean()
        fig.add_trace(go.Scatter(
            x=ohlc_data['datetime'],
            y=ohlc_data['MA20'],
            mode='lines',
            name='MA20',
            line=dict(color='orange', width=1),
            opacity=0.8
        ))
    
    if len(ohlc_data) >= 50:
        ohlc_data['MA50'] = ohlc_data['close'].rolling(window=50).mean()
        fig.add_trace(go.Scatter(
            x=ohlc_data['datetime'],
            y=ohlc_data['MA50'],
            mode='lines',
            name='MA50',
            line=dict(color='blue', width=1),
            opacity=0.8
        ))
    
    # Update layout
    fig.update_layout(
        title=f"📈 Bitcoin {time_range} Candlestick Chart with Moving Averages",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        height=600,
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)


def _render_technical_indicators(ohlc_data):
    """Render technical analysis indicators"""
    if ohlc_data.empty:
        st.warning("⚠️ No data available for technical analysis")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # RSI Chart
        st.markdown("#### 📊 RSI (14-period)")
        if len(ohlc_data) >= 14:
            rsi = _calculate_rsi(ohlc_data['close'], 14)
            
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(
                x=ohlc_data['datetime'],
                y=rsi,
                mode='lines',
                name='RSI',
                line=dict(color='purple', width=2)
            ))
            
            # Add RSI levels
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)")
            fig_rsi.add_hline(y=50, line_dash="dot", line_color="gray", annotation_text="Neutral (50)")
            
            fig_rsi.update_layout(
                title="RSI Indicator",
                xaxis_title="Date",
                yaxis_title="RSI",
                height=300,
                template="plotly_dark",
                yaxis=dict(range=[0, 100])
            )
            
            st.plotly_chart(fig_rsi, use_container_width=True)
            
            # Current RSI value
            current_rsi = rsi.iloc[-1] if not rsi.empty else 0
            rsi_status = "Overbought" if current_rsi > 70 else "Oversold" if current_rsi < 30 else "Neutral"
            st.metric("🎯 Current RSI", f"{current_rsi:.1f}", delta=rsi_status)
        else:
            st.warning("⚠️ Insufficient data for RSI calculation")
    
    with col2:
        # MACD Chart
        st.markdown("#### 📈 MACD")
        if len(ohlc_data) >= 26:
            macd_line, signal_line, histogram = _calculate_macd(ohlc_data['close'])
            
            fig_macd = go.Figure()
            
            # MACD Line
            fig_macd.add_trace(go.Scatter(
                x=ohlc_data['datetime'],
                y=macd_line,
                mode='lines',
                name='MACD',
                line=dict(color='blue', width=2)
            ))
            
            # Signal Line
            fig_macd.add_trace(go.Scatter(
                x=ohlc_data['datetime'],
                y=signal_line,
                mode='lines',
                name='Signal',
                line=dict(color='red', width=1)
            ))
            
            # Histogram
            colors = ['green' if h >= 0 else 'red' for h in histogram]
            fig_macd.add_trace(go.Bar(
                x=ohlc_data['datetime'],
                y=histogram,
                name='Histogram',
                marker_color=colors,
                opacity=0.6
            ))
            
            fig_macd.update_layout(
                title="MACD Indicator",
                xaxis_title="Date",
                yaxis_title="MACD",
                height=300,
                template="plotly_dark"
            )
            
            st.plotly_chart(fig_macd, use_container_width=True)
            
            # Current MACD values
            current_macd = macd_line.iloc[-1] if not macd_line.empty else 0
            current_signal = signal_line.iloc[-1] if not signal_line.empty else 0
            macd_status = "Bullish" if current_macd > current_signal else "Bearish"
            st.metric("🎯 MACD Signal", macd_status, delta=f"MACD: {current_macd:.2f}")
        else:
            st.warning("⚠️ Insufficient data for MACD calculation")


def _render_volume_analysis(ohlc_data):
    """Render volume analysis - placeholder since CoinGecko OHLC doesn't include volume"""
    st.info("📊 Volume data not available in CoinGecko OHLC endpoint")
    
    # Alternative: Show price volatility as a proxy for volume/activity
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Price Volatility Analysis")
        if len(ohlc_data) >= 20:
            # Calculate daily volatility (high-low range)
            ohlc_data['daily_range'] = ohlc_data['high'] - ohlc_data['low']
            ohlc_data['volatility_pct'] = (ohlc_data['daily_range'] / ohlc_data['close']) * 100
            
            fig_vol = go.Figure()
            fig_vol.add_trace(go.Bar(
                x=ohlc_data['datetime'],
                y=ohlc_data['volatility_pct'],
                name='Daily Volatility %',
                marker_color='orange'
            ))
            
            fig_vol.update_layout(
                title="Daily Volatility (High-Low Range %)",
                xaxis_title="Date",
                yaxis_title="Volatility %",
                height=300,
                template="plotly_dark"
            )
            
            st.plotly_chart(fig_vol, use_container_width=True)
            
            # Volatility metrics
            avg_volatility = ohlc_data['volatility_pct'].mean()
            recent_volatility = ohlc_data['volatility_pct'].tail(7).mean()
            
            st.metric("📊 Avg Volatility", f"{avg_volatility:.1f}%")
            st.metric("📈 Recent Volatility (7d)", f"{recent_volatility:.1f}%")
    
    with col2:
        st.markdown("#### 🎯 Support & Resistance Levels")
        if not ohlc_data.empty:
            # Calculate potential support and resistance levels
            recent_data = ohlc_data.tail(30)  # Last 30 periods
            
            resistance_level = recent_data['high'].max()
            support_level = recent_data['low'].min()
            current_price = ohlc_data['close'].iloc[-1]
            
            # Calculate distance from levels
            resistance_distance = ((resistance_level - current_price) / current_price) * 100
            support_distance = ((current_price - support_level) / current_price) * 100
            
            st.metric("📈 Resistance Level", f"${resistance_level:,.2f}", 
                     delta=f"{resistance_distance:+.1f}% away")
            st.metric("📉 Support Level", f"${support_level:,.2f}", 
                     delta=f"{support_distance:.1f}% buffer")
            
            # Price position
            price_range = resistance_level - support_level
            price_position = (current_price - support_level) / price_range * 100
            
            st.metric("🎯 Position in Range", f"{price_position:.1f}%")
            
            # Visual range indicator
            st.progress(price_position / 100, text=f"Support ← {price_position:.0f}% → Resistance")


def _render_price_statistics(ohlc_data, time_range):
    """Render comprehensive price statistics"""
    if ohlc_data.empty:
        st.warning("⚠️ No data available for statistics")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("#### 📊 Price Range")
        period_high = ohlc_data['high'].max()
        period_low = ohlc_data['low'].min()
        price_range = period_high - period_low
        range_pct = (price_range / period_low) * 100
        
        st.metric("📈 Period High", f"${period_high:,.2f}")
        st.metric("📉 Period Low", f"${period_low:,.2f}")
        st.metric("📏 Range", f"${price_range:,.2f}")
        st.metric("📊 Range %", f"{range_pct:.1f}%")
    
    with col2:
        st.markdown("#### 📈 Price Changes")
        first_price = ohlc_data['open'].iloc[0]
        last_price = ohlc_data['close'].iloc[-1]
        total_change = last_price - first_price
        total_change_pct = (total_change / first_price) * 100
        
        st.metric("🎯 Starting Price", f"${first_price:,.2f}")
        st.metric("🏁 Ending Price", f"${last_price:,.2f}")
        st.metric("📊 Total Change", f"${total_change:+,.2f}")
        st.metric("📈 Total Change %", f"{total_change_pct:+.1f}%")
    
    with col3:
        st.markdown("#### 📊 Averages")
        avg_price = ohlc_data['close'].mean()
        median_price = ohlc_data['close'].median()
        
        st.metric("📊 Average Price", f"${avg_price:,.2f}")
        st.metric("📊 Median Price", f"${median_price:,.2f}")
        
        # Price vs averages
        current_price = ohlc_data['close'].iloc[-1]
        vs_avg = ((current_price - avg_price) / avg_price) * 100
        vs_median = ((current_price - median_price) / median_price) * 100
        
        st.metric("📈 vs Average", f"{vs_avg:+.1f}%")
        st.metric("📈 vs Median", f"{vs_median:+.1f}%")
    
    with col4:
        st.markdown("#### 📊 Volatility Stats")
        daily_returns = ohlc_data['close'].pct_change().dropna()
        volatility = daily_returns.std() * 100
        
        st.metric("📊 Volatility", f"{volatility:.2f}%")
        
        if len(daily_returns) > 0:
            max_gain = daily_returns.max() * 100
            max_loss = daily_returns.min() * 100
            
            st.metric("📈 Best Day", f"{max_gain:+.1f}%")
            st.metric("📉 Worst Day", f"{max_loss:+.1f}%")
            
            # Positive vs negative days
            positive_days = (daily_returns > 0).sum()
            total_days = len(daily_returns)
            positive_pct = (positive_days / total_days) * 100
            
            st.metric("📈 Positive Days", f"{positive_pct:.0f}%")


def _calculate_rsi(prices, window=14):
    """Calculate RSI indicator"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def _calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD indicator"""
    exp1 = prices.ewm(span=fast).mean()
    exp2 = prices.ewm(span=slow).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=signal).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram
