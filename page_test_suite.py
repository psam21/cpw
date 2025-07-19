#!/usr/bin/env python3
"""
Comprehensive page-by-page test suite for the Bitcoin Crypto Dashboard.
Tests all page rendering functions and their dependencies.
"""

import sys
import os
import traceback
import pandas as pd
from typing import Dict, List, Any
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class PageTestRunner:
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
        print(f"\n{'='*70}")
        print(f"PAGE TEST SUMMARY")
        print(f"{'='*70}")
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


def setup_streamlit_mock():
    """Set up comprehensive Streamlit mocking"""
    # Mock streamlit module
    import streamlit as st
    
    # Mock key streamlit functions
    st.header = MagicMock()
    st.subheader = MagicMock()
    st.info = MagicMock()
    st.error = MagicMock()
    st.warning = MagicMock()
    st.success = MagicMock()
    st.markdown = MagicMock()
    st.write = MagicMock()
    st.caption = MagicMock()
    st.divider = MagicMock()
    st.columns = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock(), MagicMock()])
    st.selectbox = MagicMock(return_value="30D")
    st.button = MagicMock(return_value=False)
    st.spinner = MagicMock()
    st.stop = MagicMock()
    st.rerun = MagicMock()
    st.metric = MagicMock()
    st.plotly_chart = MagicMock()
    st.progress = MagicMock()
    st.sidebar = MagicMock()
    st.radio = MagicMock(return_value="Why Bitcoin?")
    st.code = MagicMock()
    
    # Mock session state
    st.session_state = {}
    
    return st


def test_bitcoin_education_page():
    """Test Bitcoin Education page"""
    try:
        # Test the page function can be imported and called without Streamlit rendering
        from pages.bitcoin_education import render_why_bitcoin_page
        
        # Create a complete mock environment
        with patch('pages.bitcoin_education.st') as mock_st:
            # Mock all streamlit functions used in the page
            mock_st.header = MagicMock()
            mock_st.info = MagicMock()
            mock_st.markdown = MagicMock()
            mock_st.columns = MagicMock(return_value=[MagicMock(), MagicMock()])
            mock_st.subheader = MagicMock()
            
            # Mock the debug logger to avoid any logging issues
            with patch('pages.bitcoin_education.debug_log_user_action'):
                # Just test that the function can be called without errors
                render_why_bitcoin_page()
                
        return True
    except Exception as e:
        return f"Bitcoin Education page error: {str(e)}"


def test_bitcoin_technical_analysis_page():
    """Test Bitcoin Technical Analysis page"""
    try:
        from pages.bitcoin_technical_analysis import render_bitcoin_ohlc_page
        
        with patch('pages.bitcoin_technical_analysis.st') as mock_st:
            # Mock all streamlit functions
            mock_st.header = MagicMock()
            mock_st.info = MagicMock()
            mock_st.columns = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock(), MagicMock()])
            mock_st.selectbox = MagicMock(return_value="30D")
            mock_st.button = MagicMock(return_value=False)
            mock_st.spinner = MagicMock()
            mock_st.error = MagicMock()
            mock_st.warning = MagicMock()
            mock_st.stop = MagicMock()
            mock_st.rerun = MagicMock()
            mock_st.subheader = MagicMock()
            mock_st.markdown = MagicMock()
            mock_st.metric = MagicMock()
            mock_st.plotly_chart = MagicMock()
            mock_st.progress = MagicMock()
            mock_st.caption = MagicMock()
            mock_st.divider = MagicMock()
            
            # Mock spinner context manager
            spinner_mock = MagicMock()
            spinner_mock.__enter__ = MagicMock(return_value=spinner_mock)
            spinner_mock.__exit__ = MagicMock(return_value=None)
            mock_st.spinner = MagicMock(return_value=spinner_mock)
            
            # Mock the cached functions to return test data
            mock_crypto_data = {
                'bitcoin': {'usd': 45000.0},
                'success_count': 1,
                'total_count': 1
            }
            
            mock_ohlc_data = pd.DataFrame({
                'timestamp': [1640995200000, 1641081600000, 1641168000000],
                'open': [46000.0, 46500.0, 47000.0],
                'high': [47000.0, 47500.0, 48000.0],
                'low': [45500.0, 46000.0, 46500.0],
                'close': [46500.0, 47000.0, 47500.0],
                'datetime': pd.to_datetime([1640995200000, 1641081600000, 1641168000000], unit='ms')
            })
            
            with patch('pages.bitcoin_technical_analysis.cached_get_crypto_prices', return_value=mock_crypto_data):
                with patch('pages.bitcoin_technical_analysis.get_ohlc_data', return_value=mock_ohlc_data):
                    with patch('pages.bitcoin_technical_analysis.debug_log_user_action'):
                        render_bitcoin_ohlc_page()
        return True
    except Exception as e:
        return f"Technical Analysis page error: {str(e)}"


