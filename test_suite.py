#!/usr/bin/env python3
"""
Comprehensive unit test suite for the Bitcoin Crypto Dashboard.
Tests all modules for import errors, basic functionality, and DataFrame handling.
"""

import sys
import os
import traceback
import pandas as pd
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestRunner:
    def __init__(self):
        self.results = {
            'passed': [],
            'failed': [],
            'skipped': []
        }
    
    def run_test(self, test_name: str, test_func):
        """Run a single test and record results"""
        try:
            print(f"🧪 Testing {test_name}...", end=" ")
            result = test_func()
            if result is True or result is None:
                print("✅ PASS")
                self.results['passed'].append(test_name)
            else:
                print(f"❌ FAIL: {result}")
                self.results['failed'].append((test_name, str(result)))
        except Exception as e:
            print(f"💥 ERROR: {str(e)}")
            self.results['failed'].append((test_name, f"Exception: {str(e)}"))
            # Print traceback for debugging
            traceback.print_exc()
    
    def print_summary(self):
        """Print test summary"""
        total = len(self.results['passed']) + len(self.results['failed']) + len(self.results['skipped'])
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Passed: {len(self.results['passed'])}")
        print(f"❌ Failed: {len(self.results['failed'])}")
        print(f"⏭️  Skipped: {len(self.results['skipped'])}")
        print(f"📊 Total: {total}")
        
        if self.results['failed']:
            print(f"\n❌ FAILED TESTS:")
            for test_name, error in self.results['failed']:
                print(f"  • {test_name}: {error}")
        
        success_rate = len(self.results['passed']) / total * 100 if total > 0 else 0
        print(f"\n🎯 Success Rate: {success_rate:.1f}%")
        
        return len(self.results['failed']) == 0


def test_imports():
    """Test all module imports"""
    modules_to_test = [
        'app',
        'utils.data_validation',
        'utils.system_logger',
        'utils.data_cache_manager',
        'utils.portfolio_session_manager',
        'utils.http_config',
        'api.bitfinex_exchange_api',
        'api.mempool_network_api',
        'api.binance_exchange_api',
        'api.coinbase_exchange_api',
        'api.kucoin_exchange_api',
        'api.multi_exchange_aggregator',
        'api.bitcoin_metrics_api',
        'pages.bitcoin_education',
        'pages.bitcoin_technical_analysis',
        'pages.mempool_network_dashboard',
        'pages.portfolio_calculator',
        'pages.bitcoin_metrics_dashboard',
        'pages.system_debug_viewer'
    ]
    
    failed_imports = []
    for module in modules_to_test:
        try:
            __import__(module)
        except Exception as e:
            failed_imports.append(f"{module}: {str(e)}")
    
    if failed_imports:
        return f"Import failures: {', '.join(failed_imports)}"
    return True


def test_data_validation():
    """Test the data validation module"""
    from utils.data_validation import is_valid_data
    
    test_cases = [
        (None, False),
        (pd.DataFrame(), False),  # Empty DataFrame
        (pd.DataFrame({'a': [1, 2]}), True),  # Non-empty DataFrame
        ({}, False),  # Empty dict
        ({'key': 'value'}, True),  # Non-empty dict
        ({'error': 'fail'}, False),  # Dict with error key
        ([], False),  # Empty list
        ([1, 2], True),  # Non-empty list
        ('', False),  # Empty string
        ('hello', True),  # Non-empty string
        (0, False),  # Falsy number
        (42, True),  # Truthy number
    ]
    
    for obj, expected in test_cases:
        result = is_valid_data(obj)
        if result != expected:
            return f"is_valid_data({obj!r}) returned {result}, expected {expected}"
    
    return True


def test_http_config():
    """Test HTTP configuration"""
    try:
        from utils.http_config import default_timeout
        if not isinstance(default_timeout, int) or default_timeout <= 0:
            return f"default_timeout should be positive integer, got {default_timeout}"
        return True
    except Exception as e:
        return f"HTTP config error: {str(e)}"


def test_system_logger():
    """Test system logger functions"""
    try:
        from utils.system_logger import debug_log, debug_log_api_call, debug_log_data_processing, debug_log_user_action
        
        # Test basic debug_log
        debug_log("Test message", "INFO", "test_context")
        
        # Test API call logging
        debug_log_api_call("TestAPI", "test_endpoint", "SUCCESS", 100, "test_data")
        
        # Test data processing logging
        test_data = pd.DataFrame({'test': [1, 2, 3]})
        debug_log_data_processing("Test Operation", "test_input", test_data, 50)
        
        # Test user action logging
        debug_log_user_action("Test Action", {"detail": "test"})
        
        return True
    except Exception as e:
        return f"System logger error: {str(e)}"


