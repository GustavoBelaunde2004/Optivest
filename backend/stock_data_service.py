import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import requests
import json

class StockDataService:
    def __init__(self):
        pass
    
    def get_stock_info(self, symbol):
        """Get basic stock information"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            return {
                "current_price": info.get('currentPrice', info.get('regularMarketPrice', 0)),
                "market_cap": info.get('marketCap', 0),
                "pe_ratio": info.get('trailingPE', 0),
                "dividend_yield": info.get('dividendYield', 0),
                "sector": info.get('sector', 'Unknown'),
                "beta": info.get('beta', 1.0)
            }
        except Exception as e:
            print(f"Error fetching info for {symbol}: {e}")
            return None
    
    def get_historical_data(self, symbols, period="2y"):
        """Get historical price data for portfolio optimization with fallback to mock data"""
        try:
            import time
            from datetime import datetime, timedelta
            start_time = time.time()
            
            print(f"📊 Fetching historical data for: {symbols}")
            print(f"   📅 Data period requested: {period}")
            
            # Show what period means in human terms
            period_info = {
                "1d": "1 day",
                "5d": "5 days", 
                "1mo": "1 month",
                "3mo": "3 months",
                "6mo": "6 months", 
                "1y": "1 year (~252 trading days)",
                "2y": "2 years (~504 trading days) ⭐ DEFAULT",
                "5y": "5 years (~1260 trading days)",
                "10y": "10 years (~2520 trading days)",
                "ytd": "Year to date",
                "max": "Maximum available history"
            }
            
            period_description = period_info.get(period, f"Custom period: {period}")
            print(f"   📆 This means: {period_description}")
            
            # Calculate expected date range for reference
            end_date = datetime.now()
            if period == "1y":
                start_date = end_date - timedelta(days=365)
            elif period == "6mo":
                start_date = end_date - timedelta(days=180)
            elif period == "3mo":
                start_date = end_date - timedelta(days=90)
            elif period == "2y":
                start_date = end_date - timedelta(days=730)
            else:
                start_date = "varies"
            
            if start_date != "varies":
                print(f"   📅 Expected date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            
            # Try real data first with longer timeout and multiple attempts
            real_data_attempts = 0
            max_attempts = 2
            
            while real_data_attempts < max_attempts:
                try:
                    real_data_attempts += 1
                    print(f"   Attempt {real_data_attempts}/{max_attempts} to fetch real data...")
                    
                    # Download data for all symbols with increased timeout
                    data = yf.download(
                        symbols, 
                        period=period, 
                        progress=False, 
                        show_errors=False,
                        timeout=30  # Increased timeout
                    )
                    
                    if not data.empty and 'Adj Close' in data.columns:
                        print(f"   ✅ Downloaded real data shape: {data.shape}")
                        
                        if len(symbols) == 1:
                            adj_close_data = data['Adj Close']
                            if isinstance(adj_close_data, pd.Series):
                                result = adj_close_data.to_frame(symbols[0])
                            else:
                                result = adj_close_data
                        else:
                            result = data['Adj Close']
                        
                        result = result.dropna()
                        if not result.empty and len(result) >= 20:
                            fetch_time = time.time() - start_time
                            
                            # Show detailed data information
                            start_date_actual = result.index[0].strftime('%Y-%m-%d')
                            end_date_actual = result.index[-1].strftime('%Y-%m-%d')
                            total_days = (result.index[-1] - result.index[0]).days
                            
                            print(f"   ✅ Real data fetched in {fetch_time:.2f} seconds")
                            print(f"   📊 Data points: {len(result)} trading days")
                            print(f"   📅 Actual date range: {start_date_actual} to {end_date_actual}")
                            print(f"   📆 Total calendar days: {total_days} days")
                            print(f"   📈 Columns (stocks): {list(result.columns)}")
                            
                            return result
                        else:
                            print(f"   ⚠️  Real data insufficient: {len(result) if not result.empty else 0} data points")
                    
                except Exception as e:
                    print(f"   ❌ Real data fetch attempt {real_data_attempts} failed: {e}")
                    if real_data_attempts < max_attempts:
                        print(f"   ⏳ Waiting 2 seconds before retry...")
                        time.sleep(2)
            
            # Fallback to mock data
            print("   📈 Using mock data for demonstration (real data unavailable)")
            mock_start = time.time()
            result = self._generate_mock_data(symbols, period)
            mock_time = time.time() - mock_start
            
            # Show mock data details
            if not result.empty:
                start_date_mock = result.index[0].strftime('%Y-%m-%d')
                end_date_mock = result.index[-1].strftime('%Y-%m-%d')
                total_days_mock = (result.index[-1] - result.index[0]).days
                
                print(f"   ✅ Mock data generated in {mock_time:.2f} seconds")
                print(f"   📊 Data points: {len(result)} trading days")
                print(f"   📅 Mock date range: {start_date_mock} to {end_date_mock}")
                print(f"   📆 Total calendar days: {total_days_mock} days")
                print(f"   📈 Columns (stocks): {list(result.columns)}")
            
            total_time = time.time() - start_time
            print(f"📊 Total data fetch time: {total_time:.2f} seconds")
            return result
            
        except Exception as e:
            print(f"❌ Error in get_historical_data: {e}")
            return self._generate_mock_data(symbols, period)
    
    def _generate_mock_data(self, symbols, period='1y'):
        """Generate realistic mock stock data for demonstration"""
        print(f"Generating mock data for {len(symbols)} symbols")
        
        # Calculate date range
        end_date = datetime.now()
        if period == '1y':
            start_date = end_date - timedelta(days=365)
        elif period == '6mo':
            start_date = end_date - timedelta(days=180)
        elif period == '3mo':
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=365)
        
        # Create date range (business days only)
        dates = pd.date_range(start=start_date, end=end_date, freq='B')
        
        # Base prices for common stocks
        base_prices = {
            'AAPL': 150, 'MSFT': 300, 'GOOGL': 100, 'AMZN': 120, 'TSLA': 200,
            'META': 250, 'NVDA': 400, 'BRK-B': 300, 'JNJ': 160, 'V': 220,
            'PG': 140, 'HD': 300, 'MA': 350, 'UNH': 450, 'DIS': 100,
            'ADBE': 400, 'NFLX': 350, 'XOM': 100, 'BAC': 30, 'ABBV': 140
        }
        
        data = {}
        
        for symbol in symbols:
            # Get base price or use random if not in our list
            base_price = base_prices.get(symbol, np.random.uniform(50, 300))
            
            # Generate realistic price movements
            n_days = len(dates)
            returns = np.random.normal(0.0005, 0.02, n_days)  # Daily returns with some drift
            
            # Add some trend and volatility
            trend = np.linspace(-0.1, 0.1, n_days)  # Slight upward trend
            returns += trend / n_days
            
            # Calculate cumulative prices
            prices = [base_price]
            for i in range(1, n_days):
                new_price = prices[-1] * (1 + returns[i])
                prices.append(max(new_price, 1))  # Ensure price doesn't go below $1
            
            data[symbol] = prices[:len(dates)]
        
        # Create DataFrame
        df = pd.DataFrame(data, index=dates)
        
        print(f"Generated mock data shape: {df.shape}")
        print(f"Mock data columns: {df.columns.tolist()}")
        
        return df
    
    def calculate_returns(self, price_data):
        """Calculate daily returns from price data"""
        return price_data.pct_change().dropna()
    
    def get_risk_free_rate(self):
        """Get current risk-free rate (using 3-month Treasury)"""
        try:
            treasury = yf.Ticker("^IRX")
            data = treasury.history(period="1d")
            if not data.empty:
                return data['Close'].iloc[-1] / 100  # Convert percentage to decimal
            else:
                return 0.02  # Default 2% if unable to fetch
        except:
            return 0.02  # Default 2% risk-free rate