def test_mempool_network_dashboard_page():
    """Test Mempool Network Dashboard page"""
    try:
        # Mock streamlit at the module level
        with patch.dict('sys.modules', {'streamlit': MagicMock()}):
            import streamlit as st
            st.header = MagicMock()
            st.info = MagicMock()
            st.columns = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock(), MagicMock()])
            st.selectbox = MagicMock(return_value=60)
            st.checkbox = MagicMock(return_value=True)
            st.button = MagicMock(return_value=False)
            st.spinner = MagicMock()
            st.success = MagicMock()
            st.warning = MagicMock()
            st.error = MagicMock()
            st.subheader = MagicMock()
            st.markdown = MagicMock()
            st.metric = MagicMock()
            st.plotly_chart = MagicMock()
            st.bar_chart = MagicMock()
            st.caption = MagicMock()
            st.divider = MagicMock()
            
            # Mock spinner context manager
            spinner_mock = MagicMock()
            spinner_mock.__enter__ = MagicMock(return_value=spinner_mock)
            spinner_mock.__exit__ = MagicMock(return_value=None)
            st.spinner = MagicMock(return_value=spinner_mock)
            
            # Mock mempool data
            mock_mempool_data = {
                'fees': {'fastestFee': 15, 'halfHourFee': 12, 'hourFee': 8, 'economyFee': 5},
                'mempool_blocks': [{'blockSize': 1000000, 'blockVSize': 1000000, 'nTx': 2500, 'totalFees': 0.5}],
                'difficulty': {'progressPercent': 45.2, 'estimatedRetargetDate': 1640995200},
                'latest_blocks': [{'height': 720000, 'timestamp': 1640995200, 'tx_count': 2500, 'size': 1000000}],
                'mining_pools': {'pools': [{'poolName': 'Test Pool', 'blockCount': 10}]},
                'fee_histogram': [[1, 100], [5, 200], [10, 300]]
            }
            
            with patch('pages.mempool_network_dashboard.cached_get_mempool_info', return_value=mock_mempool_data):
                from pages.mempool_network_dashboard import render_mempool_page
                render_mempool_page()
        return True
    except Exception as e:
        return f"Mempool Dashboard page error: {str(e)}"


