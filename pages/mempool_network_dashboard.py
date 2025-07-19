"""
Mempool Data Analysis page.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from utils.system_logger import debug_log, debug_log_user_action, debug_log_api_call
from utils.data_cache_manager import cached_get_mempool_info
import time


def render_mempool_page():
    """Render the Mempool Data Analysis page"""
    debug_log_user_action("Viewing Mempool Data page")
    
    st.header("📦 Mempool Data Analysis")
    st.info("🔍 Deep dive into Bitcoin's pending transaction pool")

    # Refresh button and auto-refresh checkbox
    col_refresh, col_auto = st.columns([1, 2])
    with col_refresh:
        if st.button("🔄 Refresh Data", type="secondary"):
            cached_get_mempool_info.clear()
            debug_log("🔄 User triggered mempool data refresh", "INFO", "user_refresh")
            st.rerun()
    
    with col_auto:
        auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", value=False, help="Automatically refresh data every 30 seconds")
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(30)
        cached_get_mempool_info.clear()
        st.rerun()
    
    # Get mempool data
    with st.spinner("🔄 Loading mempool data..."):
        try:
            debug_log("📦 Starting mempool data collection...", "INFO", "mempool_data_start")
            mempool_data = cached_get_mempool_info()
            
            if mempool_data is None:
                st.error("❌ Failed to fetch mempool data")
                st.stop()
            
            debug_log(f"📦 Mempool data loaded successfully. Count: {mempool_data.get('count', 0)}", "SUCCESS", "mempool_data_loaded")
            
            # === OVERVIEW METRICS ===
            _render_mempool_overview(mempool_data)
            
            # === FEE ANALYSIS ===
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("💰 Fee Analysis")
            _render_fee_analysis(mempool_data)
            
            # === TRANSACTION DISTRIBUTION ===
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("📊 Transaction Distribution")
            _render_transaction_distribution(mempool_data)
            
            # === DETAILED MEMPOOL STATS ===
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("📈 Detailed Statistics")
            _render_detailed_stats(mempool_data)
            
            # === FEE RATE HISTOGRAM ===
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("📊 Fee Rate Distribution")
            _render_fee_rate_histogram(mempool_data)
            
            # Data source info
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()
            col_time, col_source = st.columns(2)
            with col_time:
                st.caption(f"🕐 Data updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            with col_source:
                st.caption("📡 Source: mempool.space API")
            
        except Exception as e:
            debug_log(f"❌ Error in mempool page: {str(e)}", "ERROR", "mempool_page_error")
            st.error(f"❌ Error loading mempool data: {str(e)}")


def _render_mempool_overview(mempool_data):
    """Render the mempool overview metrics"""
    st.subheader("📊 Mempool Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        count = mempool_data.get('count', 0)
        st.metric("📦 Pending Transactions", f"{count:,}")
    
    with col2:
        size = mempool_data.get('vsize', 0)
        size_mb = size / 1_000_000  # Convert to MB
        st.metric("💾 Mempool Size", f"{size_mb:.1f} MB")
    
    with col3:
        total_fees = mempool_data.get('total_fee', 0)
        total_fees_btc = total_fees / 100_000_000  # Convert from satoshis to BTC
        st.metric("💰 Total Pending Fees", f"{total_fees_btc:.3f} BTC")
    
    with col4:
        # Calculate average fee rate if we have the data
        if mempool_data.get('fee_histogram'):
            avg_fee_rate = _calculate_average_fee_rate(mempool_data['fee_histogram'])
            st.metric("⚡ Avg Fee Rate", f"{avg_fee_rate:.1f} sat/vB")
        else:
            st.metric("⚡ Avg Fee Rate", "N/A")


def _render_fee_analysis(mempool_data):
    """Render fee analysis section"""
    fee_histogram = mempool_data.get('fee_histogram', [])
    
    if not fee_histogram:
        st.warning("⚠️ Fee histogram data not available")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Fee Rate Distribution Chart
        fee_rates = []
        tx_counts = []
        
        for bucket in fee_histogram:
            if len(bucket) >= 3:
                fee_rate = bucket[0]  # Fee rate in sat/vB
                tx_count = bucket[2]  # Number of transactions
                fee_rates.append(fee_rate)
                tx_counts.append(tx_count)
        
        if fee_rates and tx_counts:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=fee_rates,
                y=tx_counts,
                name="Transactions",
                marker_color='#f7931a'
            ))
            
            fig.update_layout(
                title="📊 Fee Rate Distribution",
                xaxis_title="Fee Rate (sat/vB)",
                yaxis_title="Number of Transactions",
                height=400,
                template="plotly_dark"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Fee Recommendations
        recommended_fees = _calculate_fee_recommendations(fee_histogram)
        
        st.markdown("### 🎯 Fee Recommendations")
        
        for priority, fee_rate in recommended_fees.items():
            if priority == "🐌 Low Priority":
                color = "🟢"
            elif priority == "🚀 Medium Priority":
                color = "🟡"
            else:  # High Priority
                color = "🔴"
            
            st.markdown(f"{color} **{priority}**: {fee_rate} sat/vB")
        
        # Additional fee insights
        st.markdown("### 💡 Fee Insights")
        
        if fee_histogram:
            # Calculate total pending value
            total_size = sum(bucket[1] for bucket in fee_histogram if len(bucket) >= 2)
            st.markdown(f"📏 **Total Pending Size**: {total_size / 1_000_000:.1f} MB")
            
            # Calculate fee range
            if fee_rates:
                min_fee = min(fee_rates)
                max_fee = max(fee_rates)
                st.markdown(f"💰 **Fee Range**: {min_fee} - {max_fee} sat/vB")


def _render_transaction_distribution(mempool_data):
    """Render transaction distribution charts"""
    fee_histogram = mempool_data.get('fee_histogram', [])
    
    if not fee_histogram:
        st.warning("⚠️ Transaction distribution data not available")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Transaction Size Distribution
        sizes = []
        counts = []
        
        for bucket in fee_histogram:
            if len(bucket) >= 3:
                size = bucket[1]  # Size in vBytes
                count = bucket[2]  # Number of transactions
                sizes.append(size)
                counts.append(count)
        
        if sizes and counts:
            # Create size ranges for better visualization
            size_ranges = []
            range_counts = []
            
            # Group by size ranges
            ranges = [
                (0, 250, "Tiny (0-250 vB)"),
                (250, 500, "Small (250-500 vB)"),
                (500, 1000, "Medium (500-1000 vB)"),
                (1000, 2000, "Large (1-2 KB)"),
                (2000, float('inf'), "Extra Large (>2 KB)")
            ]
            
            for min_size, max_size, label in ranges:
                count = sum(counts[i] for i, size in enumerate(sizes) 
                           if min_size <= size < max_size)
                if count > 0:
                    size_ranges.append(label)
                    range_counts.append(count)
            
            if size_ranges:
                fig = px.pie(
                    values=range_counts, 
                    names=size_ranges, 
                    title="📏 Transaction Size Distribution",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Fee Rate Ranges
        if fee_histogram:
            fee_ranges = []
            fee_counts = []
            
            # Define fee rate ranges
            ranges = [
                (0, 5, "Very Low (0-5 sat/vB)"),
                (5, 10, "Low (5-10 sat/vB)"),
                (10, 20, "Medium (10-20 sat/vB)"),
                (20, 50, "High (20-50 sat/vB)"),
                (50, float('inf'), "Very High (>50 sat/vB)")
            ]
            
            for min_fee, max_fee, label in ranges:
                count = sum(bucket[2] for bucket in fee_histogram 
                           if len(bucket) >= 3 and min_fee <= bucket[0] < max_fee)
                if count > 0:
                    fee_ranges.append(label)
                    fee_counts.append(count)
            
            if fee_ranges:
                fig = px.pie(
                    values=fee_counts, 
                    names=fee_ranges, 
                    title="💰 Fee Rate Distribution",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)


def _render_detailed_stats(mempool_data):
    """Render detailed mempool statistics"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📈 Size Statistics")
        vsize = mempool_data.get('vsize', 0)
        st.markdown(f"**Total vSize**: {vsize:,} vBytes")
        st.markdown(f"**Size in MB**: {vsize / 1_000_000:.2f} MB")
        
        # Calculate average transaction size
        count = mempool_data.get('count', 0)
        if count > 0:
            avg_size = vsize / count
            st.markdown(f"**Avg TX Size**: {avg_size:.0f} vBytes")
    
    with col2:
        st.markdown("### 💰 Fee Statistics")
        total_fee = mempool_data.get('total_fee', 0)
        total_fee_btc = total_fee / 100_000_000
        st.markdown(f"**Total Fees**: {total_fee_btc:.4f} BTC")
        st.markdown(f"**Fees in Sats**: {total_fee:,}")
        
        # Calculate average fee per transaction
        if count > 0:
            avg_fee = total_fee / count
            st.markdown(f"**Avg Fee/TX**: {avg_fee:,.0f} sats")
    
    with col3:
        st.markdown("### ⏱️ Time Estimates")
        fee_histogram = mempool_data.get('fee_histogram', [])
        if fee_histogram:
            # Estimate confirmation times based on mempool congestion
            total_pending_size = sum(bucket[1] for bucket in fee_histogram if len(bucket) >= 2)
            
            # Rough estimates based on 1 MB blocks every 10 minutes
            blocks_to_clear = total_pending_size / 1_000_000
            time_to_clear = blocks_to_clear * 10  # minutes
            
            st.markdown(f"**Blocks to Clear**: ~{blocks_to_clear:.1f}")
            st.markdown(f"**Est. Time**: ~{time_to_clear:.0f} minutes")
            
            if time_to_clear > 60:
                hours = time_to_clear / 60
                st.markdown(f"**({hours:.1f} hours)**")


