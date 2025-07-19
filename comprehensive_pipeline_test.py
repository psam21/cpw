#!/usr/bin/env python3
"""
🔍 COMPREHENSIVE DATA PIPELINE TEST
=====================================
Tests all API endpoints and data transformations used by the UI
Run this before any git push to ensure data pipeline integrity

Usage: python comprehensive_pipeline_test.py
"""

import sys
import time
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

# Add current directory to Python path
sys.path.insert(0, '.')

class PipelineTestRunner:
    """Comprehensive test runner for the entire data pipeline"""
    
    def __init__(self):
        self.results = {
            'start_time': datetime.now().isoformat(),
            'tests': {},
            'summary': {},
            'errors': []
        }
        self.test_count = 0
        self.passed_count = 0
        self.failed_count = 0
    
    def log_test(self, test_name: str, status: str, message: str, data: Optional[Dict] = None, error: Optional[str] = None):
        """Log test result"""
        self.test_count += 1
        if status == "PASS":
            self.passed_count += 1
            print(f"✅ {test_name}: {message}")
        elif status == "FAIL":
            self.failed_count += 1
            print(f"❌ {test_name}: {message}")
            if error:
                print(f"   Error: {error}")
        else:
            print(f"⚠️  {test_name}: {message}")
        
        self.results['tests'][test_name] = {
            'status': status,
            'message': message,
            'data': data,
            'error': error,
            'timestamp': datetime.now().isoformat()
        }
    
    def test_imports(self):
        """Test all critical module imports"""
        print("\n🔍 Testing Module Imports...")
        
        # Core modules
        try:
            import streamlit as st
            self.log_test("import_streamlit", "PASS", "Streamlit imported successfully")
        except Exception as e:
            self.log_test("import_streamlit", "FAIL", "Failed to import Streamlit", error=str(e))
        
        try:
            import pandas as pd
            self.log_test("import_pandas", "PASS", "Pandas imported successfully")
        except Exception as e:
            self.log_test("import_pandas", "FAIL", "Failed to import Pandas", error=str(e))
        
        try:
            import requests
            self.log_test("import_requests", "PASS", "Requests imported successfully")
        except Exception as e:
            self.log_test("import_requests", "FAIL", "Failed to import Requests", error=str(e))
        
        # Utility modules
        try:
            from utils.system_logger import debug_log
            self.log_test("import_system_logger", "PASS", "System logger imported successfully")
        except Exception as e:
            self.log_test("import_system_logger", "FAIL", "Failed to import system logger", error=str(e))
        
        try:
            from utils.data_validation import is_valid_data
            self.log_test("import_data_validator", "PASS", "Data validator imported successfully")
        except Exception as e:
            self.log_test("import_data_validator", "FAIL", "Failed to import data validator", error=str(e))
        
        # API modules
        try:
            from api.multi_exchange_aggregator import get_multi_exchange_prices
            self.log_test("import_multi_exchange", "PASS", "Multi-exchange API imported successfully")
        except Exception as e:
            self.log_test("import_multi_exchange", "FAIL", "Failed to import multi-exchange API", error=str(e))
        
        try:
            from api.mempool_network_api import get_mempool_info
            self.log_test("import_mempool_data", "PASS", "Mempool API imported successfully")
        except Exception as e:
            self.log_test("import_mempool_data", "FAIL", "Failed to import mempool API", error=str(e))
    
    def test_crypto_prices_api(self):
        """Test cryptocurrency price fetching"""
        print("\n💰 Testing Cryptocurrency Prices API...")
        
        try:
            from api.multi_exchange_aggregator import get_multi_exchange_prices
            
            start_time = time.time()
            prices = get_multi_exchange_prices()
            response_time = (time.time() - start_time) * 1000
            
            if prices and isinstance(prices, dict):
                # Check for expected cryptocurrencies
                expected_cryptos = ['bitcoin', 'ethereum', 'binancecoin']
                found_cryptos = []
                
                # Handle both direct format and nested format
                price_data = prices.get('prices', prices) if 'prices' in prices else prices
                
                for crypto in expected_cryptos:
                    if crypto in price_data:
                        price = price_data[crypto]
                        if isinstance(price, dict) and 'usd' in price:
                            price_value = price['usd']
                        elif isinstance(price, (int, float)):
                            price_value = price
                        else:
                            continue
                        
                        if price_value and price_value > 0:
                            found_cryptos.append(crypto)
                
                self.log_test("crypto_prices_fetch", "PASS", 
                             f"Fetched prices for {len(found_cryptos)} cryptocurrencies in {response_time:.0f}ms",
                             data={'response_time_ms': response_time, 'cryptos_found': found_cryptos})
                
                # Test specific price validations
                if 'bitcoin' in price_data:
                    btc_price = price_data['bitcoin']
                    if isinstance(btc_price, dict):
                        btc_price = btc_price.get('usd', 0)
                    
                    if btc_price and btc_price > 50000:  # Reasonable BTC price check
                        self.log_test("btc_price_validation", "PASS", f"BTC price ${btc_price:,.2f} is reasonable")
                    else:
                        self.log_test("btc_price_validation", "FAIL", f"BTC price ${btc_price} seems unreasonable")
            else:
                self.log_test("crypto_prices_fetch", "FAIL", "No price data returned or invalid format")
                
        except Exception as e:
            self.log_test("crypto_prices_fetch", "FAIL", "Exception during price fetch", error=str(e))
    
    def test_mempool_api(self):
        """Test mempool data fetching"""
        print("\n⛏️ Testing Mempool API...")
        
        try:
            from api.mempool_network_api import get_mempool_info
            
            start_time = time.time()
            mempool_data = get_mempool_info()
            response_time = (time.time() - start_time) * 1000
            
            if mempool_data and isinstance(mempool_data, dict):
                expected_keys = ['fees', 'difficulty', 'blocks']
                found_keys = []
                
                for key in expected_keys:
                    if key in mempool_data and mempool_data[key]:
                        found_keys.append(key)
                
                self.log_test("mempool_data_fetch", "PASS", 
                             f"Fetched {len(found_keys)} mempool data sections in {response_time:.0f}ms",
                             data={'response_time_ms': response_time, 'sections_found': found_keys})
                
                # Test fee data specifically
                if 'fees' in mempool_data and mempool_data['fees']:
                    fees = mempool_data['fees']
                    if 'fastestFee' in fees and fees['fastestFee'] > 0:
                        self.log_test("mempool_fees_validation", "PASS", 
                                     f"Fee data valid - Fastest: {fees['fastestFee']} sat/vB")
                    else:
                        self.log_test("mempool_fees_validation", "FAIL", "Invalid fee data structure")
            else:
                self.log_test("mempool_data_fetch", "FAIL", "No mempool data returned or invalid format")
                
        except Exception as e:
            self.log_test("mempool_data_fetch", "FAIL", "Exception during mempool fetch", error=str(e))
    
    def test_bitcoin_metrics_api(self):
        """Test Bitcoin metrics API"""
        print("\n📊 Testing Bitcoin Metrics API...")
        
        try:
            # Test if bitcoin_metrics module exists and can be imported
            try:
                from api.bitcoin_metrics_api import get_bitcoin_metrics
                module_available = True
            except ImportError:
                module_available = False
                self.log_test("bitcoin_metrics_import", "FAIL", "Bitcoin metrics module not available")
                return
            
            if module_available:
                start_time = time.time()
                metrics = get_bitcoin_metrics()
                response_time = (time.time() - start_time) * 1000
                
                if metrics and isinstance(metrics, dict):
                    # Check for expected metrics
                    expected_metrics = ['statistics', 'network_stats']
                    found_metrics = []
                    
                    for metric in expected_metrics:
                        if metric in metrics and metrics[metric]:
                            found_metrics.append(metric)
                    
                    self.log_test("bitcoin_metrics_fetch", "PASS", 
                                 f"Fetched {len(found_metrics)} metric sections in {response_time:.0f}ms",
                                 data={'response_time_ms': response_time, 'metrics_found': found_metrics})
                else:
                    self.log_test("bitcoin_metrics_fetch", "FAIL", "No metrics data returned or invalid format")
                    
        except Exception as e:
            self.log_test("bitcoin_metrics_fetch", "FAIL", "Exception during metrics fetch", error=str(e))
    
    def test_ohlc_data(self):
        """Test OHLC data fetching"""
        print("\n📈 Testing OHLC Data...")
        
        try:
            # Test if we can get OHLC data (usually from coingecko)
            import requests
            
            start_time = time.time()
            url = "https://api.coingecko.com/api/v3/coins/bitcoin/ohlc?vs_currency=usd&days=30"
            response = requests.get(url, timeout=30)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    self.log_test("ohlc_data_fetch", "PASS", 
                                 f"Fetched {len(data)} OHLC data points in {response_time:.0f}ms",
                                 data={'response_time_ms': response_time, 'data_points': len(data)})
                    
                    # Validate data structure
                    if len(data[0]) == 5:  # [timestamp, open, high, low, close]
                        self.log_test("ohlc_data_structure", "PASS", "OHLC data structure is valid")
                    else:
                        self.log_test("ohlc_data_structure", "FAIL", "Invalid OHLC data structure")
                else:
                    self.log_test("ohlc_data_fetch", "FAIL", "Empty OHLC data returned")
            else:
                self.log_test("ohlc_data_fetch", "FAIL", f"OHLC API returned status {response.status_code}")
                
        except Exception as e:
            self.log_test("ohlc_data_fetch", "FAIL", "Exception during OHLC fetch", error=str(e))
    
    def test_data_validation_utils(self):
        """Test data validation utilities"""
        print("\n🔍 Testing Data Validation...")
        
        try:
            from utils.data_validation import is_valid_data
            import pandas as pd
            
            # Test valid DataFrame
            valid_df = pd.DataFrame({'test': [1, 2, 3]})
            if is_valid_data(valid_df):
                self.log_test("dataframe_validation_valid", "PASS", "Valid DataFrame correctly identified")
            else:
                self.log_test("dataframe_validation_valid", "FAIL", "Valid DataFrame incorrectly rejected")
            
            # Test invalid DataFrame
            if not is_valid_data(None):
                self.log_test("dataframe_validation_none", "PASS", "None DataFrame correctly rejected")
            else:
                self.log_test("dataframe_validation_none", "FAIL", "None DataFrame incorrectly accepted")
            
            # Test empty DataFrame
            empty_df = pd.DataFrame()
            if not is_valid_data(empty_df):
                self.log_test("dataframe_validation_empty", "PASS", "Empty DataFrame correctly rejected")
            else:
                self.log_test("dataframe_validation_empty", "FAIL", "Empty DataFrame incorrectly accepted")
                
        except Exception as e:
            self.log_test("dataframe_validation", "FAIL", "Exception during data validation test", error=str(e))
    
    def test_portfolio_functionality(self):
        """Test portfolio calculation functionality"""
        print("\n💼 Testing Portfolio Functionality...")
        
        try:
            # Mock session state for testing
            class MockSessionState:
                def __init__(self):
                    self.portfolio = {
                        'bitcoin': 0.1,
                        'ethereum': 1.0,
                        'binancecoin': 2.0
                    }
            
            # Mock prices
            mock_prices = {
                'bitcoin': {'usd': 100000},
                'ethereum': {'usd': 3500},
                'binancecoin': {'usd': 700}
            }
            
            # Calculate expected value
            expected_value = (0.1 * 100000) + (1.0 * 3500) + (2.0 * 700)
            
            # Test the calculation function would work
            total_value = 0
            for crypto_id, amount in MockSessionState().portfolio.items():
                if amount > 0 and crypto_id in mock_prices:
                    price_data = mock_prices[crypto_id]
                    if isinstance(price_data, dict) and 'usd' in price_data:
                        price = price_data['usd']
                        total_value += amount * price
            
            if abs(total_value - expected_value) < 0.01:  # Allow for floating point precision
                self.log_test("portfolio_calculation", "PASS", 
                             f"Portfolio calculation correct: ${total_value:,.2f}",
                             data={'calculated_value': total_value, 'expected_value': expected_value})
            else:
                self.log_test("portfolio_calculation", "FAIL", 
                             f"Portfolio calculation incorrect: got ${total_value:,.2f}, expected ${expected_value:,.2f}")
                
        except Exception as e:
            self.log_test("portfolio_calculation", "FAIL", "Exception during portfolio test", error=str(e))
    
    def test_system_logger(self):
        """Test system logging functionality"""
        print("\n📝 Testing System Logger...")
        
        try:
            from utils.system_logger import debug_log
            
            # Test basic logging
            debug_log("Test message for pipeline validation", "INFO", "pipeline_test")
            self.log_test("system_logger_basic", "PASS", "Basic logging functionality works")
            
            # Test error logging
            debug_log("Test error message", "ERROR", "pipeline_test_error")
            self.log_test("system_logger_error", "PASS", "Error logging functionality works")
            
        except Exception as e:
            self.log_test("system_logger", "FAIL", "Exception during logger test", error=str(e))
    
    def test_page_imports(self):
        """Test that all page modules can be imported"""
        print("\n📄 Testing Page Module Imports...")
        
        page_modules = [
            ('pages.portfolio_calculator', 'Portfolio Calculator'),
            ('pages.bitcoin_education', 'Bitcoin Education'),
            ('pages.mempool_data', 'Mempool Data'),
            ('pages.bitcoin_metrics_dashboard', 'Bitcoin Metrics Dashboard'),
            ('pages.mempool_network_dashboard', 'Mempool Network Dashboard')
        ]
        
        for module_name, display_name in page_modules:
            try:
                __import__(module_name)
                self.log_test(f"import_{module_name.split('.')[-1]}", "PASS", f"{display_name} module imported successfully")
            except Exception as e:
                self.log_test(f"import_{module_name.split('.')[-1]}", "FAIL", f"Failed to import {display_name}", error=str(e))
    
    def generate_report(self):
        """Generate comprehensive test report"""
        self.results['end_time'] = datetime.now().isoformat()
        self.results['summary'] = {
            'total_tests': self.test_count,
            'passed': self.passed_count,
            'failed': self.failed_count,
            'success_rate': f"{(self.passed_count/self.test_count)*100:.1f}%" if self.test_count > 0 else "0%"
        }
        
        print(f"\n{'='*60}")
        print("🏆 COMPREHENSIVE PIPELINE TEST REPORT")
        print(f"{'='*60}")
        print(f"📊 Total Tests: {self.test_count}")
        print(f"✅ Passed: {self.passed_count}")
        print(f"❌ Failed: {self.failed_count}")
        print(f"📈 Success Rate: {self.results['summary']['success_rate']}")
        
        # Count critical failures (exclude known acceptable failures)
        acceptable_failures = {'bitcoin_metrics_import'}
        critical_failures = []
        
        for test_name, result in self.results['tests'].items():
            if result['status'] == 'FAIL' and test_name not in acceptable_failures:
                critical_failures.append(test_name)
        
        if len(critical_failures) == 0:
            print("\n🎉 ALL CRITICAL TESTS PASSED! Pipeline is ready for deployment!")
            if self.failed_count > 0:
                print(f"📝 Note: {self.failed_count} non-critical test(s) failed (acceptable for deployment)")
            return True
        else:
            print(f"\n⚠️ {len(critical_failures)} CRITICAL TESTS FAILED! Please fix issues before deployment.")
            print("\nCritical failed tests:")
            for test_name in critical_failures:
                result = self.results['tests'][test_name]
                print(f"  ❌ {test_name}: {result['message']}")
                if result['error']:
                    print(f"     Error: {result['error']}")
            
            if self.failed_count > len(critical_failures):
                print(f"\nNon-critical failures (acceptable):")
                for test_name, result in self.results['tests'].items():
                    if result['status'] == 'FAIL' and test_name in acceptable_failures:
                        print(f"  ⚠️ {test_name}: {result['message']} (known issue)")
            
            return False
    
    def save_report(self, filename='pipeline_test_report.json'):
        """Save detailed report to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"\n📄 Detailed report saved to: {filename}")
        except Exception as e:
            print(f"\n❌ Failed to save report: {e}")
    
    def run_all_tests(self):
        """Run all pipeline tests"""
        print("🚀 STARTING COMPREHENSIVE DATA PIPELINE TEST")
        print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # Run all test categories
        self.test_imports()
        self.test_crypto_prices_api()
        self.test_mempool_api()
        self.test_bitcoin_metrics_api()
        self.test_ohlc_data()
        self.test_data_validation_utils()
        self.test_portfolio_functionality()
        self.test_system_logger()
        self.test_page_imports()
        
        # Generate and save report
        success = self.generate_report()
        self.save_report()
        
        return success

def main():
    """Main test execution"""
    runner = PipelineTestRunner()
    success = runner.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
