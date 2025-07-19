"""
Bitcoin Metrics Dashboard page.
"""
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
from utils.system_logger import debug_log, debug_log_user_action


def render_bitcoin_metrics_page():
    """Render the Bitcoin Metrics Dashboard page"""
    debug_log_user_action("Viewing Bitcoin Metrics page")
    
    st.header("📊 Bitcoin Metrics Dashboard")
    
    # Add cache for metrics with 5-minute TTL
    @st.cache_data(ttl=300)
    def cached_get_bitcoin_metrics():
        debug_log("🚀 Initializing Bitcoin Metrics with enhanced logging...", "INFO", "bitcoin_metrics_init")
        
        from api.bitcoin_metrics_api import BitcoinMetrics
        # Create instance with debug logging
        btc_metrics = BitcoinMetrics(debug_logger=debug_log)
        
        debug_log("📊 Starting comprehensive Bitcoin metrics collection...", "INFO", "bitcoin_metrics_start")
        return btc_metrics.get_comprehensive_metrics()
    
    # Refresh button
    col_refresh, col_status = st.columns([1, 3])
    with col_refresh:
        if st.button("🔄 Refresh Metrics", type="secondary"):
            cached_get_bitcoin_metrics.clear()
            st.rerun()
    
    # Load metrics with spinner
    with st.spinner("🔄 Loading comprehensive Bitcoin metrics..."):
        try:
            metrics = cached_get_bitcoin_metrics()
            
            with col_status:
                if len(metrics.get('errors', [])) == 0:
                    st.success("✅ All metrics loaded successfully")
                elif len(metrics.get('errors', [])) < 5:
                    st.warning(f"⚠️ {len(metrics['errors'])} metrics failed to load")
                else:
                    st.error(f"❌ Multiple metrics failed ({len(metrics['errors'])} errors)")
            
            # Show errors in expander if any
            if metrics.get('errors'):
                with st.expander(f"🔍 View {len(metrics['errors'])} API Issues"):
                    for error in metrics['errors']:
                        st.error(error)
            
            # === SECTION 1: PRICE & MARKET DATA ===
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("💰 Price & Market Data")
            
            price_col1, price_col2, price_col3, price_col4 = st.columns(4)
            
            # Bitcoin Price (Multi-source)
            with price_col1:
                coingecko = metrics.get('coingecko', {})
                coindesk = metrics.get('coindesk_price', {})
                
                if coingecko.get('price_usd'):
                    price = coingecko['price_usd']
                    change_24h = coingecko.get('change_24h', 0)
                    delta_color = "normal" if change_24h >= 0 else "inverse"
                    st.metric(
                        "💵 Bitcoin Price (USD)", 
                        f"${price:,.2f}",
                        delta=f"{change_24h:+.2f}% (24h)",
                        delta_color=delta_color
                    )
                elif coindesk.get('price_usd'):
                    st.metric("💵 Bitcoin Price (USD)", f"${coindesk['price_usd']:,.2f}")
                else:
                    st.metric("💵 Bitcoin Price (USD)", "API Failed")
            
            # Market Cap
            with price_col2:
                if coingecko.get('market_cap_usd'):
                    market_cap = coingecko['market_cap_usd']
                    market_cap_t = market_cap / 1e12
                    st.metric("🏛️ Market Cap", f"${market_cap_t:.2f}T")
                else:
                    st.metric("🏛️ Market Cap", "API Failed")
            
            # 24h Volume
            with price_col3:
                if coingecko.get('volume_24h'):
                    volume = coingecko['volume_24h']
                    volume_b = volume / 1e9
                    st.metric("📊 24h Volume", f"${volume_b:.1f}B")
                else:
                    st.metric("📊 24h Volume", "API Failed")
            
            # Bitcoin Dominance
            with price_col4:
                global_data = metrics.get('global', {})
                if global_data.get('btc_dominance'):
                    dominance = global_data['btc_dominance']
                    st.metric("👑 BTC Dominance", f"{dominance:.1f}%")
                else:
                    st.metric("👑 BTC Dominance", "API Failed")
            
            # Multi-currency prices with minimal spacing
            st.subheader("🌍 Global Prices")
            curr_col1, curr_col2, curr_col3, curr_col4 = st.columns(4)
            
            with curr_col1:
                if coingecko.get('price_usd'):
                    st.metric("🇺🇸 USD", f"${coingecko['price_usd']:,.2f}")
                else:
                    st.metric("🇺🇸 USD", "N/A")
            
            with curr_col2:
                if coingecko.get('price_eur'):
                    st.metric("🇪🇺 EUR", f"€{coingecko['price_eur']:,.2f}")
                else:
                    st.metric("🇪🇺 EUR", "N/A")
            
            with curr_col3:
                if coingecko.get('price_gbp'):
                    st.metric("🇬🇧 GBP", f"£{coingecko['price_gbp']:,.2f}")
                else:
                    st.metric("🇬🇧 GBP", "N/A")
            
            with curr_col4:
                if coingecko.get('price_inr'):
                    st.metric("🇮🇳 INR", f"₹{coingecko['price_inr']:,.0f}")
                else:
                    st.metric("🇮🇳 INR", "N/A")
            
            # === SECTION 2: FEAR & GREED + SUPPLY METRICS ===
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("📈 Market Sentiment & Supply")
            
            _render_fear_greed_section(metrics)
            
            # === SECTION 3: NETWORK ACTIVITY CHARTS ===
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("🌐 Network Activity")
            
            _render_network_activity_charts(metrics)
            
            # === SECTION 4: NETWORK HEALTH ===
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("🌐 Network Health")
            
            _render_network_health_section(metrics)
            
            # Show data freshness with minimal spacing
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()
            col_time, col_sources = st.columns(2)
            with col_time:
                st.caption(f"🕐 Data refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            with col_sources:
                st.caption("📡 Sources: CoinGecko, Blockchain.info, Alternative.me, Bitnodes")
            
        except Exception as e:
            st.error(f"❌ Failed to load Bitcoin metrics: {str(e)}")
            st.code(f"Error type: {type(e).__name__}\nRaw error: {repr(e)}", language="python")
            st.info("🔄 Please try refreshing the page or check your internet connection.")
            st.info("💡 Check Debug Logs for detailed API failure information")


def _render_fear_greed_section(metrics):
    """Render the Fear & Greed and Supply metrics section"""
    fear_col1, fear_col2, fear_col3 = st.columns(3)
    
    # Fear & Greed Index with Gauge Meter
    with fear_col1:
        fng_data = metrics.get('fear_greed', {})
        if fng_data.get('value') is not None:
            fng_value = fng_data['value']
            fng_class = fng_data.get('classification', 'Unknown')
            
            # Create gauge meter
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=fng_value,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "🎯 Fear & Greed Index", 'font': {'size': 16}},
                delta={'reference': 50, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
                gauge={
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': "darkblue"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 20], 'color': '#ff4444'},      # Extreme Fear - Red
                        {'range': [20, 40], 'color': '#ff8800'},     # Fear - Orange  
                        {'range': [40, 60], 'color': '#ffdd00'},     # Neutral - Yellow
                        {'range': [60, 80], 'color': '#88dd00'},     # Greed - Light Green
                        {'range': [80, 100], 'color': '#00dd44'}     # Extreme Greed - Green
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            
            fig_gauge.update_layout(
                height=200,
                margin=dict(l=10, r=10, t=30, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={'color': "darkblue", 'family': "Arial"}
            )
            
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Show classification below gauge
            st.markdown(f"**Classification:** {fng_class}", unsafe_allow_html=True)
        else:
            st.metric("😰 Fear & Greed Index", "API Failed")
    
    # Circulating Supply
    with fear_col2:
        blockchain_data = metrics.get('blockchain', {})
        if blockchain_data.get('total_supply'):
            total_supply = blockchain_data['total_supply'] / 1e8  # Convert from satoshis
            remaining = 21_000_000 - total_supply
            st.metric("🪙 Circulating Supply", f"{total_supply:,.0f} BTC")
            st.markdown("<br>", unsafe_allow_html=True)
            st.metric("⏳ Remaining to Mine", f"{remaining:,.0f} BTC")
            
            # Progress bar to 21M
            st.markdown("<br>", unsafe_allow_html=True)
            progress = total_supply / 21_000_000
            st.progress(progress, text=f"{progress:.1%} of 21M mined")
        else:
            st.metric("🪙 Circulating Supply", "API Failed")
    
    # Block Count & Difficulty
    with fear_col3:
        if blockchain_data.get('block_count'):
            st.metric("🧱 Block Count", f"{blockchain_data['block_count']:,}")
        else:
            st.metric("🧱 Block Count", "API Failed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if blockchain_data.get('mining_difficulty'):
            difficulty = blockchain_data['mining_difficulty']
            difficulty_t = difficulty / 1e12
            st.metric("⛏️ Mining Difficulty", f"{difficulty_t:.2f}T")
        else:
            st.metric("⛏️ Mining Difficulty", "API Failed")


def _render_network_activity_charts(metrics):
    """Render the network activity charts section"""
    # Check if we have chart data
    charts = metrics.get('charts', {})
    
    if charts:
        # Create tabs for different chart categories
        chart_tab1, chart_tab2, chart_tab3 = st.tabs(["📊 Transactions", "⛏️ Mining", "💰 Economics"])
        
        with chart_tab1:
            _render_transaction_charts(charts)
        
        with chart_tab2:
            _render_mining_charts(charts)
        
        with chart_tab3:
            _render_economic_charts(charts)
    else:
        st.warning("⚠️ Chart data unavailable - API issues detected")


def _render_transaction_charts(charts):
    """Render transaction-related charts"""
    trans_col1, trans_col2 = st.columns(2)
    
    with trans_col1:
        # Daily Transactions
        if 'n-transactions' in charts:
            tx_data = charts['n-transactions']
            if tx_data.get('values'):
                # Prepare data
                dates = [datetime.fromtimestamp(point['x']) for point in tx_data['values']]
                values = [point['y'] for point in tx_data['values']]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=dates, 
                    y=values,
                    mode='lines',
                    name='Daily Transactions',
                    line=dict(color='#f7931a', width=2)
                ))
                
                fig.update_layout(
                    title="📈 Daily Bitcoin Transactions",
                    xaxis_title="Date",
                    yaxis_title="Transactions",
                    height=400,
                    template="plotly_dark"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show latest value
                if values:
                    st.metric("🔄 Latest Daily Transactions", f"{values[-1]:,.0f}")
        else:
            st.error("❌ Transaction data unavailable")
    
    with trans_col2:
        # Network Activity (Alternative to deprecated Active Addresses)
        if 'n-transactions' in charts:
            tx_data = charts['n-transactions']
            if tx_data.get('values'):
                # Use transaction data as a proxy for network activity
                dates = [datetime.fromtimestamp(point['x']) for point in tx_data['values']]
                values = [point['y'] for point in tx_data['values']]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=dates, 
                    y=values,
                    mode='lines+markers',
                    name='Daily Transactions',
                    line=dict(color='#00d4aa', width=2),
                    marker=dict(size=4)
                ))
                
                fig.update_layout(
                    title="📊 Network Activity (Daily Transactions)",
                    xaxis_title="Date",
                    yaxis_title="Number of Transactions",
                    height=400,
                    template="plotly_dark"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                if values:
                    # Show transactions per second for context
                    latest_tx = values[-1]
                    tx_per_second = latest_tx / (24 * 60 * 60)
                    st.metric("📊 Latest Daily Transactions", f"{latest_tx:,.0f}")
                    st.metric("⚡ Transactions per Second", f"{tx_per_second:.2f}")
        else:
            st.warning("⚠️ Network activity data temporarily unavailable")


def _render_mining_charts(charts):
    """Render mining-related charts"""
    mining_col1, mining_col2 = st.columns(2)
    
    with mining_col1:
        # Hash Rate
        if 'hash-rate' in charts:
            hash_data = charts['hash-rate']
            if hash_data.get('values'):
                dates = [datetime.fromtimestamp(point['x']) for point in hash_data['values']]
                raw_values = [point['y'] for point in hash_data['values']]
                
                # Convert hash rate based on magnitude
                latest_raw = raw_values[-1] if raw_values else 0
                if latest_raw > 1e15:
                    values = [v / 1e18 for v in raw_values]
                elif latest_raw > 1e6:
                    values = [v / 1e6 for v in raw_values]
                elif latest_raw > 1e3:
                    values = [v / 1e9 for v in raw_values]
                elif latest_raw > 1:
                    values = [v / 1e12 for v in raw_values]
                else:
                    values = raw_values
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=dates, 
                    y=values,
                    mode='lines',
                    name='Hash Rate (EH/s)',
                    line=dict(color='#ff6b35', width=3),
                    fill='tonexty'
                ))
                
                fig.update_layout(
                    title="⚡ Bitcoin Network Hash Rate",
                    xaxis_title="Date",
                    yaxis_title="Hash Rate (EH/s)",
                    height=400,
                    template="plotly_dark"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                if values:
                    st.metric("⚡ Current Hash Rate", f"{values[-1]:.0f} EH/s")
        else:
            st.error("❌ Hash rate data unavailable")
    
    with mining_col2:
        # Mining Revenue
        if 'miners-revenue' in charts:
            revenue_data = charts['miners-revenue']
            if revenue_data.get('values'):
                dates = [datetime.fromtimestamp(point['x']) for point in revenue_data['values']]
                values = [point['y'] / 1e6 for point in revenue_data['values']]  # Convert to millions
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=dates, 
                    y=values,
                    mode='lines',
                    name='Daily Revenue ($M)',
                    line=dict(color='#4ecdc4', width=2),
                    fill='tozeroy'
                ))
                
                fig.update_layout(
                    title="💰 Daily Mining Revenue",
                    xaxis_title="Date",
                    yaxis_title="Revenue (Million USD)",
                    height=400,
                    template="plotly_dark"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                if values:
                    st.metric("💰 Latest Daily Revenue", f"${values[-1]:.1f}M")
        else:
            st.error("❌ Mining revenue data unavailable")


def _render_economic_charts(charts):
    """Render economic-related charts"""
    econ_col1, econ_col2 = st.columns(2)
    
    with econ_col1:
        # Transaction Fees
        if 'transaction-fees-usd' in charts:
            fees_data = charts['transaction-fees-usd']
            if fees_data.get('values'):
                dates = [datetime.fromtimestamp(point['x']) for point in fees_data['values']]
                values = [point['y'] for point in fees_data['values']]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=dates, 
                    y=values,
                    mode='lines+markers',
                    name='Avg Transaction Fee',
                    line=dict(color='#e74c3c', width=2),
                    marker=dict(size=3)
                ))
                
                fig.update_layout(
                    title="💳 Average Transaction Fees",
                    xaxis_title="Date",
                    yaxis_title="Fee (USD)",
                    height=400,
                    template="plotly_dark"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                if values:
                    st.metric("💳 Current Avg Fee", f"${values[-1]:.2f}")
        else:
            st.error("❌ Transaction fees data unavailable")
    
    with econ_col2:
        # Mempool Size
        if 'mempool-size' in charts:
            mempool_data = charts['mempool-size']
            if mempool_data.get('values'):
                dates = [datetime.fromtimestamp(point['x']) for point in mempool_data['values']]
                values = [point['y'] / 1e6 for point in mempool_data['values']]  # Convert to MB
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=dates, 
                    y=values,
                    mode='lines',
                    name='Mempool Size (MB)',
                    line=dict(color='#9b59b6', width=2),
                    fill='tozeroy'
                ))
                
                fig.update_layout(
                    title="📦 Mempool Size",
                    xaxis_title="Date",
                    yaxis_title="Size (MB)",
                    height=400,
                    template="plotly_dark"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                if values:
                    st.metric("📦 Current Mempool", f"{values[-1]:.1f} MB")
        else:
            st.error("❌ Mempool data unavailable")


def _render_network_health_section(metrics):
    """Render the network health section"""
    network_col1, network_col2, network_col3 = st.columns(3)
    charts = metrics.get('charts', {})
    
    # Block timing
    with network_col1:
        if 'avg_block_time' in metrics:
            # Use the new direct avg_block_time field
            avg_block_time = metrics['avg_block_time']
            delta_color = "normal" if 8 <= avg_block_time <= 12 else "inverse"
            st.metric(
                "⏰ Avg Block Time", 
                f"{avg_block_time:.1f} min",
                delta=f"Target: 10 min",
                delta_color=delta_color
            )
        elif 'avg-block-time' in charts:
            # Fallback to chart data if available
            block_time_data = charts['avg-block-time']
            if block_time_data.get('values') and len(block_time_data['values']) > 0:
                latest_block_time = block_time_data['values'][-1]['y'] / 60  # Convert to minutes
                delta_color = "normal" if 8 <= latest_block_time <= 12 else "inverse"
                st.metric(
                    "⏰ Avg Block Time", 
                    f"{latest_block_time:.1f} min",
                    delta=f"Target: 10 min",
                    delta_color=delta_color
                )
            else:
                st.metric("⏰ Avg Block Time", "API Failed")
        else:
            st.metric("⏰ Avg Block Time", "API Failed")
    
    # Block size
    with network_col2:
        if 'avg-block-size' in charts:
            block_size_data = charts['avg-block-size']
            if block_size_data.get('values') and len(block_size_data['values']) > 0:
                latest_value = block_size_data['values'][-1]
                if isinstance(latest_value, dict) and 'y' in latest_value:
                    y_value = latest_value['y']
                    latest_block_size = y_value  # No conversion needed
                    st.metric("📏 Avg Block Size", f"{latest_block_size:.2f} MB")
                else:
                    st.metric("📏 Avg Block Size", "Data Error")
            else:
                st.metric("📏 Avg Block Size", "API Failed")
        else:
            st.metric("📏 Avg Block Size", "API Failed")
    
    # Block reward and halving details
    with network_col3:
        blockchain_data = metrics.get('blockchain', {})
        if blockchain_data.get('block_reward'):
            block_reward = blockchain_data['block_reward']
            st.metric("🎁 Block Reward", f"{block_reward} BTC")
            
            # Enhanced halving calculations with validation
            current_blocks = blockchain_data.get('block_count', 0)
            blocks_per_halving = 210_000
            
            # Calculate current halving epoch and cycle details
            current_epoch = current_blocks // blocks_per_halving
            blocks_mined_this_cycle = current_blocks - (current_epoch * blocks_per_halving)
            next_halving_block = (current_epoch + 1) * blocks_per_halving
            blocks_to_halving = next_halving_block - current_blocks
            
            # Time calculation using actual average block time
            actual_block_time = 10.0  # Default fallback
            days_to_halving = (blocks_to_halving * actual_block_time) / (60 * 24)
            
            # Display main halving countdown
            st.metric("📅 Est. Days to Halving", f"{days_to_halving:,.0f}")
            
            # Add detailed halving cycle information
            st.caption(f"🔄 **Halving Cycle {current_epoch + 1}**")
            st.caption(f"✅ Blocks Mined: {blocks_mined_this_cycle:,} / {blocks_per_halving:,}")
            st.caption(f"⏳ Blocks Remaining: {blocks_to_halving:,}")
            
            # Progress percentage
            cycle_progress = (blocks_mined_this_cycle / blocks_per_halving) * 100
            st.caption(f"📊 Cycle Progress: {cycle_progress:.1f}%")
            
            # Next halving block number
            st.caption(f"🎯 Next Halving Block: {next_halving_block:,}")
            
        else:
            st.metric("🎁 Block Reward", "API Failed")
