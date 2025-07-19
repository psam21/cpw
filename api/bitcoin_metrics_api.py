"""
Bitcoin Metrics API Module
Fetches comprehensive Bitcoin data from multiple sources for professional visualization.
Optimized for Streamlit Community Cloud deployment with enhanced debug logging.
"""
import requests
import json
import time
from datetime import datetime, timedelta

class BitcoinMetrics:
    """Class to fetch and manage Bitcoin metrics from various APIs with enhanced logging"""
    
    def __init__(self, debug_logger=None):
        self.headers = {
            'User-Agent': 'StreamlitApp/1.0',
            'Accept': 'application/json',
            'Connection': 'close'
        }
        self.timeout = 8
        self.debug_log = debug_logger if debug_logger else print
        self.debug_log_api = None
        
        # Set up API logging if debug_logger is available
        if hasattr(debug_logger, '__module__'):
            try:
                # Import the API logging function from utils
                from utils.system_logger import debug_log_api_call
                self.debug_log_api = debug_log_api_call
            except ImportError:
                pass
    
    def safe_request(self, url, params=None, api_name="Unknown"):
        """Make a safe API request with comprehensive error handling and logging"""
        import time
        start_time = time.time()
        
        try:
            self.debug_log(f"🌐 Making API request to {api_name}: {url}", "INFO")
            if self.debug_log_api:
                self.debug_log_api(api_name, url, "STARTING")
            
            response = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
            response_time = round((time.time() - start_time) * 1000, 2)
            
            self.debug_log(f"📡 {api_name} response: Status={response.status_code}, Time={response_time}ms", "INFO")
            
            response.raise_for_status()
            data = response.json()
            
            if self.debug_log_api:
                self.debug_log_api(api_name, url, "SUCCESS", response_time, f"Status {response.status_code}")
            
            self.debug_log(f"✅ {api_name} API success: Got valid JSON data", "SUCCESS")
            return data
            
        except requests.exceptions.Timeout as e:
            response_time = round((time.time() - start_time) * 1000, 2)
            error_msg = f"Timeout after {self.timeout}s"
            self.debug_log(f"⏰ {api_name} API timeout: {error_msg}", "ERROR")
            if self.debug_log_api:
                self.debug_log_api(api_name, url, "TIMEOUT", response_time, None, error_msg)
            return None
            
        except requests.exceptions.HTTPError as e:
            response_time = round((time.time() - start_time) * 1000, 2)
            error_msg = f"HTTP {response.status_code}: {str(e)}"
            self.debug_log(f"🚨 {api_name} HTTP error: {error_msg}", "ERROR")
            if self.debug_log_api:
                self.debug_log_api(api_name, url, "HTTP_ERROR", response_time, None, error_msg)
            return None
            
        except requests.exceptions.ConnectionError as e:
            response_time = round((time.time() - start_time) * 1000, 2)
            error_msg = f"Connection failed: {str(e)}"
            self.debug_log(f"🔌 {api_name} connection error: {error_msg}", "ERROR")
            if self.debug_log_api:
                self.debug_log_api(api_name, url, "CONNECTION_ERROR", response_time, None, error_msg)
            return None
            
        except json.JSONDecodeError as e:
            response_time = round((time.time() - start_time) * 1000, 2)
            error_msg = f"Invalid JSON response: {str(e)}"
            self.debug_log(f"📄 {api_name} JSON decode error: {error_msg}", "ERROR")
            if self.debug_log_api:
                self.debug_log_api(api_name, url, "JSON_ERROR", response_time, None, error_msg)
            return None
            
        except Exception as e:
            response_time = round((time.time() - start_time) * 1000, 2)
            error_msg = f"Unexpected error: {str(e)}"
            self.debug_log(f"❌ {api_name} API failed: {error_msg}", "ERROR")
            if self.debug_log_api:
                self.debug_log_api(api_name, url, "ERROR", response_time, None, error_msg)
            return None
    
    def get_price_coindesk(self):
        """Get Bitcoin price from CoinDesk API with enhanced logging and fallback"""
        self.debug_log("🏦 Fetching Bitcoin price from CoinDesk...", "INFO")
        url = "https://api.coindesk.com/v1/bpi/currentprice.json"
        data = self.safe_request(url, api_name="CoinDesk")
        
        if data and 'bpi' in data and 'USD' in data['bpi']:
            price_data = {
                'price_usd': float(data['bpi']['USD']['rate'].replace(',', '')),
                'last_updated': data.get('time', {}).get('updated', 'Unknown'),
                'source': 'CoinDesk'
            }
            self.debug_log(f"💰 CoinDesk price: ${price_data['price_usd']:,.2f}", "SUCCESS")
            return price_data
        
        # Fallback: Use CoinGecko if CoinDesk fails (DNS issues observed)
        self.debug_log("🔄 CoinDesk failed, trying CoinGecko fallback...", "WARNING")
        fallback_url = "https://api.coingecko.com/api/v3/simple/price"
        fallback_params = {'ids': 'bitcoin', 'vs_currencies': 'usd'}
        fallback_data = self.safe_request(fallback_url, fallback_params, api_name="CoinGecko-Fallback")
        
        if fallback_data and 'bitcoin' in fallback_data and 'usd' in fallback_data['bitcoin']:
            price_data = {
                'price_usd': float(fallback_data['bitcoin']['usd']),
                'last_updated': 'Current',
                'source': 'CoinGecko (Fallback)'
            }
            self.debug_log(f"💰 CoinGecko fallback price: ${price_data['price_usd']:,.2f}", "SUCCESS")
            return price_data
        
        self.debug_log("❌ Both CoinDesk and CoinGecko price fetching failed", "ERROR")
        return None
    
    def get_coingecko_data(self):
        """Get comprehensive Bitcoin data from CoinGecko with enhanced logging"""
        self.debug_log("🦎 Fetching comprehensive Bitcoin data from CoinGecko...", "INFO")
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': 'bitcoin',
            'vs_currencies': 'usd,eur,gbp,inr',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true',
            'include_last_updated_at': 'true'
        }
        data = self.safe_request(url, params, api_name="CoinGecko")
        
        if data and 'bitcoin' in data:
            btc_data = data['bitcoin']
            coingecko_result = {
                'price_usd': btc_data.get('usd'),
                'price_eur': btc_data.get('eur'),
                'price_gbp': btc_data.get('gbp'),
                'price_inr': btc_data.get('inr'),
                'market_cap_usd': btc_data.get('usd_market_cap'),
                'volume_24h': btc_data.get('usd_24h_vol'),
                'change_24h': btc_data.get('usd_24h_change'),
                'last_updated': btc_data.get('last_updated_at'),
                'source': 'CoinGecko'
            }
            self.debug_log(f"🦎 CoinGecko data: Price=${coingecko_result['price_usd']:,.2f}, Cap=${coingecko_result['market_cap_usd']:,.0f}", "SUCCESS")
            return coingecko_result
        
        self.debug_log("❌ CoinGecko data extraction failed - invalid data structure", "ERROR")
        return None
    
    def get_fear_greed_index(self):
        """Get Fear & Greed Index with enhanced logging"""
        self.debug_log("😰 Fetching Fear & Greed Index from Alternative.me...", "INFO")
        url = "https://api.alternative.me/fng/"
        data = self.safe_request(url, api_name="Alternative.me")
        
        if data and 'data' in data and len(data['data']) > 0:
            fng_data = data['data'][0]
            fear_greed_result = {
                'value': int(fng_data.get('value', 0)),
                'classification': fng_data.get('value_classification', 'Unknown'),
                'timestamp': fng_data.get('timestamp', ''),
                'source': 'Alternative.me'
            }
            self.debug_log(f"😰 Fear & Greed Index: {fear_greed_result['value']} ({fear_greed_result['classification']})", "SUCCESS")
            return fear_greed_result
        
        self.debug_log("❌ Fear & Greed Index extraction failed - invalid data structure", "ERROR")
        return None
    
    def get_blockchain_info_simple(self, endpoint):
        """Get simple data from blockchain.info with enhanced logging"""
        self.debug_log(f"🔗 Fetching {endpoint} from Blockchain.info...", "INFO")
        url = f"https://blockchain.info/q/{endpoint}"
        import time
        start_time = time.time()
        
        try:
            if self.debug_log_api:
                self.debug_log_api("Blockchain.info", f"{url} ({endpoint})", "STARTING")
                
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response_time = round((time.time() - start_time) * 1000, 2)
            
            self.debug_log(f"📡 Blockchain.info {endpoint}: Status={response.status_code}, Time={response_time}ms", "INFO")
            
            response.raise_for_status()
            value = float(response.text.strip())
            
            if self.debug_log_api:
                self.debug_log_api("Blockchain.info", f"{url} ({endpoint})", "SUCCESS", response_time, f"Value: {value}")
                
            self.debug_log(f"✅ Blockchain.info {endpoint}: {value}", "SUCCESS")
            return value
            
        except ValueError as e:
            response_time = round((time.time() - start_time) * 1000, 2)
            error_msg = f"Invalid numeric response: {response.text if 'response' in locals() else 'No response'}"
            self.debug_log(f"🔢 Blockchain.info {endpoint} value error: {error_msg}", "ERROR")
            if self.debug_log_api:
                self.debug_log_api("Blockchain.info", f"{url} ({endpoint})", "VALUE_ERROR", response_time, None, error_msg)
            return None
            
        except Exception as e:
            response_time = round((time.time() - start_time) * 1000, 2)
            error_msg = str(e)
            self.debug_log(f"❌ Blockchain.info {endpoint} failed: {error_msg}", "ERROR")
            if self.debug_log_api:
                self.debug_log_api("Blockchain.info", f"{url} ({endpoint})", "ERROR", response_time, None, error_msg)
            return None
    
    def get_blockchain_chart(self, chart_type, timespan="1weeks"):
        """Get chart data with alternative sources for deprecated Blockchain.info APIs"""
        self.debug_log(f"📊 Fetching {chart_type} data from alternative sources...", "INFO")
        
        # Use alternative data sources for deprecated Blockchain.info charts
        try:
            if chart_type == 'hash-rate':
                return self.get_hashrate_alternative()
            elif chart_type == 'n-transactions':
                return self.get_transactions_alternative()
            elif chart_type == 'estimated-transaction-volume-usd':
                return self.get_volume_alternative()
            elif chart_type == 'miners-revenue':
                return self.get_miners_revenue_alternative()
            elif chart_type == 'transaction-fees-usd':
                return self.get_fees_alternative()
            elif chart_type == 'mempool-size':
                return self.get_mempool_size_alternative()
            elif chart_type == 'avg-block-size':
                return self.get_block_size_alternative()
            else:
                self.debug_log(f"❌ No alternative source available for {chart_type}", "WARNING")
                return None
                
        except Exception as e:
            self.debug_log(f"❌ Alternative data source failed for {chart_type}: {str(e)}", "ERROR")
            return None
    
    def get_hashrate_alternative(self):
        """Get hashrate data from mempool.space API"""
        self.debug_log("⛏️ Getting hashrate from mempool.space...", "INFO")
        url = "https://mempool.space/api/v1/mining/hashrate/3m"
        data = self.safe_request(url, api_name="Mempool-Hashrate")
        
        if data and isinstance(data, list) and len(data) > 0:
            # Convert to blockchain.info format
            values = []
            for item in data:
                if 'timestamp' in item and 'avgHashrate' in item:
                    values.append({
                        'x': item['timestamp'],
                        'y': item['avgHashrate'] / 1e18  # Convert to EH/s
                    })
            
            return {
                'values': values[-30:],  # Last 30 data points
                'source': 'mempool.space'
            }
        return None
    
    def get_transactions_alternative(self):
        """Get transaction count from mempool.space API"""
        self.debug_log("🔄 Getting transaction data from mempool.space...", "INFO")
        url = "https://mempool.space/api/v1/statistics/1w"  # Fixed: Use 1w instead of 2w
        data = self.safe_request(url, api_name="Mempool-Transactions")
        
        if data and isinstance(data, list):
            values = []
            for item in data:
                if 'added' in item and 'tx_count' in item:
                    values.append({
                        'x': item['added'],
                        'y': item['tx_count']
                    })
            
            return {
                'values': values[-30:],
                'source': 'mempool.space'
            }
        return None
    
    def get_volume_alternative(self):
        """Estimate transaction volume using CoinGecko market data"""
        self.debug_log("💰 Estimating transaction volume from market data...", "INFO")
        # Use 24h volume as proxy for transaction volume
        coingecko_data = self.get_coingecko_data()
        if coingecko_data and 'total_volume' in coingecko_data:
            current_time = int(time.time())
            return {
                'values': [{
                    'x': current_time,
                    'y': coingecko_data['total_volume']
                }],
                'source': 'CoinGecko (estimated)'
            }
        return None
    
    def get_miners_revenue_alternative(self):
        """Estimate miners revenue from block data"""
        self.debug_log("💎 Estimating miners revenue...", "INFO")
        # Simplified estimation: current price * 6.25 BTC per block * 144 blocks per day
        coingecko_data = self.get_coingecko_data()
        if coingecko_data and 'current_price' in coingecko_data:
            daily_revenue = coingecko_data['current_price'] * 6.25 * 144
            current_time = int(time.time())
            return {
                'values': [{
                    'x': current_time,
                    'y': daily_revenue
                }],
                'source': 'Estimated from block rewards'
            }
        return None
    
    def get_fees_alternative(self):
        """Get fee data from mempool.space"""
        self.debug_log("💸 Getting fee data from mempool.space...", "INFO")
        url = "https://mempool.space/api/v1/fees/recommended"
        data = self.safe_request(url, api_name="Mempool-Fees")
        
        if data and 'fastestFee' in data:
            current_time = int(time.time())
            return {
                'values': [{
                    'x': current_time,
                    'y': data['fastestFee']
                }],
                'source': 'mempool.space'
            }
        return None
    
    def get_mempool_size_alternative(self):
        """Get mempool size from mempool.space"""
        self.debug_log("🏊 Getting mempool size from mempool.space...", "INFO")
        url = "https://mempool.space/api/mempool"
        data = self.safe_request(url, api_name="Mempool-Size")
        
        if data and 'count' in data:
            current_time = int(time.time())
            return {
                'values': [{
                    'x': current_time,
                    'y': data['count']
                }],
                'source': 'mempool.space'
            }
        return None
    
    def get_block_size_alternative(self):
        """Get average block size from recent blocks"""
        self.debug_log("📦 Getting block size data from mempool.space...", "INFO")
        url = "https://mempool.space/api/v1/statistics/1w"
        data = self.safe_request(url, api_name="Mempool-BlockSize")
        
        if data and isinstance(data, list):
            values = []
            for item in data:
                if 'added' in item and 'avg_block_size' in item:
                    values.append({
                        'x': item['added'],
                        'y': item['avg_block_size']
                    })
            
            return {
                'values': values[-30:],
                'source': 'mempool.space'
            }
        return None
    
    def get_bitnodes_data(self):
        """Get Bitcoin node data from Bitnodes"""
        url = "https://bitnodes.io/api/v1/snapshots/latest/"
        data = self.safe_request(url)
        if data:
            return {
                'total_nodes': data.get('total_nodes', 0),
                'timestamp': data.get('timestamp', 0),
                'nodes_by_country': data.get('nodes', {}),
                'source': 'Bitnodes'
            }
        return None
    
    def get_lightning_network_data(self):
        """Get Lightning Network statistics"""
        url = "https://1ml.com/statistics?json=true"
        data = self.safe_request(url)
        if data:
            return {
                'total_capacity': data.get('total_capacity', 0),
                'node_count': data.get('node_count', 0),
                'channel_count': data.get('channel_count', 0),
                'avg_capacity': data.get('avg_capacity', 0),
                'source': '1ML'
            }
        return None
    
    def get_global_crypto_data(self):
        """Get global cryptocurrency market data with enhanced logging and rate limiting handling"""
        self.debug_log("🌍 Fetching global crypto market data from CoinGecko...", "INFO")
        url = "https://api.coingecko.com/api/v3/global"
        
        # First attempt
        data = self.safe_request(url, api_name="CoinGecko-Global")
        
        # If rate limited (429), try again after delay
        if data is None:
            self.debug_log("⏳ Rate limit detected, waiting 2 seconds before retry...", "WARNING")
            import time
            time.sleep(2)
            data = self.safe_request(url, api_name="CoinGecko-Global-Retry")
        
        if data and 'data' in data:
            global_data = data['data']
            global_result = {
                'total_market_cap_usd': global_data.get('total_market_cap', {}).get('usd', 0),
                'total_volume_24h': global_data.get('total_volume', {}).get('usd', 0),
                'btc_dominance': global_data.get('market_cap_percentage', {}).get('btc', 0),
                'active_cryptocurrencies': global_data.get('active_cryptocurrencies', 0),
                'markets': global_data.get('markets', 0),
                'source': 'CoinGecko'
            }
            self.debug_log(f"🌍 Global crypto data: BTC dominance {global_result['btc_dominance']:.1f}%, {global_result['active_cryptocurrencies']} cryptos", "SUCCESS")
            return global_result
        
        # If still failing, provide fallback data
        self.debug_log("❌ Global crypto data extraction failed - using fallback data", "WARNING")
        return {
            'total_market_cap_usd': 0,
            'total_volume_24h': 0,
            'btc_dominance': 50.0,  # Reasonable fallback
            'active_cryptocurrencies': 0,
            'markets': 0,
            'source': 'Fallback (API unavailable)'
        }
    
    def get_btc_historical_data(self, days=30):
        """Get historical Bitcoin price data"""
        url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': days,
            'interval': 'daily' if days <= 90 else 'weekly'
        }
        data = self.safe_request(url, params)
        if data:
            return {
                'prices': data.get('prices', []),
                'market_caps': data.get('market_caps', []),
                'total_volumes': data.get('total_volumes', []),
                'source': 'CoinGecko'
            }
        return None
    
    def get_all_basic_metrics(self):
        """Get all basic blockchain metrics in one call"""
        metrics = {}
        
        # Simple blockchain.info queries
        simple_metrics = {
            'mining_difficulty': 'getdifficulty',
            'block_reward': 'bcperblock', 
            'block_count': 'getblockcount',
            'total_supply': 'totalbc'
        }
        
        for metric_name, endpoint in simple_metrics.items():
            value = self.get_blockchain_info_simple(endpoint)
            if value is not None:
                metrics[metric_name] = value
        
        return metrics
    
    def get_comprehensive_metrics(self):
        """Get all Bitcoin metrics for the dashboard with enhanced logging"""
        self.debug_log("🔄 Fetching comprehensive Bitcoin metrics...", "INFO", "comprehensive_metrics_start")
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'errors': []
        }
        
        # Price data
        try:
            self.debug_log("💰 Starting CoinDesk price fetch...", "INFO", "coindesk_fetch")
            coindesk_price = self.get_price_coindesk()
            if coindesk_price:
                metrics['coindesk_price'] = coindesk_price
                self.debug_log("✅ CoinDesk price data acquired", "SUCCESS", "coindesk_success")
            else:
                error_msg = "CoinDesk price API failed"
                metrics['errors'].append(error_msg)
                self.debug_log(f"❌ {error_msg}", "ERROR", "coindesk_failure")
        except Exception as e:
            error_msg = f"CoinDesk error: {str(e)}"
            metrics['errors'].append(error_msg)
            self.debug_log(f"💥 CoinDesk exception: {error_msg}", "ERROR", "coindesk_exception")
        
        # CoinGecko comprehensive data
        try:
            self.debug_log("🦎 Starting CoinGecko comprehensive fetch...", "INFO", "coingecko_fetch")
            coingecko_data = self.get_coingecko_data()
            if coingecko_data:
                metrics['coingecko'] = coingecko_data
                self.debug_log("✅ CoinGecko comprehensive data acquired", "SUCCESS", "coingecko_success")
            else:
                error_msg = "CoinGecko API failed"
                metrics['errors'].append(error_msg)
                self.debug_log(f"❌ {error_msg}", "ERROR", "coingecko_failure")
        except Exception as e:
            error_msg = f"CoinGecko error: {str(e)}"
            metrics['errors'].append(error_msg)
            self.debug_log(f"🦎 CoinGecko exception: {error_msg}", "ERROR", "coingecko_exception")
        
        # Fear & Greed Index
        try:
            self.debug_log("😰 Starting Fear & Greed Index fetch...", "INFO", "fear_greed_fetch")
            fng_data = self.get_fear_greed_index()
            if fng_data:
                metrics['fear_greed'] = fng_data
                self.debug_log("✅ Fear & Greed Index data acquired", "SUCCESS", "fear_greed_success")
            else:
                error_msg = "Fear & Greed Index API failed"
                metrics['errors'].append(error_msg)
                self.debug_log(f"❌ {error_msg}", "ERROR", "fear_greed_failure")
        except Exception as e:
            error_msg = f"Fear & Greed error: {str(e)}"
            metrics['errors'].append(error_msg)
            self.debug_log(f"😰 Fear & Greed exception: {error_msg}", "ERROR", "fear_greed_exception")
        
        # Basic blockchain metrics
        try:
            self.debug_log("🔗 Starting Blockchain.info basic metrics fetch...", "INFO", "blockchain_fetch")
            basic_metrics = self.get_all_basic_metrics()
            if basic_metrics:
                metrics['blockchain'] = basic_metrics
                self.debug_log("✅ Blockchain.info basic metrics acquired", "SUCCESS", "blockchain_success")
            else:
                error_msg = "Blockchain.info basic metrics failed"
                metrics['errors'].append(error_msg)
                self.debug_log(f"❌ {error_msg}", "ERROR", "blockchain_failure")
        except Exception as e:
            error_msg = f"Blockchain.info error: {str(e)}"
            metrics['errors'].append(error_msg)
            self.debug_log(f"🔗 Blockchain.info exception: {error_msg}", "ERROR", "blockchain_exception")
        
        # Global crypto data
        try:
            self.debug_log("🌍 Starting global crypto data fetch...", "INFO", "global_crypto_fetch")
            global_data = self.get_global_crypto_data()
            if global_data:
                metrics['global'] = global_data
                self.debug_log("✅ Global crypto data acquired", "SUCCESS", "global_crypto_success")
            else:
                error_msg = "Global crypto data failed"
                metrics['errors'].append(error_msg)
                self.debug_log(f"❌ {error_msg}", "ERROR", "global_crypto_failure")
        except Exception as e:
            error_msg = f"Global crypto error: {str(e)}"
            metrics['errors'].append(error_msg)
            self.debug_log(f"🌍 Global crypto exception: {error_msg}", "ERROR", "global_crypto_exception")
        
        # Chart data (these are the failing APIs!)
        chart_types = ['hash-rate', 'n-transactions', 'estimated-transaction-volume-usd', 
                      'miners-revenue', 'transaction-fees-usd', 'mempool-size', 
                      'avg-block-size']  # Removed deprecated: 'n-active-addresses', 'avg-block-time'
        
        self.debug_log("📊 Starting chart data collection...", "INFO", "charts_start")
        metrics['charts'] = {}
        
        # Handle avg-block-time separately with alternative method
        try:
            self.debug_log("⏰ Fetching average block time (alternative method)...", "INFO", "avg_block_time_alt")
            # Use mempool.space API for accurate block time
            self.debug_log("⏰ Trying mempool.space for block time...", "INFO", "mempool_block_time")
            mempool_url = "https://mempool.space/api/v1/difficulty-adjustment"
            mempool_data = self.safe_request(mempool_url, api_name="Mempool-Difficulty")
            if mempool_data and 'timeAvg' in mempool_data:
                # timeAvg is in milliseconds, convert to minutes
                avg_time = mempool_data['timeAvg'] / 1000 / 60  # Convert milliseconds to minutes
                self.debug_log(f"✅ Average block time from mempool: {avg_time:.1f} minutes", "SUCCESS", "avg_block_time_success")
                metrics['avg_block_time'] = avg_time
            else:
                # Default to theoretical 10 minutes if API fails
                self.debug_log("⏰ Using default block time: 10.0 minutes", "INFO", "default_block_time")
                metrics['avg_block_time'] = 10.0
                
        except Exception as e:
            error_msg = f"Average block time fetch error: {str(e)}"
            metrics['errors'].append(error_msg)
            self.debug_log(f"❌ {error_msg}", "ERROR", "avg_block_time_error")
            # Fallback to theoretical 10 minutes
            metrics['avg_block_time'] = 10.0
            self.debug_log("⏰ Using fallback block time: 10.0 minutes", "INFO", "fallback_block_time")
        
        for chart_type in chart_types:
            try:
                self.debug_log(f"📈 Fetching {chart_type} chart...", "INFO", f"chart_{chart_type.replace('-', '_')}")
                chart_data = self.get_blockchain_chart(chart_type)
                if chart_data:
                    metrics['charts'][chart_type] = chart_data
                    self.debug_log(f"✅ {chart_type} chart acquired", "SUCCESS", f"chart_{chart_type.replace('-', '_')}_success")
                else:
                    error_msg = f"{chart_type} chart failed"
                    metrics['errors'].append(error_msg)
                    self.debug_log(f"❌ {error_msg}", "ERROR", f"chart_{chart_type.replace('-', '_')}_failure")
            except Exception as e:
                error_msg = f"{chart_type} chart error: {str(e)}"
                metrics['errors'].append(error_msg)
                self.debug_log(f"💥 {chart_type} chart exception: {error_msg}", "ERROR", f"chart_{chart_type.replace('-', '_')}_exception")
        
        # Final summary
        total_metrics = len([k for k in metrics.keys() if k not in ['timestamp', 'errors']]) + len(metrics.get('charts', {}))
        error_count = len(metrics['errors'])
        success_rate = round(((total_metrics - error_count) / max(total_metrics, 1)) * 100, 1)
        
        self.debug_log(f"📋 Metrics collection complete:", "INFO", "metrics_summary")
        self.debug_log(f"- Total metrics attempted: {total_metrics}", "DATA", "metrics_summary")
        self.debug_log(f"- Errors encountered: {error_count}", "DATA", "metrics_summary")
        self.debug_log(f"- Success rate: {success_rate}%", "DATA", "metrics_summary")
        
        if error_count == 0:
            self.debug_log("🎉 All Bitcoin metrics collected successfully!", "SUCCESS", "metrics_complete")
        elif error_count < 5:
            self.debug_log(f"⚠️ {error_count} Bitcoin metrics failed", "WARNING", "metrics_partial")
        else:
            self.debug_log(f"🚨 Multiple Bitcoin metric failures: {error_count}", "ERROR", "metrics_major_failure")
        
        return metrics

# Create a global instance
bitcoin_metrics = BitcoinMetrics()
