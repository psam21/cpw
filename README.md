# Bitcoin Crypto Dashboard

A comprehensive Bitcoin and cryptocurrency dashboard built with Streamlit, featuring real-time data from multiple exchanges, technical analysis, portfolio tracking, and network monitoring.

## 🚀 Features

- **📊 Bitcoin Metrics Dashboard** - Real-time Bitcoin price, market cap, Fear & Greed Index
- **📈 Technical Analysis** - OHLC charts with RSI, MACD, and volatility indicators  
- **⛏️ Mempool Network Monitor** - Fee recommendations and network congestion analysis
- **💼 Portfolio Calculator** - Multi-asset portfolio tracking and performance analysis
- **🔍 System Debug Viewer** - Comprehensive logging and system information
- **📚 Bitcoin Education** - Educational content about Bitcoin fundamentals

## 🏗️ Architecture

This project uses a clean, modular architecture with descriptive naming:

### `/api/` - External Data Sources
External API integrations for fetching cryptocurrency data:
- `bitcoin_metrics_api.py` - Bitcoin metrics aggregation (CoinGecko, CoinDesk, Alternative.me)
- `binance_exchange_api.py` - Binance exchange integration
- `bitfinex_exchange_api.py` - Bitfinex exchange integration  
- `coinbase_exchange_api.py` - Coinbase exchange integration
- `kucoin_exchange_api.py` - KuCoin exchange integration
- `mempool_network_api.py` - Bitcoin mempool and network data
- `multi_exchange_aggregator.py` - Multi-exchange price aggregation

### `/pages/` - Streamlit Dashboard Pages
User interface components for the Streamlit dashboard:
- `bitcoin_metrics_dashboard.py` - Main Bitcoin metrics and indicators
- `bitcoin_technical_analysis.py` - OHLC charts with technical analysis
- `mempool_network_dashboard.py` - Network fee analysis and recommendations
- `portfolio_calculator.py` - Portfolio value tracking and calculations
- `system_debug_viewer.py` - Debug logs and system information
- `bitcoin_education.py` - Educational content about Bitcoin

### `/utils/` - Shared Utilities
Helper modules providing shared functionality:
- `system_logger.py` - Centralized logging and debugging system
- `data_cache_manager.py` - Data caching and fetch optimization
- `portfolio_session_manager.py` - Portfolio session state management

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/psam21/cpw.git
   cd cpw
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## 📋 Requirements

- Python 3.8+
- Streamlit
- Plotly
- Pandas
- Requests
- NumPy
- TA-Lib (for technical indicators)

See `requirements.txt` for complete dependency list.

## 🌐 Data Sources

The dashboard aggregates data from multiple reliable sources:

- **CoinGecko** - Comprehensive cryptocurrency market data
- **CoinDesk** - Bitcoin price and market information
- **Alternative.me** - Fear & Greed Index
- **Blockchain.info** - Bitcoin network statistics
- **Mempool.space** - Bitcoin mempool and fee data
- **Binance** - Real-time trading data
- **Bitfinex** - OHLC and trading data
- **Coinbase** - Price and market data
- **KuCoin** - Additional exchange data

## 🔧 Configuration

The application is optimized for Streamlit Community Cloud deployment with:
- Intelligent caching (5-minute TTL for most data)
- Graceful error handling and fallback mechanisms
- Cloud-optimized API timeouts and headers
- Comprehensive logging and debugging

## 📊 Usage

1. **Navigation**: Use the sidebar to switch between different dashboard pages
2. **Real-time Data**: Data is automatically cached and refreshed every 5 minutes
3. **Portfolio Tracking**: Add your cryptocurrency holdings in the Portfolio Calculator
4. **Technical Analysis**: View detailed OHLC charts with multiple indicators
5. **Network Monitoring**: Check current Bitcoin network fees and congestion
6. **Debug Information**: Use the Debug Viewer to monitor API performance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Charts powered by [Plotly](https://plotly.com/)
- Data sources: CoinGecko, CoinDesk, Alternative.me, and various cryptocurrency exchanges
- Technical analysis indicators via [TA-Lib](https://ta-lib.org/)

## 📞 Support

For support, please open an issue on the GitHub repository or contact the maintainer.

---

**⚡ Built for Bitcoin enthusiasts, traders, and developers who want comprehensive cryptocurrency market insights in a beautiful, responsive dashboard.**
