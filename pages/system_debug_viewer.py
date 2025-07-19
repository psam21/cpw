"""
Debug Logs and System Information page.
"""
import streamlit as st
import platform
import sys
from datetime import datetime
import json
from utils.system_logger import debug_log, debug_log_user_action

# Optional psutil import for system stats
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


def render_debug_logs_page():
    """Render the Debug Logs and System Information page"""
    debug_log_user_action("Viewing Debug Logs page")
    
    st.header("🔧 Debug Logs & System Information")
    st.info("🔍 Monitor application performance and troubleshoot issues")

    # Control buttons
    col_clear, col_refresh, col_download = st.columns(3)
    
    with col_clear:
        if st.button("🗑️ Clear Logs", type="secondary"):
            st.session_state.debug_logs = []
            debug_log("🗑️ Debug logs cleared by user", "INFO", "logs_cleared")
            st.success("✅ Debug logs cleared")
            st.rerun()
    
    with col_refresh:
        if st.button("🔄 Refresh", type="secondary"):
            debug_log("🔄 Debug page refreshed by user", "INFO", "debug_refresh")
            st.rerun()
    
    with col_download:
        if st.session_state.get('debug_logs'):
            log_data = _prepare_logs_for_download()
            st.download_button(
                "📥 Download Logs",
                data=log_data,
                file_name=f"debug_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                type="secondary"
            )
    
    # === SYSTEM INFORMATION ===
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("💻 System Information")
    _render_system_info()
    
    # === APPLICATION STATUS ===
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📊 Application Status")
    _render_app_status()
    
    # === DEBUG LOGS ===
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📋 Debug Logs")
    _render_debug_logs()
    
    # === LOG STATISTICS ===
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📈 Log Statistics")
    _render_log_statistics()
    
    # === SESSION STATE VIEWER ===
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🔍 Session State Viewer")
    _render_session_state()


