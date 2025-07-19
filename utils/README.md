# Utils Module

This directory contains utility modules that provide shared functionality across the Bitcoin Crypto Dashboard application.

## 🛠️ Utility Modules

### Core Utilities
- **`system_logger.py`** - Centralized logging system with multiple log levels, API call tracking, and user action monitoring
- **`data_cache_manager.py`** - Intelligent data caching with TTL (Time To Live) management for optimal API usage and performance
- **`portfolio_session_manager.py`** - Streamlit session state management for portfolio data, user preferences, and application state

## 🎯 Module Purposes

### `system_logger.py`
Provides comprehensive logging functionality:
- Debug logging with categorization
- API call performance tracking
- User action monitoring
- Error reporting and diagnostics

### `data_cache_manager.py`
Manages data fetching and caching:
- 5-minute TTL caching for API responses
- Multi-exchange price aggregation
- Mempool and OHLC data caching
- Fallback mechanisms for failed API calls

### `portfolio_session_manager.py`
Handles user session management:
- Portfolio initialization and persistence
- Default portfolio configuration
- Session state reset functionality
- Cross-page data sharing

## 🔧 Dependencies

Utility modules depend on:
- `streamlit` - Session state and caching
- API modules from `/api/` - Data fetching
- Standard Python libraries - Core functionality

## 📖 Usage

Utilities are imported by page modules and the main application:

```python
from utils.system_logger import debug_log
from utils.data_cache_manager import cached_get_crypto_prices
from utils.portfolio_session_manager import initialize_portfolio_session
```

## 🚀 Benefits

- **Centralized**: Common functionality in one place
- **Reusable**: Shared across multiple pages
- **Maintainable**: Single responsibility principle
- **Optimized**: Intelligent caching and performance