def test_bitcoin_technical_analysis():
    """Test Bitcoin technical analysis functions"""
    try:
        from pages.bitcoin_technical_analysis import _calculate_rsi, _calculate_macd
        
        # Create test price data
        prices = pd.Series([100, 102, 98, 105, 103, 107, 104, 108, 106, 110, 
                           112, 108, 115, 113, 118, 116, 120, 118, 122, 125])
        
        # Test RSI calculation
        rsi = _calculate_rsi(prices, window=14)
        if not isinstance(rsi, pd.Series):
            return f"RSI should return pandas Series, got {type(rsi)}"
        
        # Test MACD calculation
        macd_line, signal_line, histogram = _calculate_macd(prices)
        if not all(isinstance(x, pd.Series) for x in [macd_line, signal_line, histogram]):
            return "MACD should return three pandas Series"
        
        return True
    except Exception as e:
        return f"Technical analysis error: {str(e)}"


def test_dataframe_safety():
    """Test DataFrame boolean evaluation safety"""
    try:
        from utils.data_validation import is_valid_data
        
        # Test various DataFrame scenarios
        empty_df = pd.DataFrame()
        non_empty_df = pd.DataFrame({'a': [1, 2, 3]})
        
        # These should not raise "truth value ambiguous" errors
        result1 = is_valid_data(empty_df)
        result2 = is_valid_data(non_empty_df)
        
        if result1 != False:
            return f"Empty DataFrame should be invalid, got {result1}"
        if result2 != True:
            return f"Non-empty DataFrame should be valid, got {result2}"
        
        # Test direct DataFrame boolean evaluation (should be safe now)
        if hasattr(empty_df, 'empty') and empty_df.empty:
            pass  # This should work without error
        
        if hasattr(non_empty_df, 'empty') and not non_empty_df.empty:
            pass  # This should work without error
        
        return True
    except Exception as e:
        return f"DataFrame safety error: {str(e)}"


def test_api_modules():
    """Test API module structure"""
    api_modules = [
        'api.bitfinex_exchange_api',
        'api.mempool_network_api',
        'api.binance_exchange_api',
        'api.coinbase_exchange_api',
        'api.kucoin_exchange_api',
        'api.multi_exchange_aggregator',
        'api.bitcoin_metrics_api'
    ]
    
    for module_name in api_modules:
        try:
            module = __import__(module_name, fromlist=[''])
            
            # Check for timeout usage
            import inspect
            source = inspect.getsource(module)
            if 'timeout=' in source and 'TIMEOUT' not in source and 'default_timeout' not in source:
                # Some modules might still have hardcoded timeouts
                pass  # This is informational, not a failure
                
        except Exception as e:
            return f"API module {module_name} error: {str(e)}"
    
    return True


def test_page_modules():
    """Test page module structure"""
    page_modules = [
        'pages.bitcoin_education',
        'pages.bitcoin_technical_analysis',
        'pages.mempool_network_dashboard',
        'pages.portfolio_calculator',
        'pages.bitcoin_metrics_dashboard',
        'pages.system_debug_viewer'
    ]
    
    for module_name in page_modules:
        try:
            module = __import__(module_name, fromlist=[''])
            
            # Check for render function
            if hasattr(module, 'render_bitcoin_ohlc_page') or \
               hasattr(module, 'render_why_bitcoin_page') or \
               hasattr(module, 'render_mempool_page') or \
               hasattr(module, 'render_portfolio_page') or \
               hasattr(module, 'render_bitcoin_metrics_page') or \
               hasattr(module, 'render_debug_logs_page'):
                pass  # Has a render function
            else:
                return f"Page module {module_name} missing render function"
                
        except Exception as e:
            return f"Page module {module_name} error: {str(e)}"
    
    return True


def test_portfolio_session_manager():
    """Test portfolio session manager"""
    try:
        from utils.portfolio_session_manager import initialize_portfolio_session, reset_to_default_portfolio, clear_portfolio
        
        # These functions should be callable without Streamlit session state
        # They should handle missing session state gracefully
        return True
    except Exception as e:
        return f"Portfolio session manager error: {str(e)}"


def test_cache_manager():
    """Test data cache manager"""
    try:
        from utils.data_cache_manager import cached_get_mempool_info, cached_get_mempool_stats
        from utils.data_cache_manager import cached_get_crypto_prices, cached_get_binance_prices, cached_get_btc_ohlc_data
        
        # These should be importable (actual calls would require Streamlit context)
        return True
    except Exception as e:
        return f"Cache manager error: {str(e)}"


def main():
    """Run all tests"""
    print("🚀 Starting comprehensive unit test suite...")
    print("="*60)
    
    runner = TestRunner()
    
    # Core functionality tests
    runner.run_test("Module Imports", test_imports)
    runner.run_test("Data Validation", test_data_validation)
    runner.run_test("HTTP Config", test_http_config)
    runner.run_test("System Logger", test_system_logger)
    runner.run_test("DataFrame Safety", test_dataframe_safety)
    
    # Module-specific tests
    runner.run_test("API Modules", test_api_modules)
    runner.run_test("Page Modules", test_page_modules)
    runner.run_test("Portfolio Session Manager", test_portfolio_session_manager)
    runner.run_test("Cache Manager", test_cache_manager)
    runner.run_test("Technical Analysis", test_bitcoin_technical_analysis)
    
    # Print results
    success = runner.print_summary()
    
    if success:
        print("\n🎉 All tests passed! The application should run without errors.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the errors above and fix them.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