def test_portfolio_calculator_page():
    """Test Portfolio Calculator page"""
    try:
        # Mock streamlit at the module level  
        with patch.dict('sys.modules', {'streamlit': MagicMock()}):
            import streamlit as st
            st.header = MagicMock()
            st.info = MagicMock()
            st.tabs = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock()])
            st.columns = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock(), MagicMock()])
            st.number_input = MagicMock(return_value=1000.0)
            st.text_input = MagicMock(return_value="Test Portfolio")
            st.date_input = MagicMock()
            st.button = MagicMock(return_value=False)
            st.success = MagicMock()
            st.warning = MagicMock()
            st.error = MagicMock()
            st.metric = MagicMock()
            st.dataframe = MagicMock()
            st.download_button = MagicMock()
            st.markdown = MagicMock()
            st.subheader = MagicMock()
            st.caption = MagicMock()
            
            # Mock session state
            st.session_state = {
                'portfolio_holdings': [],
                'portfolio_transactions': [],
                'portfolio_name': 'Test Portfolio'
            }
            
            # Mock tab context managers
            tab_mock = MagicMock()
            tab_mock.__enter__ = MagicMock(return_value=tab_mock)
            tab_mock.__exit__ = MagicMock(return_value=None)
            st.tabs.return_value = [tab_mock, tab_mock, tab_mock]
            
            # Mock crypto prices
            mock_crypto_prices = {
                'prices': {
                    'BTC': 45000.0,
                    'ETH': 3000.0,
                    'BNB': 300.0,
                    'POL': 1.0
                },
                'success_count': 4,
                'total_count': 4
            }
            
            with patch('pages.portfolio_calculator.cached_get_crypto_prices', return_value=mock_crypto_prices):
                from pages.portfolio_calculator import render_portfolio_page
                render_portfolio_page()
        return True
    except Exception as e:
        return f"Portfolio Calculator page error: {str(e)}"


def test_bitcoin_metrics_dashboard_page():
    """Test Bitcoin Metrics Dashboard page"""
    try:
        # Mock streamlit at the module level
        with patch.dict('sys.modules', {'streamlit': MagicMock()}):
            import streamlit as st
            st.header = MagicMock()
            st.info = MagicMock()
            st.tabs = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock(), MagicMock()])
            st.container = MagicMock()
            st.columns = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock()])
            st.metric = MagicMock()
            st.plotly_chart = MagicMock()
            st.warning = MagicMock()
            st.markdown = MagicMock()
            st.subheader = MagicMock()
            st.caption = MagicMock()
            
            # Mock tab context managers
            tab_mock = MagicMock()
            tab_mock.__enter__ = MagicMock(return_value=tab_mock)
            tab_mock.__exit__ = MagicMock(return_value=None)
            st.tabs.return_value = [tab_mock, tab_mock, tab_mock, tab_mock]
            
            from pages.bitcoin_metrics_dashboard import render_bitcoin_metrics_page
            render_bitcoin_metrics_page()
        return True
    except Exception as e:
        return f"Bitcoin Metrics Dashboard page error: {str(e)}"


def test_system_debug_viewer_page():
    """Test System Debug Viewer page"""
    try:
        # Mock streamlit at the module level
        with patch.dict('sys.modules', {'streamlit': MagicMock()}):
            import streamlit as st
            st.header = MagicMock()
            st.info = MagicMock()
            st.columns = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock()])
            st.button = MagicMock(return_value=False)
            st.success = MagicMock()
            st.warning = MagicMock()
            st.metric = MagicMock()
            st.empty = MagicMock()
            st.expander = MagicMock()
            st.json = MagicMock()
            st.text_area = MagicMock()
            st.code = MagicMock()
            st.markdown = MagicMock()
            st.subheader = MagicMock()
            st.caption = MagicMock()
            
            # Mock session state with debug logs
            st.session_state = {
                'debug_logs': [
                    {
                        'timestamp': '2025-07-19T10:00:00',
                        'level': 'INFO',
                        'message': 'Test log message',
                        'context': 'test_context'
                    }
                ]
            }
            
            # Mock expander context manager
            expander_mock = MagicMock()
            expander_mock.__enter__ = MagicMock(return_value=expander_mock)
            expander_mock.__exit__ = MagicMock(return_value=None)
            st.expander = MagicMock(return_value=expander_mock)
            
            from pages.system_debug_viewer import render_debug_logs_page
            render_debug_logs_page()
        return True
    except Exception as e:
        return f"Debug Viewer page error: {str(e)}"


