"""
Module to fetch mempool data.
"""
import requests

def get_mempool_info():
    """
    Fetches comprehensive mempool information.
    """
    try:
        print("Starting mempool data fetch...")  # Debug log
        
        # Get recommended fees
        fees_url = "https://mempool.space/api/v1/fees/recommended"
        print(f"Fetching fees from: {fees_url}")
        fees_response = requests.get(fees_url, timeout=15)
        fees_response.raise_for_status()
        fees = fees_response.json()
        print(f"Fees data: {fees}")
        
        # Get mempool statistics
        mempool_url = "https://mempool.space/api/v1/fees/mempool-blocks"
        print(f"Fetching mempool blocks from: {mempool_url}")
        mempool_response = requests.get(mempool_url, timeout=15)
        mempool_response.raise_for_status()
        mempool_blocks = mempool_response.json()
        print(f"Mempool blocks: {len(mempool_blocks)} blocks")
        
        # Get difficulty adjustment
        difficulty_url = "https://mempool.space/api/v1/difficulty-adjustment"
        print(f"Fetching difficulty from: {difficulty_url}")
        difficulty_response = requests.get(difficulty_url, timeout=15)
        difficulty_response.raise_for_status()
        difficulty = difficulty_response.json()
        print(f"Difficulty data: {difficulty}")
        
        # Get latest block information
        blocks_url = "https://mempool.space/api/v1/blocks"
        print(f"Fetching blocks from: {blocks_url}")
        blocks_response = requests.get(blocks_url, timeout=15)
        blocks_response.raise_for_status()
        latest_blocks = blocks_response.json()
        print(f"Latest blocks: {len(latest_blocks)} blocks")
        
        # Get mining pool stats
        mining_url = "https://mempool.space/api/v1/mining/pools/1w"
        print(f"Fetching mining pools from: {mining_url}")
        mining_response = requests.get(mining_url, timeout=15)
        mining_response.raise_for_status()
        mining_pools = mining_response.json()
        print(f"Mining pools data fetched successfully")
        
        # Get fee histogram - this endpoint might not exist, so handle gracefully
        fee_histogram = []
        try:
            histogram_url = "https://mempool.space/api/v1/fees/histogram"
            print(f"Fetching fee histogram from: {histogram_url}")
            fee_hist_response = requests.get(histogram_url, timeout=15)
            if fee_hist_response.status_code == 200:
                fee_histogram = fee_hist_response.json()
                print(f"Fee histogram fetched: {len(fee_histogram)} entries")
        except Exception as e:
            print(f"Fee histogram fetch failed: {e}")
        
        result = {
            'fees': fees,
            'mempool_blocks': mempool_blocks,
            'difficulty': difficulty,
            'latest_blocks': latest_blocks[:5],  # Show only latest 5 blocks
            'mining_pools': mining_pools,
            'fee_histogram': fee_histogram
        }
        print(f"Successfully fetched all mempool data")
        return result
        
    except requests.exceptions.Timeout:
        print("Error: Mempool API request timed out")
        return {
            'fees': {'fastestFee': 15, 'halfHourFee': 12, 'hourFee': 8, 'economyFee': 5, 'minimumFee': 1},
            'mempool_blocks': [],
            'difficulty': {'progressPercent': 50, 'difficultyChange': 0, 'estimatedRetargetDate': 0, 'remainingBlocks': 1000, 'remainingTime': 604800},
            'latest_blocks': [],
            'mining_pools': {'pools': []},
            'fee_histogram': []
        }
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to Mempool API")
        return {
            'fees': {'fastestFee': 15, 'halfHourFee': 12, 'hourFee': 8, 'economyFee': 5, 'minimumFee': 1},
            'mempool_blocks': [],
            'difficulty': {'progressPercent': 50, 'difficultyChange': 0, 'estimatedRetargetDate': 0, 'remainingBlocks': 1000, 'remainingTime': 604800},
            'latest_blocks': [],
            'mining_pools': {'pools': []},
            'fee_histogram': []
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching mempool data: {e}")
        return {
            'fees': {'fastestFee': 15, 'halfHourFee': 12, 'hourFee': 8, 'economyFee': 5, 'minimumFee': 1},
            'mempool_blocks': [],
            'difficulty': {'progressPercent': 50, 'difficultyChange': 0, 'estimatedRetargetDate': 0, 'remainingBlocks': 1000, 'remainingTime': 604800},
            'latest_blocks': [],
            'mining_pools': {'pools': []},
            'fee_histogram': []
        }
    except ValueError as e:
        print(f"JSON parsing error: {e}")
        return {
            'fees': {'fastestFee': 15, 'halfHourFee': 12, 'hourFee': 8, 'economyFee': 5, 'minimumFee': 1},
            'mempool_blocks': [],
            'difficulty': {'progressPercent': 50, 'difficultyChange': 0, 'estimatedRetargetDate': 0, 'remainingBlocks': 1000, 'remainingTime': 604800},
            'latest_blocks': [],
            'mining_pools': {'pools': []},
            'fee_histogram': []
        }
    except Exception as e:
        print(f"Unexpected error in mempool data fetch: {e}")
        return {
            'fees': {'fastestFee': 15, 'halfHourFee': 12, 'hourFee': 8, 'economyFee': 5, 'minimumFee': 1},
            'mempool_blocks': [],
            'difficulty': {'progressPercent': 50, 'difficultyChange': 0, 'estimatedRetargetDate': 0, 'remainingBlocks': 1000, 'remainingTime': 604800},
            'latest_blocks': [],
            'mining_pools': {'pools': []},
            'fee_histogram': []
        }

def get_mempool_stats():
    """
    Fetches additional mempool statistics.
    """
    try:
        # Get network statistics - this endpoint might not exist
        network_stats = {}
        try:
            stats_response = requests.get("https://mempool.space/api/v1/statistics", timeout=10)
            if stats_response.status_code == 200:
                network_stats = stats_response.json()
        except:
            pass
        
        # Get hashrate
        hashrate_response = requests.get("https://mempool.space/api/v1/mining/hashrate/1w", timeout=10)
        hashrate_response.raise_for_status()
        hashrate = hashrate_response.json()
        
        # Get mempool size over time - this endpoint might not exist
        mempool_size = []
        try:
            mempool_size_response = requests.get("https://mempool.space/api/v1/statistics/2h", timeout=10)
            if mempool_size_response.status_code == 200:
                mempool_size = mempool_size_response.json()
        except:
            pass
        
        return {
            'network_stats': network_stats,
            'hashrate': hashrate,
            'mempool_size': mempool_size
        }
    except requests.exceptions.RequestException as e:
        return {'error': f'Network error: {str(e)}'}
    except ValueError as e:
        return {'error': f'JSON parsing error: {str(e)}'}
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}
