from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from gemini import GeminiService
from portfolio_optimizer import PortfolioOptimizer
from stock_data_service import StockDataService
from flask_sqlalchemy import SQLAlchemy
from models import db 
from auth import auth_bp
from flask import session
from models import db, User, Portfolio, PortfolioStock, ValidatedStock
import json

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
db.init_app(app)
app.secret_key = "key"

# Initialize database tables
with app.app_context():
    db.create_all()

app.register_blueprint(auth_bp, url_prefix="/auth")

# Configure CORS for frontend integration
CORS(app, origins=[
    "http://localhost:5173",  # React dev server
    "http://127.0.0.1:5173",  # Alternative React port
    "https://didactic-space-robot-jjrjxxp79rqrhpv7g-5173.app.github.dev",  # Codespaces frontend
], supports_credentials=True, allow_headers=['Content-Type'], methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Initialize services
gemini_service = GeminiService(os.getenv('GEMINI_API_KEY'))
portfolio_optimizer = PortfolioOptimizer()
stock_data_service = StockDataService()

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Portfolio Optimizer API is running"})

@app.route('/api/session/check', methods=['GET'])
def check_session():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            return jsonify({"authenticated": True, "user_id": user_id, "username": user.username}), 200
        else:
            return jsonify({"authenticated": False, "error": "User not found"}), 401
    else:
        return jsonify({"authenticated": False, "error": "No active session"}), 401

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
    """Get stock recommendations based on selected industries or validate a custom stock"""
    try:
        data = request.get_json()
        selected_industries = data.get('industries', [])
        custom_stock = data.get('custom_stock')

        # If custom_stock is provided, validate and return info for that stock
        if custom_stock:
            # Use Gemini to extract a stock symbol and company name from the user's message
            extracted_ticker, extracted_company = gemini_service.extract_stock_symbol(custom_stock)
            symbol_to_try = extracted_ticker or ''
            company_to_try = extracted_company or ''
            stock_info = None
            tried = []
            # Try ticker first
            if symbol_to_try:
                stock_info = stock_data_service.get_stock_info(symbol_to_try)
                tried.append(symbol_to_try)
            # If ticker fails, try company name
            if not stock_info and company_to_try:
                stock_info = stock_data_service.get_stock_info(company_to_try)
                tried.append(company_to_try)
            if not stock_info:
                return jsonify({"error": f"Could not find a valid stock for your input. Tried: {', '.join(tried)}"}), 404
            from stock_validator import StockValidator
            validator = StockValidator()
            # Use the symbol from stock_info if available
            symbol = stock_info.get('symbol', symbol_to_try or company_to_try).upper()
            stock_dict = {
                'symbol': symbol,
                'name': stock_info.get('shortName', symbol),
                'description': stock_info.get('longBusinessSummary', f"User-requested stock: {symbol}"),
                'industry': stock_info.get('sector', selected_industries[0] if selected_industries else 'Unknown'),
                'current_price': stock_info.get('current_price', 0),
                'market_cap': stock_info.get('market_cap', 0)
            }
            validated = validator.validate_stocks([stock_dict], max_stocks=1)
            quality_score = validated[0]['quality_score'] if validated else 0
            validation_passed = bool(validated and validated[0]['is_valid'])
            validation_message = (
                validated[0]['failure_reason'] if validated and not validated[0]['is_valid'] else "Passed validation"
            )
            # Format price and market cap for display (like recommended stocks)
            try:
                price = float(stock_info.get('current_price', 0))
                formatted_price = f"${price:.2f}" if price > 0 else 'N/A'
            except (ValueError, TypeError):
                formatted_price = 'N/A'
            try:
                market_cap = float(stock_info.get('market_cap', 0))
                if market_cap > 1_000_000_000:
                    formatted_market_cap = f"${market_cap/1_000_000_000:.1f}B"
                elif market_cap > 1_000_000:
                    formatted_market_cap = f"${market_cap/1_000_000:.1f}M"
                else:
                    formatted_market_cap = f"${market_cap:,.0f}"
            except (ValueError, TypeError):
                formatted_market_cap = 'N/A'
            response_stock = {
                'symbol': symbol,
                'name': stock_info.get('shortName', symbol),
                'description': stock_info.get('longBusinessSummary', f"User-requested stock: {symbol}"),
                'industry': stock_info.get('sector', selected_industries[0] if selected_industries else 'Unknown'),
                'current_price': formatted_price,
                'market_cap': formatted_market_cap,
                'quality_score': quality_score,
                'validation_passed': validation_passed,
                'validation_message': validation_message
            }
            return jsonify({"stocks": [response_stock]})

        # Normal industry-based recommendations
        if not selected_industries:
            return jsonify({"error": "Please select at least one industry"}), 400
        try:
            # Get validated stock recommendations from Gemini
            recommendations = gemini_service.get_validated_stock_recommendations(selected_industries)
            print(f"Validation completed: {len(recommendations) if recommendations else 0} stocks")
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
            print(f"Returning {len(json_safe_stocks)} validated stocks")
            return jsonify({"stocks": json_safe_stocks})
        except Exception as validation_error:
            print(f"Validation error: {validation_error}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"Stock validation failed: {str(validation_error)}"}), 500
    except Exception as e:
        print(f"General error: {e}")
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
        
        print(f"Starting portfolio optimization request...")
        print(f"Investment amount: ${investment_amount:,.2f}")
        print(f"Selected stocks: {len(selected_stocks)}")
        print(f"Data period: {data_period}")
        
        if not selected_stocks:
            return jsonify({"error": "Please select at least 2 stocks"}), 400
        
        if len(selected_stocks) < 2:
            return jsonify({"error": "Portfolio optimization requires at least 2 stocks"}), 400
        
        # Get historical data for optimization
        symbols = [stock['symbol'] for stock in selected_stocks]
        print(f"Symbols: {symbols}")
        
        data_start_time = time.time()
        historical_data = stock_data_service.get_historical_data(symbols, period=data_period)
        data_fetch_time = time.time() - data_start_time
        print(f"Data fetch completed in {data_fetch_time:.2f} seconds")
        
        if historical_data.empty:
            print("Historical data is empty")
            return jsonify({"error": "Unable to fetch historical data for optimization. Please try again or select different stocks."}), 500
        
        print(f"Historical data shape: {historical_data.shape}")
        print(f"Data columns: {historical_data.columns.tolist()}")
        
        # Check if we have enough data points
        if len(historical_data) < 20:
            return jsonify({"error": "Insufficient historical data for optimization. Need at least 20 data points."}), 400
        
        # Optimize portfolio
        optimization_start_time = time.time()
        optimal_weights = portfolio_optimizer.optimize_portfolio(historical_data)
        optimization_time = time.time() - optimization_start_time
        print(f"Portfolio optimization completed in {optimization_time:.2f} seconds")
        
        if optimal_weights is None or len(optimal_weights) == 0:
            return jsonify({"error": "Portfolio optimization failed. Please try different stocks."}), 500
        
        # Generate explanation
        explanation_start_time = time.time()
        explanation = portfolio_optimizer.generate_explanation(
            symbols, optimal_weights, historical_data
        )
        explanation_time = time.time() - explanation_start_time
        print(f"Explanation generated in {explanation_time:.2f} seconds")
        
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
        print(f"Risk metrics calculated in {metrics_time:.2f} seconds")
        
        total_time = time.time() - total_start_time
        print(f"Total optimization request completed in {total_time:.2f} seconds")
        
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
    

@app.route('/api/portfolio/save', methods=['POST'])
def save_portfolio():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 401

    try:
        data = request.get_json()
        portfolio_name = data.get('name', 'My Portfolio')
        allocations = data.get('allocations', [])
        projected_return = data.get('projected_return', 0)

        if not allocations:
            return jsonify({"error": "No allocations provided"}), 400

        # Create new portfolio
        new_portfolio = Portfolio(
            user_id=user_id,
            name=portfolio_name,
            projected_return=projected_return
        )
        db.session.add(new_portfolio)
        db.session.flush()  # Get the portfolio ID

        # Add portfolio stocks
        for allocation in allocations:
            symbol = allocation.get('symbol')
            weight = allocation.get('weight', 0)
            name = allocation.get('name', symbol)

            # Get or create validated stock entry
            validated_stock = ValidatedStock.query.filter_by(symbol=symbol).first()
            if not validated_stock:
                # Create new validated stock entry
                stock_info = stock_data_service.get_stock_info(symbol)
                validated_stock = ValidatedStock(
                    symbol=symbol,
                    name=name,
                    industry=stock_info.get('sector', 'Unknown') if stock_info else 'Unknown',
                    current_price=stock_info.get('current_price', 0) if stock_info else 0,
                    market_cap=stock_info.get('market_cap', 0) if stock_info else 0,
                    quality_score=allocation.get('quality_score', 0)
                )
                db.session.add(validated_stock)

            # Add portfolio stock
            portfolio_stock = PortfolioStock(
                portfolio_id=new_portfolio.id,
                stock_symbol=symbol,
                weight=weight
            )
            db.session.add(portfolio_stock)

        db.session.commit()
        
        return jsonify({
            "message": "Portfolio saved successfully",
            "portfolio_id": new_portfolio.id,
            "portfolio_name": portfolio_name
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error saving portfolio: {e}")
        return jsonify({"error": f"Failed to save portfolio: {str(e)}"}), 500

@app.route('/api/portfolio/list', methods=['GET'])
def list_user_portfolios():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 401

    try:
        portfolios = Portfolio.query.filter_by(user_id=user_id).all()
        
        portfolio_list = []
        for portfolio in portfolios:
            # Get portfolio stocks with their details
            portfolio_stocks = []
            for ps in portfolio.stocks:
                validated_stock = ValidatedStock.query.filter_by(symbol=ps.stock_symbol).first()
                if validated_stock:
                    portfolio_stocks.append({
                        "symbol": ps.stock_symbol,
                        "name": validated_stock.name,
                        "industry": validated_stock.industry,
                        "weight": ps.weight,
                        "quality_score": validated_stock.quality_score
                    })
                else:
                    # Fallback if validated stock not found
                    portfolio_stocks.append({
                        "symbol": ps.stock_symbol,
                        "name": ps.stock_symbol,
                        "industry": "Unknown",
                        "weight": ps.weight,
                        "quality_score": 0
                    })

            portfolio_list.append({
                "id": portfolio.id,
                "name": portfolio.name,
                "created_at": portfolio.created_at.isoformat(),
                "projected_return": portfolio.projected_return,
                "stocks": portfolio_stocks
            })

        return jsonify({"portfolios": portfolio_list})

    except Exception as e:
        print(f"Error listing portfolios: {e}")
        return jsonify({"error": f"Failed to list portfolios: {str(e)}"}), 500



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