def test_page_functions_exist():
    """Test that all page render functions exist and are callable"""
    pages = [
        ('pages.bitcoin_education', 'render_why_bitcoin_page'),
        ('pages.bitcoin_technical_analysis', 'render_bitcoin_ohlc_page'),
        ('pages.mempool_network_dashboard', 'render_mempool_page'),
        ('pages.portfolio_calculator', 'render_portfolio_page'),
        ('pages.bitcoin_metrics_dashboard', 'render_bitcoin_metrics_page'),
        ('pages.system_debug_viewer', 'render_debug_logs_page')
    ]
    
    missing_functions = []
    for module_name, function_name in pages:
        try:
            module = __import__(module_name, fromlist=[function_name])
            if not hasattr(module, function_name):
                missing_functions.append(f"{module_name}.{function_name}")
            elif not callable(getattr(module, function_name)):
                missing_functions.append(f"{module_name}.{function_name} (not callable)")
        except Exception as e:
            missing_functions.append(f"{module_name}.{function_name} (import error: {str(e)})")
    
    if missing_functions:
        return f"Missing page functions: {', '.join(missing_functions)}"
    return True


def test_page_data_dependencies():
    """Test that page dependencies (data functions) work"""
    try:
        # Test data cache manager functions
        from utils.data_cache_manager import cached_get_mempool_info, cached_get_crypto_prices
        from utils.data_validation import is_valid_data
        
        # Test that functions exist and are callable
        if not callable(cached_get_mempool_info):
            return "cached_get_mempool_info not callable"
        if not callable(cached_get_crypto_prices):
            return "cached_get_crypto_prices not callable"
        if not callable(is_valid_data):
            return "is_valid_data not callable"
        
        return True
    except Exception as e:
        return f"Data dependencies error: {str(e)}"


def test_technical_analysis_functions():
    """Test technical analysis helper functions"""
    try:
        from pages.bitcoin_technical_analysis import _calculate_rsi, _calculate_macd
        
        # Create test data
        test_prices = pd.Series([100, 102, 98, 105, 103, 107, 104, 108, 106, 110, 
                               112, 108, 115, 113, 118, 116, 120, 118, 122, 125])
        
        # Test RSI
        rsi = _calculate_rsi(test_prices, window=14)
        if not isinstance(rsi, pd.Series):
            return f"RSI should return Series, got {type(rsi)}"
        
        # Test MACD  
        macd_line, signal_line, histogram = _calculate_macd(test_prices)
        if not all(isinstance(x, pd.Series) for x in [macd_line, signal_line, histogram]):
            return "MACD should return three Series"
        
        return True
    except Exception as e:
        return f"Technical analysis functions error: {str(e)}"


def main():
    """Run all page tests"""
    print("🚀 Starting comprehensive PAGE-BY-PAGE test suite...")
    print("="*70)
    
    runner = PageTestRunner()
    
    # Test page function existence
    runner.run_test("Page Functions Exist", test_page_functions_exist)
    runner.run_test("Page Data Dependencies", test_page_data_dependencies)
    runner.run_test("Technical Analysis Functions", test_technical_analysis_functions)
    
    # Test each page rendering
    runner.run_test("Bitcoin Education Page", test_bitcoin_education_page)
    runner.run_test("Bitcoin Technical Analysis Page", test_bitcoin_technical_analysis_page)
    runner.run_test("Mempool Network Dashboard Page", test_mempool_network_dashboard_page)
    runner.run_test("Portfolio Calculator Page", test_portfolio_calculator_page)
    runner.run_test("Bitcoin Metrics Dashboard Page", test_bitcoin_metrics_dashboard_page)
    runner.run_test("System Debug Viewer Page", test_system_debug_viewer_page)
    
    # Print results
    success = runner.print_summary()
    
    if success:
        print("\n🎉 All page tests passed! All pages are rendering correctly.")
        return 0
    else:
        print("\n⚠️  Some page tests failed. Check the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
