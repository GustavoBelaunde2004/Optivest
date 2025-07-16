from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from gemini import GeminiService
from portfolio_optimizer import PortfolioOptimizer
from stock_data_service import StockDataService
from flask_sqlalchemy import SQLAlchemy
from models import db 


load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
db.init_app(app)

# Configure CORS for frontend integration
CORS(app, origins=[
    "http://localhost:3000",  # React dev server
    "http://localhost:3001",  # Alternative React port
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001"
])

# Initialize services
gemini_service = GeminiService(os.getenv('GEMINI_API_KEY'))
portfolio_optimizer = PortfolioOptimizer()
stock_data_service = StockDataService()

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Portfolio Optimizer API is running"})

@app.route('/api/industries', methods=['GET'])
def get_industries():
    """Get list of available investment industries"""
    industries = [
        "Technology",
        "Healthcare", 
        "Finance",
        "Energy",
        "Nuclear Energy",
        "Consumer Goods",
        "Real Estate",
        "Utilities",
        "Telecommunications",
        "Transportation",
        "Materials",
        "Aerospace & Defense"
    ]
    return jsonify({"industries": industries})

@app.route('/api/stocks/recommend', methods=['POST'])
def recommend_stocks():
    """Get stock recommendations based on selected industries"""
    try:
        data = request.get_json()
        selected_industries = data.get('industries', [])
        
        if not selected_industries:
            return jsonify({"error": "Please select at least one industry"}), 400
        
        try:
            # Get validated stock recommendations from Gemini
            recommendations = gemini_service.get_validated_stock_recommendations(selected_industries)
            
            print(f"   ✅ Validation completed: {len(recommendations) if recommendations else 0} stocks")
            
            if not recommendations:
                return jsonify({"error": "No stocks passed quality validation"}), 400
            
            # Return validated stocks with current prices
            json_safe_stocks = []
            for stock in recommendations:
                # Get current price and market cap from stock data service
                stock_info = stock_data_service.get_stock_info(stock['symbol'])
                
                # Format price for display
                if stock_info and stock_info['current_price']:
                    try:
                        price = float(stock_info['current_price'])
                        formatted_price = f"${price:.2f}" if price > 0 else 'N/A'
                    except (ValueError, TypeError):
                        formatted_price = 'N/A'
                else:
                    formatted_price = 'N/A'
                
                # Format market cap for display
                if stock_info and stock_info['market_cap']:
                    try:
                        market_cap = float(stock_info['market_cap'])
                        if market_cap > 1_000_000_000:
                            formatted_market_cap = f"${market_cap/1_000_000_000:.1f}B"
                        elif market_cap > 1_000_000:
                            formatted_market_cap = f"${market_cap/1_000_000:.1f}M"
                        else:
                            formatted_market_cap = f"${market_cap:,.0f}"
                    except (ValueError, TypeError):
                        formatted_market_cap = 'N/A'
                else:
                    formatted_market_cap = 'N/A'
                
                # Create a clean JSON-serializable copy
                clean_stock = {
                    'symbol': stock['symbol'],
                    'name': stock['name'],
                    'industry': stock['industry'],
                    'description': stock['description'],
                    'current_price': formatted_price,
                    'market_cap': formatted_market_cap
                }
                
                # Add quality score if available
                if 'quality_score' in stock:
                    clean_stock['quality_score'] = float(stock['quality_score'])
                
                json_safe_stocks.append(clean_stock)
            
            print(f"   📤 Returning {len(json_safe_stocks)} validated stocks")
            return jsonify({"stocks": json_safe_stocks})
            
        except Exception as validation_error:
            print(f"❌ Validation error: {validation_error}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"Stock validation failed: {str(validation_error)}"}), 500
        
    except Exception as e:
        print(f"❌ General error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/portfolio/optimize', methods=['POST'])
def optimize_portfolio():
    """Optimize portfolio for selected stocks"""
    try:
        import time
        total_start_time = time.time()
        
        data = request.get_json()
        selected_stocks = data.get('stocks', [])
        investment_amount = data.get('investment_amount', 10000)
        data_period = data.get('data_period', '2y')  # Default to 2 years
        
        print(f"🚀 Starting portfolio optimization request...")
        print(f"   Investment amount: ${investment_amount:,.2f}")
        print(f"   Selected stocks: {len(selected_stocks)}")
        print(f"   Data period: {data_period}")
        
        if not selected_stocks:
            return jsonify({"error": "Please select at least 2 stocks"}), 400
        
        if len(selected_stocks) < 2:
            return jsonify({"error": "Portfolio optimization requires at least 2 stocks"}), 400
        
        # Get historical data for optimization
        symbols = [stock['symbol'] for stock in selected_stocks]
        print(f"   Symbols: {symbols}")
        
        data_start_time = time.time()
        historical_data = stock_data_service.get_historical_data(symbols, period=data_period)
        data_fetch_time = time.time() - data_start_time
        print(f"   📊 Data fetch completed in {data_fetch_time:.2f} seconds")
        
        if historical_data.empty:
            print("   ❌ Historical data is empty")
            return jsonify({"error": "Unable to fetch historical data for optimization. Please try again or select different stocks."}), 500
        
        print(f"   ✅ Historical data shape: {historical_data.shape}")
        print(f"   ✅ Data columns: {historical_data.columns.tolist()}")
        
        # Check if we have enough data points
        if len(historical_data) < 20:
            return jsonify({"error": "Insufficient historical data for optimization. Need at least 20 data points."}), 400
        
        # Optimize portfolio
        optimization_start_time = time.time()
        optimal_weights = portfolio_optimizer.optimize_portfolio(historical_data)
        optimization_time = time.time() - optimization_start_time
        print(f"   🎯 Portfolio optimization completed in {optimization_time:.2f} seconds")
        
        if optimal_weights is None or len(optimal_weights) == 0:
            return jsonify({"error": "Portfolio optimization failed. Please try different stocks."}), 500
        
        # Generate explanation
        explanation_start_time = time.time()
        explanation = portfolio_optimizer.generate_explanation(
            symbols, optimal_weights, historical_data
        )
        explanation_time = time.time() - explanation_start_time
        print(f"   📝 Explanation generated in {explanation_time:.2f} seconds")
        
        # Calculate investment allocation
        allocations = []
        for i, symbol in enumerate(symbols):
            allocations.append({
                "symbol": symbol,
                "weight": float(optimal_weights[i]),
                "amount": float(optimal_weights[i] * investment_amount),
                "name": next((s['name'] for s in selected_stocks if s['symbol'] == symbol), symbol)
            })
        
        # Calculate risk metrics
        metrics_start_time = time.time()
        risk_metrics = portfolio_optimizer.calculate_risk_metrics(historical_data, optimal_weights)
        metrics_time = time.time() - metrics_start_time
        print(f"   📈 Risk metrics calculated in {metrics_time:.2f} seconds")
        
        total_time = time.time() - total_start_time
        print(f"🎉 Total optimization request completed in {total_time:.2f} seconds")
        
        return jsonify({
            "allocations": allocations,
            "explanation": explanation,
            "total_investment": investment_amount,
            "risk_metrics": risk_metrics,
            "performance_info": {
                "total_time": f"{total_time:.2f}s",
                "data_fetch_time": f"{data_fetch_time:.2f}s", 
                "optimization_time": f"{optimization_time:.2f}s",
                "explanation_time": f"{explanation_time:.2f}s",
                "metrics_time": f"{metrics_time:.2f}s"
            }
        })
        
    except Exception as e:
        print(f"Error in portfolio optimization: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Portfolio optimization failed: {str(e)}"}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
