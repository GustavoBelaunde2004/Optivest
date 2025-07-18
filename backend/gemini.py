import google.generativeai as genai
import json
import re
from stock_validator import StockValidator

class GeminiService:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required")
        
        genai.configure(api_key=api_key)
        self.validator = StockValidator()
        
        try:
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        except:
            try:
                self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            except:
                try:
                    self.model = genai.GenerativeModel('gemini-1.5-flash')
                except:
                    self.model = genai.GenerativeModel('gemini-pro')
    
    def get_stock_recommendations(self, industries):
        """Get stock recommendations for selected industries"""
        
        # Calculate stocks per industry (aim for 15 initial recommendations)
        stocks_per_industry = max(3, 15 // len(industries))
        
        prompt = f"""
You are a financial advisor specializing in beginner-friendly investments.
Given the following industries: {', '.join(industries)}, recommend exactly {stocks_per_industry} publicly traded stocks for each industry.

For each stock, provide:
1. Stock symbol (ticker)
2. Company name  
3. Brief description explaining why it's good for beginner investors
4. Industry category

Return the response as a JSON array with this exact structure:
[
    {{
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "description": "A stable technology company with consistent growth and strong brand loyalty, making it ideal for beginner investors.",
        "industry": "Technology"
    }}
]

Focus on well-established companies with:
- Strong financial stability
- Good dividend history (where applicable)
- Clear business models
- Lower volatility suitable for beginners

Only include real, currently traded stocks with valid ticker symbols.
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            response_text = response.text
            
            # Find JSON array in the response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                stocks = json.loads(json_str)
                
                # Validate and clean the data
                validated_stocks = []
                for stock in stocks:
                    if all(key in stock for key in ['symbol', 'name', 'description', 'industry']):
                        # Clean up the symbol (remove any extra characters)
                        stock['symbol'] = stock['symbol'].upper().strip()
                        validated_stocks.append(stock)
                
                return validated_stocks[:15]  # Allow more initial recommendations for filtering
            else:
                raise ValueError("Could not parse JSON from Gemini response")
                
        except Exception as e:
            print(f"Error getting recommendations from Gemini: {e}")
            # Fallback recommendations
            return self._get_fallback_recommendations(industries)
    
    def _get_fallback_recommendations(self, industries):
        """Fallback stock recommendations if Gemini fails"""
        fallback_stocks = {
            "Technology": [
                {"symbol": "AAPL", "name": "Apple Inc.", "description": "Leading technology company with strong brand and consistent growth.", "industry": "Technology"},
                {"symbol": "MSFT", "name": "Microsoft Corp.", "description": "Diversified technology giant with cloud computing leadership.", "industry": "Technology"},
                {"symbol": "GOOGL", "name": "Alphabet Inc.", "description": "Google's parent company dominating search and digital advertising.", "industry": "Technology"}
            ],
            "Healthcare": [
                {"symbol": "JNJ", "name": "Johnson & Johnson", "description": "Diversified healthcare company with pharmaceutical and consumer products.", "industry": "Healthcare"},
                {"symbol": "PFE", "name": "Pfizer Inc.", "description": "Major pharmaceutical company with strong drug pipeline.", "industry": "Healthcare"}
            ],
            "Finance": [
                {"symbol": "JPM", "name": "JPMorgan Chase", "description": "Largest US bank with diversified financial services.", "industry": "Finance"},
                {"symbol": "BAC", "name": "Bank of America", "description": "Major banking institution with strong retail and commercial presence.", "industry": "Finance"}
            ],
            "Energy": [
                {"symbol": "XOM", "name": "Exxon Mobil", "description": "Major integrated oil and gas company with global operations.", "industry": "Energy"},
                {"symbol": "CVX", "name": "Chevron Corp.", "description": "Well-managed energy company with strong dividend history.", "industry": "Energy"}
            ]
        }
        
        recommendations = []
        for industry in industries:
            if industry in fallback_stocks:
                recommendations.extend(fallback_stocks[industry])
        
        return recommendations[:20]

    def get_validated_stock_recommendations(self, industries):
        """Get stock recommendations and validate them for quality"""
        print(f"\n🤖 GEMINI AI: Generating recommendations for {len(industries)} industries...")
        
        # Get initial recommendations from Gemini
        raw_recommendations = self.get_stock_recommendations(industries)
        
        if not raw_recommendations:
            print("No recommendations received from Gemini")
            return []
        
        print(f"   Generated {len(raw_recommendations)} initial recommendations")
        
        # Validate the recommendations
        validated_stocks = self.validator.validate_stocks(raw_recommendations, max_stocks=20)
        
        if validated_stocks:
            self.validator.display_validation_summary(validated_stocks)
        
        return validated_stocks

    def extract_stock_symbol(self, user_message):
        prompt = (
            "Extract the most likely US stock ticker symbol (e.g., TSLA for Tesla) and company name from the following message. "
            "If a ticker is found, return it. If not, return the company name. If neither, return an empty string.\n"
            f"Message: {user_message}\n"
            "Ticker: <ticker>\nCompany: <company>"
        )
        try:
            response = self.model.generate_content(prompt)
            lines = response.text.strip().split('\n')
            ticker = ''
            company = ''
            for line in lines:
                if line.lower().startswith('ticker:'):
                    ticker = line.split(':', 1)[1].strip()
                elif line.lower().startswith('company:'):
                    company = line.split(':', 1)[1].strip()
            return ticker, company
        except Exception as e:
            print(f"Gemini extraction error: {e}")
            return '', ''
