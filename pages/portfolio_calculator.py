"""
Portfolio Value Calculator page.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from utils.system_logger import debug_log, debug_log_user_action
from utils.data_cache_manager import cached_get_crypto_prices
from utils.portfolio_session_manager import initialize_portfolio_session, reset_to_default_portfolio


def render_portfolio_page():
    """Render the Portfolio Value Calculator page"""
    debug_log_user_action("Viewing Portfolio Value page")
    
    st.header("💼 Portfolio Value Calculator")
    st.info("📊 Track your cryptocurrency portfolio value and performance")

    # Initialize portfolio session state
    initialize_portfolio_session()
    
    # Portfolio management controls
    col_reset, col_total, col_refresh = st.columns([1, 2, 1])
    
    with col_reset:
        if st.button("🔄 Reset Portfolio", type="secondary"):
            reset_to_default_portfolio()
            debug_log("🔄 User reset portfolio to defaults", "INFO", "portfolio_reset")
            st.rerun()
    
    with col_refresh:
        if st.button("📊 Refresh Prices", type="secondary"):
            cached_get_crypto_prices.clear()
            debug_log("🔄 User triggered price refresh", "INFO", "price_refresh")
            st.rerun()
    
    # Load current prices
    with st.spinner("🔄 Loading current cryptocurrency prices..."):
        try:
            current_prices = cached_get_crypto_prices()
            
            if not current_prices:
                st.error("❌ Failed to fetch current prices")
                st.stop()
            
            debug_log(f"💰 Prices loaded for portfolio calculation. Available: {list(current_prices.keys())}", "SUCCESS", "portfolio_prices_loaded")
            
            # Calculate total portfolio value
            total_value = _calculate_total_portfolio_value(current_prices)
            
            with col_total:
                st.metric("💰 Total Portfolio Value", f"${total_value:,.2f}")
            
            # === PORTFOLIO MANAGEMENT ===
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("⚙️ Portfolio Management")
            _render_portfolio_management(current_prices)
            
            # === PORTFOLIO OVERVIEW ===
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("📊 Portfolio Overview")
            _render_portfolio_overview(current_prices)
            
            # === DETAILED HOLDINGS ===
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("📈 Detailed Holdings")
            _render_detailed_holdings(current_prices)
            
            # === PORTFOLIO CHARTS ===
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("📊 Portfolio Visualization")
            _render_portfolio_charts(current_prices)
            
            # === PERFORMANCE TRACKING ===
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("📈 Performance Tracking")
            _render_performance_tracking(current_prices)
            
            # Data source info
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()
            col_time, col_source = st.columns(2)
            with col_time:
                st.caption(f"🕐 Prices updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            with col_source:
                st.caption("📡 Source: CoinGecko API")
            
        except Exception as e:
            debug_log(f"❌ Error in portfolio page: {str(e)}", "ERROR", "portfolio_page_error")
            st.error(f"❌ Error loading portfolio data: {str(e)}")


def _render_portfolio_management(current_prices):
    """Render portfolio management interface"""
    # Available cryptocurrencies from the price data
    available_cryptos = {
        'bitcoin': 'Bitcoin (BTC)',
        'ethereum': 'Ethereum (ETH)',
        'binancecoin': 'Binance Coin (BNB)',
        'cardano': 'Cardano (ADA)',
        'solana': 'Solana (SOL)',
        'polkadot': 'Polkadot (DOT)',
        'chainlink': 'Chainlink (LINK)',
        'litecoin': 'Litecoin (LTC)',
        'bitcoin-cash': 'Bitcoin Cash (BCH)',
        'stellar': 'Stellar (XLM)'
    }
    
    # Filter to only show available cryptos
    available_in_data = {k: v for k, v in available_cryptos.items() if k in current_prices}
    
    col_add, col_edit = st.columns(2)
    
    with col_add:
        st.markdown("#### ➕ Add New Holding")
        
        selected_crypto = st.selectbox(
            "Select Cryptocurrency",
            options=list(available_in_data.keys()),
            format_func=lambda x: available_in_data[x],
            key="add_crypto_select"
        )
        
        amount = st.number_input(
            "Amount",
            min_value=0.0,
            value=0.0,
            step=0.001,
            format="%.6f",
            key="add_amount"
        )
        
        if st.button("➕ Add Holding", type="primary"):
            if amount > 0:
                if selected_crypto not in st.session_state.portfolio:
                    st.session_state.portfolio[selected_crypto] = 0.0
                
                st.session_state.portfolio[selected_crypto] += amount
                debug_log(f"➕ Added {amount} {selected_crypto} to portfolio", "INFO", "portfolio_add")
                st.success(f"✅ Added {amount} {available_in_data[selected_crypto]} to portfolio")
                st.rerun()
            else:
                st.error("❌ Amount must be greater than 0")
    
    with col_edit:
        st.markdown("#### ✏️ Edit Existing Holdings")
        
        if st.session_state.portfolio:
            holding_to_edit = st.selectbox(
                "Select Holding to Edit",
                options=list(st.session_state.portfolio.keys()),
                format_func=lambda x: available_cryptos.get(x, x),
                key="edit_crypto_select"
            )
            
            current_amount = st.session_state.portfolio.get(holding_to_edit, 0.0)
            
            new_amount = st.number_input(
                f"New Amount (Current: {current_amount})",
                min_value=0.0,
                value=current_amount,
                step=0.001,
                format="%.6f",
                key="edit_amount"
            )
            
            col_update, col_remove = st.columns(2)
            
            with col_update:
                if st.button("💾 Update", type="secondary"):
                    if new_amount >= 0:
                        old_amount = st.session_state.portfolio[holding_to_edit]
                        st.session_state.portfolio[holding_to_edit] = new_amount
                        debug_log(f"💾 Updated {holding_to_edit}: {old_amount} → {new_amount}", "INFO", "portfolio_update")
                        st.success(f"✅ Updated {available_cryptos.get(holding_to_edit, holding_to_edit)}")
                        st.rerun()
            
            with col_remove:
                if st.button("🗑️ Remove", type="secondary"):
                    removed_amount = st.session_state.portfolio.pop(holding_to_edit, 0)
                    debug_log(f"🗑️ Removed {holding_to_edit} ({removed_amount}) from portfolio", "INFO", "portfolio_remove")
                    st.success(f"✅ Removed {available_cryptos.get(holding_to_edit, holding_to_edit)}")
                    st.rerun()
        else:
            st.info("📝 No holdings to edit. Add some cryptocurrency first!")


def _render_portfolio_overview(current_prices):
    """Render portfolio overview metrics"""
    if not st.session_state.portfolio:
        st.info("📝 Your portfolio is empty. Add some cryptocurrency holdings above!")
        return
    
    # Calculate portfolio metrics
    portfolio_data = []
    total_value = 0
    
    for crypto_id, amount in st.session_state.portfolio.items():
        if amount > 0 and crypto_id in current_prices:
            price = current_prices[crypto_id]['usd']
            value = amount * price
            change_24h = current_prices[crypto_id].get('usd_24h_change', 0)
            
            portfolio_data.append({
                'crypto': crypto_id,
                'amount': amount,
                'price': price,
                'value': value,
                'change_24h': change_24h,
                'value_change_24h': value * (change_24h / 100)
            })
            total_value += value
    
    if not portfolio_data:
        st.warning("⚠️ No valid holdings found with current prices")
        return
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Total Value", f"${total_value:,.2f}")
    
    with col2:
        total_change_24h = sum(item['value_change_24h'] for item in portfolio_data)
        change_pct = (total_change_24h / total_value) * 100 if total_value > 0 else 0
        delta_color = "normal" if total_change_24h >= 0 else "inverse"
        st.metric(
            "📈 24h Change", 
            f"${total_change_24h:+,.2f}",
            delta=f"{change_pct:+.2f}%",
            delta_color=delta_color
        )
    
    with col3:
        num_holdings = len(portfolio_data)
        st.metric("🏛️ Holdings", f"{num_holdings}")
    
    with col4:
        # Calculate largest holding percentage
        largest_value = max(item['value'] for item in portfolio_data)
        largest_pct = (largest_value / total_value) * 100 if total_value > 0 else 0
        st.metric("🎯 Largest Holding", f"{largest_pct:.1f}%")


def _render_detailed_holdings(current_prices):
    """Render detailed holdings table"""
    if not st.session_state.portfolio:
        st.info("📝 No holdings to display")
        return
    
    # Prepare data for table
    table_data = []
    
    for crypto_id, amount in st.session_state.portfolio.items():
        if amount > 0 and crypto_id in current_prices:
            price_data = current_prices[crypto_id]
            price = price_data['usd']
            value = amount * price
            change_24h = price_data.get('usd_24h_change', 0)
            
            # Get crypto name
            crypto_names = {
                'bitcoin': 'Bitcoin',
                'ethereum': 'Ethereum',
                'binancecoin': 'Binance Coin',
                'cardano': 'Cardano',
                'solana': 'Solana',
                'polkadot': 'Polkadot',
                'chainlink': 'Chainlink',
                'litecoin': 'Litecoin',
                'bitcoin-cash': 'Bitcoin Cash',
                'stellar': 'Stellar'
            }
            
            crypto_name = crypto_names.get(crypto_id, crypto_id.title())
            
            table_data.append({
                'Cryptocurrency': crypto_name,
                'Symbol': crypto_id.upper()[:3],
                'Amount': f"{amount:.6f}",
                'Price (USD)': f"${price:,.2f}",
                'Value (USD)': f"${value:,.2f}",
                '24h Change (%)': f"{change_24h:+.2f}%",
                '24h Change ($)': f"${value * (change_24h / 100):+,.2f}"
            })
    
    if table_data:
        df = pd.DataFrame(table_data)
        
        # Sort by value (descending)
        df['Value_Numeric'] = [float(val.replace('$', '').replace(',', '')) for val in df['Value (USD)']]
        df = df.sort_values('Value_Numeric', ascending=False).drop('Value_Numeric', axis=1)
        
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "24h Change (%)": st.column_config.TextColumn(
                    "24h Change (%)",
                    help="24-hour price change percentage"
                ),
                "24h Change ($)": st.column_config.TextColumn(
                    "24h Change ($)",
                    help="24-hour value change in USD"
                )
            }
        )
    else:
        st.info("📝 No valid holdings to display")


def _render_portfolio_charts(current_prices):
    """Render portfolio visualization charts"""
    if not st.session_state.portfolio:
        st.info("📝 No data to visualize")
        return
    
    # Prepare data for charts
    chart_data = []
    total_value = 0
    
    for crypto_id, amount in st.session_state.portfolio.items():
        if amount > 0 and crypto_id in current_prices:
            price = current_prices[crypto_id]['usd']
            value = amount * price
            
            crypto_names = {
                'bitcoin': 'Bitcoin',
                'ethereum': 'Ethereum', 
                'binancecoin': 'Binance Coin',
                'cardano': 'Cardano',
                'solana': 'Solana',
                'polkadot': 'Polkadot',
                'chainlink': 'Chainlink',
                'litecoin': 'Litecoin',
                'bitcoin-cash': 'Bitcoin Cash',
                'stellar': 'Stellar'
            }
            
            crypto_name = crypto_names.get(crypto_id, crypto_id.title())
            chart_data.append({
                'name': crypto_name,
                'value': value,
                'amount': amount,
                'price': price
            })
            total_value += value
    
    if not chart_data:
        st.info("📝 No valid data for charts")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Portfolio allocation pie chart
        if len(chart_data) > 1:
            fig_pie = px.pie(
                values=[item['value'] for item in chart_data],
                names=[item['name'] for item in chart_data],
                title="💼 Portfolio Allocation",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig_pie.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Value: $%{value:,.2f}<br>Percentage: %{percent}<extra></extra>'
            )
            
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("📊 Need multiple holdings for allocation chart")
    
    with col2:
        # Value bar chart
        fig_bar = go.Figure()
        
        names = [item['name'] for item in chart_data]
        values = [item['value'] for item in chart_data]
        
        # Sort by value for better visualization
        sorted_data = sorted(zip(names, values), key=lambda x: x[1], reverse=True)
        sorted_names, sorted_values = zip(*sorted_data) if sorted_data else ([], [])
        
        fig_bar.add_trace(go.Bar(
            x=sorted_names,
            y=sorted_values,
            name="Holdings Value",
            marker_color='#f7931a',
            text=[f"${v:,.0f}" for v in sorted_values],
            textposition='auto'
        ))
        
        fig_bar.update_layout(
            title="💰 Holdings Value",
            xaxis_title="Cryptocurrency",
            yaxis_title="Value (USD)",
            height=400,
            template="plotly_dark",
            xaxis_tickangle=-45
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)


def _render_performance_tracking(current_prices):
    """Render performance tracking section"""
    if not st.session_state.portfolio:
        st.info("📝 No portfolio data for performance tracking")
        return
    
    # Calculate current performance metrics
    portfolio_data = []
    total_value = 0
    total_change_24h = 0
    
    for crypto_id, amount in st.session_state.portfolio.items():
        if amount > 0 and crypto_id in current_prices:
            price_data = current_prices[crypto_id]
            price = price_data['usd']
            value = amount * price
            change_24h = price_data.get('usd_24h_change', 0)
            value_change_24h = value * (change_24h / 100)
            
            portfolio_data.append({
                'crypto': crypto_id,
                'value': value,
                'change_24h': change_24h,
                'value_change_24h': value_change_24h
            })
            
            total_value += value
            total_change_24h += value_change_24h
    
    if not portfolio_data:
        st.info("📝 No valid data for performance tracking")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📊 24-Hour Performance")
        change_pct = (total_change_24h / total_value) * 100 if total_value > 0 else 0
        
        if total_change_24h >= 0:
            st.success(f"📈 **Gain**: ${total_change_24h:+,.2f} ({change_pct:+.2f}%)")
        else:
            st.error(f"📉 **Loss**: ${total_change_24h:+,.2f} ({change_pct:+.2f}%)")
        
        # Performance by asset
        st.markdown("**Performance by Asset:**")
        for item in sorted(portfolio_data, key=lambda x: x['value_change_24h'], reverse=True):
            crypto_name = item['crypto'].replace('-', ' ').title()
            change = item['value_change_24h']
            change_pct = item['change_24h']
            
            if change >= 0:
                st.markdown(f"🟢 {crypto_name}: ${change:+,.2f} ({change_pct:+.1f}%)")
            else:
                st.markdown(f"🔴 {crypto_name}: ${change:+,.2f} ({change_pct:+.1f}%)")
    
    with col2:
        st.markdown("#### 📈 Portfolio Metrics")
        
        # Best and worst performers
        best_performer = max(portfolio_data, key=lambda x: x['change_24h'])
        worst_performer = min(portfolio_data, key=lambda x: x['change_24h'])
        
        st.metric(
            "🏆 Best Performer", 
            best_performer['crypto'].replace('-', ' ').title(),
            delta=f"{best_performer['change_24h']:+.1f}%"
        )
        
        st.metric(
            "📉 Worst Performer", 
            worst_performer['crypto'].replace('-', ' ').title(),
            delta=f"{worst_performer['change_24h']:+.1f}%"
        )
        
        # Portfolio diversity
        num_holdings = len(portfolio_data)
        st.metric("🏛️ Diversification", f"{num_holdings} assets")
    
    with col3:
        st.markdown("#### 💡 Portfolio Insights")
        
        # Calculate some insights
        positive_performers = sum(1 for item in portfolio_data if item['change_24h'] > 0)
        negative_performers = len(portfolio_data) - positive_performers
        
        st.markdown(f"📈 **Positive**: {positive_performers} assets")
        st.markdown(f"📉 **Negative**: {negative_performers} assets")
        
        if len(portfolio_data) > 0:
            positive_pct = (positive_performers / len(portfolio_data)) * 100
            st.progress(positive_pct / 100, text=f"{positive_pct:.0f}% positive performers")
        
        # Risk assessment based on portfolio concentration
        largest_holding_pct = max(item['value'] for item in portfolio_data) / total_value * 100
        
        if largest_holding_pct > 70:
            risk_level = "🔴 High Risk (Concentrated)"
        elif largest_holding_pct > 50:
            risk_level = "🟡 Medium Risk"
        else:
            risk_level = "🟢 Low Risk (Diversified)"
        
        st.markdown(f"⚖️ **Risk Level**: {risk_level}")
        st.markdown(f"📊 **Largest Holding**: {largest_holding_pct:.1f}%")


def _calculate_total_portfolio_value(current_prices):
    """Calculate total portfolio value"""
    total_value = 0
    
    for crypto_id, amount in st.session_state.portfolio.items():
        if amount > 0 and crypto_id in current_prices:
            price = current_prices[crypto_id]['usd']
            total_value += amount * price
    
    return total_value
