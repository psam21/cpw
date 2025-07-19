"""
Debug logging utilities for the Bitcoin dashboard application.
Provides comprehensive session instrumentation and production debugging.
"""
import streamlit as st
from datetime import datetime


def debug_log(message, level="INFO", context=None, data=None):
    """Enhanced debug logging with full session instrumentation"""
    if 'debug_logs' not in st.session_state:
        st.session_state.debug_logs = []
        # Log session initialization
        session_start = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            'level': 'SYSTEM',
            'message': '🚀 Debug session initialized',
            'context': 'session_start',
            'session_id': id(st.session_state),
            'user_agent': st.context.headers.get('User-Agent', 'Unknown') if hasattr(st, 'context') and hasattr(st.context, 'headers') else 'Unknown',
            'timestamp_full': datetime.now().isoformat(),
            'log_sequence': 1
        }
        st.session_state.debug_logs.append(session_start)
    
    # Enhanced timestamp with full datetime
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    timestamp_full = datetime.now().isoformat()
    
    # Build comprehensive log entry
    log_entry = {
        'timestamp': timestamp,
        'timestamp_full': timestamp_full,
        'level': level,
        'message': str(message),
        'context': context,
        'session_id': id(st.session_state),
        'log_sequence': len(st.session_state.debug_logs) + 1
    }
    
    # Add data payload if provided
    if data is not None:
        log_entry['data'] = data
    
    # Add system context for certain levels
    if level in ['ERROR', 'SYSTEM', 'WARNING']:
        try:
            import psutil
            import platform
            log_entry['system_info'] = {
                'platform': platform.system(),
                'python_version': platform.python_version(),
                'memory_usage_mb': psutil.Process().memory_info().rss / 1024 / 1024,
                'cpu_percent': psutil.cpu_percent(interval=None)
            }
        except ImportError:
            # psutil not available in this environment
            import platform
            log_entry['system_info'] = {
                'platform': platform.system(),
                'python_version': platform.python_version(),
                'memory_usage_mb': 'unavailable',
                'cpu_percent': 'unavailable'
            }
        except Exception:
            log_entry['system_info'] = 'unavailable'
    
    # Add stack trace for errors
    if level == 'ERROR':
        try:
            import traceback
            log_entry['stack_trace'] = traceback.format_stack()
        except:
            log_entry['stack_trace'] = 'unavailable'
    
    st.session_state.debug_logs.append(log_entry)
    
    # Keep last 2000 entries for full session history (increased from 1000)
    if len(st.session_state.debug_logs) > 2000:
        st.session_state.debug_logs = st.session_state.debug_logs[-2000:]
    
    # Enhanced console logging
    console_msg = f"[{timestamp}] {level}: {message}"
    if context:
        console_msg += f" | Context: {context}"
    if data:
        console_msg += f" | Data: {str(data)[:100]}..."
    print(console_msg)


def debug_log_api_call(api_name, endpoint, status, response_time=None, response_data=None, error=None):
    """Specialized logging for API calls with full instrumentation"""
    from datetime import datetime
    
    context_data = {
        'api_name': api_name,
        'endpoint': endpoint,
        'status': status,
        'response_time_ms': response_time,
        'timestamp_iso': datetime.now().isoformat()
    }
    
    if response_data:
        context_data['response_preview'] = str(response_data)[:200] + "..." if len(str(response_data)) > 200 else str(response_data)
    
    if error:
        context_data['error_details'] = str(error)
        debug_log(f"🌐 API {api_name} FAILED: {endpoint} - {error}", "ERROR", f"api_{api_name.lower()}", context_data)
    else:
        debug_log(f"🌐 API {api_name} SUCCESS: {endpoint} ({response_time}ms)", "SUCCESS", f"api_{api_name.lower()}", context_data)


def debug_log_data_processing(operation, input_data, output_data, processing_time=None):
    """Specialized logging for data processing operations"""
    from datetime import datetime
    
    context_data = {
        'operation': operation,
        'input_size': len(str(input_data)) if input_data else 0,
        'output_size': len(str(output_data)) if output_data else 0,
        'processing_time_ms': processing_time,
        'timestamp_iso': datetime.now().isoformat()
    }
    
    debug_log(f"⚙️ DATA PROCESSING: {operation}", "DATA", f"processing_{operation.lower().replace(' ', '_')}", context_data)


def debug_log_user_action(action, details=None):
    """Log user interactions and navigation"""
    from datetime import datetime
    
    context_data = {
        'action': action,
        'details': details,
        'timestamp_iso': datetime.now().isoformat()
    }
    
    debug_log(f"👤 USER ACTION: {action}", "INFO", "user_interaction", context_data)


def clear_debug_logs():
    """Clear debug logs with proper logging of the action"""
    log_count = len(st.session_state.debug_logs) if 'debug_logs' in st.session_state else 0
    
    if 'debug_logs' in st.session_state:
        st.session_state.debug_logs = []
    
    # Log the clear action
    debug_log(f"🗑️ Debug logs cleared (removed {log_count} entries)", "SYSTEM", "log_management")
    print(f"[SYSTEM] Debug logs cleared - removed {log_count} entries")