def _render_fee_rate_histogram(mempool_data):
    """Render detailed fee rate histogram"""
    fee_histogram = mempool_data.get('fee_histogram', [])
    
    if not fee_histogram:
        st.warning("⚠️ Fee rate histogram data not available")
        return
    
    # Extract data for histogram
    fee_rates = []
    tx_counts = []
    total_sizes = []
    
    for bucket in fee_histogram:
        if len(bucket) >= 3:
            fee_rate = bucket[0]
            size = bucket[1]
            count = bucket[2]
            
            fee_rates.append(fee_rate)
            tx_counts.append(count)
            total_sizes.append(size)
    
    if not fee_rates:
        st.warning("⚠️ No fee rate data available")
        return
    
    # Create dual-axis chart
    fig = go.Figure()
    
    # Add transaction count bars
    fig.add_trace(go.Bar(
        x=fee_rates,
        y=tx_counts,
        name="Transaction Count",
        marker_color='#f7931a',
        yaxis='y',
        opacity=0.7
    ))
    
    # Add size line
    fig.add_trace(go.Scatter(
        x=fee_rates,
        y=total_sizes,
        mode='lines+markers',
        name="Total Size (vBytes)",
        line=dict(color='#00d4aa', width=2),
        yaxis='y2'
    ))
    
    # Update layout with dual y-axes
    fig.update_layout(
        title="📊 Comprehensive Fee Rate Analysis",
        xaxis_title="Fee Rate (sat/vB)",
        yaxis=dict(
            title="Number of Transactions",
            side="left"
        ),
        yaxis2=dict(
            title="Total Size (vBytes)",
            side="right",
            overlaying="y"
        ),
        height=500,
        template="plotly_dark",
        legend=dict(x=0.02, y=0.98)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        median_fee = _calculate_median_fee_rate(fee_histogram)
        st.metric("📊 Median Fee Rate", f"{median_fee:.1f} sat/vB")
    
    with col2:
        total_transactions = sum(tx_counts)
        st.metric("📦 Total Transactions", f"{total_transactions:,}")
    
    with col3:
        total_size = sum(total_sizes)
        st.metric("💾 Total Size", f"{total_size / 1_000_000:.1f} MB")
    
    with col4:
        if fee_rates:
            max_fee = max(fee_rates)
            st.metric("💰 Highest Fee Rate", f"{max_fee} sat/vB")


def _calculate_average_fee_rate(fee_histogram):
    """Calculate weighted average fee rate"""
    total_weighted_fee = 0
    total_transactions = 0
    
    for bucket in fee_histogram:
        if len(bucket) >= 3:
            fee_rate = bucket[0]
            tx_count = bucket[2]
            total_weighted_fee += fee_rate * tx_count
            total_transactions += tx_count
    
    return total_weighted_fee / total_transactions if total_transactions > 0 else 0


def _calculate_median_fee_rate(fee_histogram):
    """Calculate median fee rate"""
    # Create a list of all fee rates weighted by transaction count
    all_fees = []
    for bucket in fee_histogram:
        if len(bucket) >= 3:
            fee_rate = bucket[0]
            tx_count = bucket[2]
            all_fees.extend([fee_rate] * tx_count)
    
    if not all_fees:
        return 0
    
    all_fees.sort()
    n = len(all_fees)
    if n % 2 == 0:
        return (all_fees[n//2 - 1] + all_fees[n//2]) / 2
    else:
        return all_fees[n//2]


def _calculate_fee_recommendations(fee_histogram):
    """Calculate fee recommendations based on mempool state"""
    if not fee_histogram:
        return {
            "🐌 Low Priority": "N/A",
            "🚀 Medium Priority": "N/A", 
            "⚡ High Priority": "N/A"
        }
    
    # Extract fee rates and transaction counts
    fee_data = []
    for bucket in fee_histogram:
        if len(bucket) >= 3:
            fee_rate = bucket[0]
            tx_count = bucket[2]
            fee_data.append((fee_rate, tx_count))
    
    # Sort by fee rate
    fee_data.sort(key=lambda x: x[0])
    
    # Calculate cumulative transaction counts
    total_transactions = sum(count for _, count in fee_data)
    cumulative = 0
    
    recommendations = {}
    
    for fee_rate, tx_count in fee_data:
        cumulative += tx_count
        percentile = (cumulative / total_transactions) * 100
        
        # Define percentile thresholds for recommendations
        if percentile >= 90 and "⚡ High Priority" not in recommendations:
            recommendations["⚡ High Priority"] = f"{fee_rate}"
        elif percentile >= 70 and "🚀 Medium Priority" not in recommendations:
            recommendations["🚀 Medium Priority"] = f"{fee_rate}"
        elif percentile >= 50 and "🐌 Low Priority" not in recommendations:
            recommendations["🐌 Low Priority"] = f"{fee_rate}"
    
    # Fallback values if not enough data
    if "🐌 Low Priority" not in recommendations:
        recommendations["🐌 Low Priority"] = "1"
    if "🚀 Medium Priority" not in recommendations:
        recommendations["🚀 Medium Priority"] = "10"
    if "⚡ High Priority" not in recommendations:
        recommendations["⚡ High Priority"] = "20"
    
    return recommendations