def _render_system_info():
    """Render system information section"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("#### 🖥️ Platform")
        st.markdown(f"**OS**: {platform.system()}")
        st.markdown(f"**Version**: {platform.release()}")
        st.markdown(f"**Architecture**: {platform.machine()}")
        st.markdown(f"**Processor**: {platform.processor()}")
    
    with col2:
        st.markdown("#### 🐍 Python")
        st.markdown(f"**Version**: {sys.version.split()[0]}")
        st.markdown(f"**Executable**: {sys.executable}")
        st.markdown(f"**Path**: {sys.path[0]}")
    
    with col3:
        st.markdown("#### 💾 Memory")
        if PSUTIL_AVAILABLE:
            memory = psutil.virtual_memory()
            st.markdown(f"**Total**: {memory.total / (1024**3):.1f} GB")
            st.markdown(f"**Available**: {memory.available / (1024**3):.1f} GB")
            st.markdown(f"**Used**: {memory.percent:.1f}%")
            
            # Memory usage bar
            st.progress(memory.percent / 100, text=f"Memory: {memory.percent:.1f}%")
        else:
            st.markdown("**Status**: psutil not available")
            st.markdown("**Info**: Install psutil for detailed memory stats")
    
    with col4:
        st.markdown("#### 💽 Disk")
        if PSUTIL_AVAILABLE:
            disk = psutil.disk_usage('/')
            st.markdown(f"**Total**: {disk.total / (1024**3):.1f} GB")
            st.markdown(f"**Free**: {disk.free / (1024**3):.1f} GB")
            st.markdown(f"**Used**: {(disk.used / disk.total) * 100:.1f}%")
            
            # Disk usage bar
            disk_percent = (disk.used / disk.total) * 100
            st.progress(disk_percent / 100, text=f"Disk: {disk_percent:.1f}%")
        else:
            st.markdown("**Status**: psutil not available")
            st.markdown("**Info**: Install psutil for detailed disk stats")


def _render_app_status():
    """Render application status section"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📊 Session Information")
        
        # Calculate session duration
        if 'session_start_time' not in st.session_state:
            st.session_state.session_start_time = datetime.now()
        
        session_duration = datetime.now() - st.session_state.session_start_time
        hours, remainder = divmod(session_duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        st.markdown(f"**Duration**: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
        st.markdown(f"**Start Time**: {st.session_state.session_start_time.strftime('%H:%M:%S')}")
        
        # Session state size
        session_size = sys.getsizeof(str(st.session_state))
        st.markdown(f"**Session Size**: {session_size:,} bytes")
    
    with col2:
        st.markdown("#### 🔄 Cache Information")
        
        # Cache stats (approximate based on session state)
        cache_items = len([k for k in st.session_state.keys() if 'cache' in k.lower()])
        st.markdown(f"**Cached Items**: {cache_items}")
        
        # Debug logs count
        debug_logs_count = len(st.session_state.get('debug_logs', []))
        st.markdown(f"**Debug Entries**: {debug_logs_count:,}")
        
        # Portfolio items
        portfolio_size = len(st.session_state.get('portfolio', {}))
        st.markdown(f"**Portfolio Items**: {portfolio_size}")
    
    with col3:
        st.markdown("#### ⚡ Performance Metrics")
        
        # Calculate approximate load time based on logs
        api_logs = [log for log in st.session_state.get('debug_logs', []) 
                   if log.get('category') == 'api_call']
        
        if api_logs:
            recent_api_logs = [log for log in api_logs 
                             if (datetime.now() - datetime.fromisoformat(log['timestamp'])).total_seconds() < 300]
            st.markdown(f"**Recent API Calls**: {len(recent_api_logs)}")
        else:
            st.markdown(f"**Recent API Calls**: 0")
        
        # Error count
        error_logs = [log for log in st.session_state.get('debug_logs', []) 
                     if log.get('level') == 'ERROR']
        st.markdown(f"**Total Errors**: {len(error_logs)}")
        
        # Success rate
        success_logs = [log for log in st.session_state.get('debug_logs', []) 
                       if log.get('level') == 'SUCCESS']
        total_logs = len(st.session_state.get('debug_logs', []))
        success_rate = (len(success_logs) / total_logs * 100) if total_logs > 0 else 0
        st.markdown(f"**Success Rate**: {success_rate:.1f}%")


def _render_debug_logs():
    """Render debug logs section"""
    debug_logs = st.session_state.get('debug_logs', [])
    
    if not debug_logs:
        st.info("📝 No debug logs available. Use the application to generate logs.")
        return
    
    # Log filtering
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        log_levels = list(set(log.get('level', 'INFO') for log in debug_logs))
        selected_levels = st.multiselect(
            "Filter by Level",
            options=log_levels,
            default=log_levels,
            key="log_level_filter"
        )
    
    with col_filter2:
        categories = list(set(log.get('category', 'general') for log in debug_logs))
        selected_categories = st.multiselect(
            "Filter by Category", 
            options=categories,
            default=categories,
            key="log_category_filter"
        )
    
    with col_filter3:
        max_logs = st.number_input(
            "Max Logs to Show",
            min_value=10,
            max_value=1000,
            value=100,
            step=10
        )
    
    # Filter logs
    filtered_logs = [
        log for log in debug_logs 
        if log.get('level', 'INFO') in selected_levels 
        and log.get('category', 'general') in selected_categories
    ]
    
    # Sort by timestamp (newest first) and limit
    filtered_logs = sorted(filtered_logs, key=lambda x: x.get('timestamp', ''), reverse=True)[:max_logs]
    
    if not filtered_logs:
        st.warning("⚠️ No logs match the selected filters")
        return
    
    # Display logs
    st.markdown(f"**Showing {len(filtered_logs)} of {len(debug_logs)} logs**")
    
    # Logs container with scrolling
    with st.container():
        for i, log in enumerate(filtered_logs):
            timestamp = log.get('timestamp', 'Unknown')
            level = log.get('level', 'INFO')
            message = log.get('message', 'No message')
            category = log.get('category', 'general')
            
            # Format timestamp
            try:
                dt = datetime.fromisoformat(timestamp)
                formatted_time = dt.strftime('%H:%M:%S')
            except:
                formatted_time = timestamp
            
            # Color coding for different log levels
            if level == 'ERROR':
                st.error(f"🔴 **{formatted_time}** [{category}] {message}")
            elif level == 'WARNING':
                st.warning(f"🟡 **{formatted_time}** [{category}] {message}")
            elif level == 'SUCCESS':
                st.success(f"🟢 **{formatted_time}** [{category}] {message}")
            else:
                st.info(f"ℹ️ **{formatted_time}** [{category}] {message}")
            
            # Add separator for readability
            if i < len(filtered_logs) - 1:
                st.markdown("---")


def _render_log_statistics():
    """Render log statistics section"""
    debug_logs = st.session_state.get('debug_logs', [])
    
    if not debug_logs:
        st.info("📝 No logs available for statistics")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📊 Log Level Distribution")
        
        level_counts = {}
        for log in debug_logs:
            level = log.get('level', 'INFO')
            level_counts[level] = level_counts.get(level, 0) + 1
        
        for level, count in sorted(level_counts.items()):
            percentage = (count / len(debug_logs)) * 100
            st.markdown(f"**{level}**: {count} ({percentage:.1f}%)")
    
    with col2:
        st.markdown("#### 🏷️ Category Distribution")
        
        category_counts = {}
        for log in debug_logs:
            category = log.get('category', 'general')
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Show top 5 categories
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        for category, count in sorted_categories:
            percentage = (count / len(debug_logs)) * 100
            st.markdown(f"**{category}**: {count} ({percentage:.1f}%)")
    
    with col3:
        st.markdown("#### ⏰ Time Distribution")
        
        # Group logs by hour
        hour_counts = {}
        for log in debug_logs:
            try:
                timestamp = log.get('timestamp', '')
                dt = datetime.fromisoformat(timestamp)
                hour = dt.hour
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
            except:
                continue
        
        if hour_counts:
            # Show current hour and peak hour
            current_hour = datetime.now().hour
            current_hour_count = hour_counts.get(current_hour, 0)
            peak_hour = max(hour_counts.items(), key=lambda x: x[1])
            
            st.markdown(f"**Current Hour ({current_hour}:00)**: {current_hour_count} logs")
            st.markdown(f"**Peak Hour ({peak_hour[0]}:00)**: {peak_hour[1]} logs")
        else:
            st.markdown("**No time data available**")


def _render_session_state():
    """Render session state viewer"""
    # Filter sensitive information
    safe_keys = [k for k in st.session_state.keys() 
                 if not k.startswith('_') and k != 'debug_logs']
    
    if not safe_keys:
        st.info("📝 No session state data to display")
        return
    
    # Session state overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Session State Overview")
        st.markdown(f"**Total Keys**: {len(st.session_state.keys())}")
        st.markdown(f"**Safe Keys**: {len(safe_keys)}")
        st.markdown(f"**Hidden Keys**: {len(st.session_state.keys()) - len(safe_keys)}")
    
    with col2:
        st.markdown("#### 🔍 Quick Stats")
        
        # Count different types of data
        portfolio_keys = [k for k in safe_keys if 'portfolio' in k.lower()]
        cache_keys = [k for k in safe_keys if 'cache' in k.lower()]
        
        st.markdown(f"**Portfolio Keys**: {len(portfolio_keys)}")
        st.markdown(f"**Cache Keys**: {len(cache_keys)}")
    
    # Expandable session state viewer
    with st.expander("🔍 View Session State Details"):
        for key in sorted(safe_keys):
            value = st.session_state[key]
            
            # Truncate large values for display
            if isinstance(value, (dict, list)) and len(str(value)) > 200:
                display_value = f"{type(value).__name__} with {len(value)} items"
            elif isinstance(value, str) and len(value) > 200:
                display_value = value[:200] + "..."
            else:
                display_value = str(value)
            
            st.markdown(f"**{key}**: `{display_value}`")


def _prepare_logs_for_download():
    """Prepare debug logs for download"""
    debug_logs = st.session_state.get('debug_logs', [])
    
    # Create a structured export
    export_data = {
        'export_timestamp': datetime.now().isoformat(),
        'total_logs': len(debug_logs),
        'system_info': {
            'platform': platform.system(),
            'python_version': sys.version.split()[0],
            'memory_usage': psutil.virtual_memory().percent if PSUTIL_AVAILABLE else 'N/A'
        },
        'logs': debug_logs
    }
    
    return json.dumps(export_data, indent=2, default=str)
