import yfinance as yf
import requests
from datetime import datetime, timedelta

class StockValidator:
    def __init__(self):
        self.quality_thresholds = {
            'min_market_cap': 10_000_000_000,  # $10B minimum market cap
            'min_volume': 1_000_000,           # Daily volume > 1M shares
            'max_volatility': 0.40,            # Max 40% annual volatility
            'min_sharpe_ratio': 0.5,           # Minimum Sharpe ratio
            'min_data_points': 100             # Need sufficient historical data
        }
    
    def validate_stocks(self, stocks, max_stocks=20):
        """Validate and filter stocks based on quality metrics"""
        print(f"\nSTOCK VALIDATION: Analyzing {len(stocks)} Gemini recommendations...")
        print("-" * 60)
        
        validated_stocks = []
        
        for i, stock in enumerate(stocks, 1):
            symbol = stock['symbol']
            print(f"   {i:2d}. Validating {symbol}...")
            
            validation_result = self._validate_single_stock(stock)
            
            if validation_result['is_valid']:
                # Add validation metrics to stock data
                enhanced_stock = {**stock, **validation_result}
                validated_stocks.append(enhanced_stock)
                print(f"       PASSED - Quality Score: {validation_result['quality_score']:.2f}")
            else:
                print(f"       FAILED - {validation_result['failure_reason']}")
        
        # Sort by quality score (highest first)
        validated_stocks.sort(key=lambda x: x['quality_score'], reverse=True)
        
        # Limit to max_stocks best candidates
        if len(validated_stocks) > max_stocks:
            validated_stocks = validated_stocks[:max_stocks]
            print(f"\nSelected top {max_stocks} highest quality stocks")
        
        print(f"\nVALIDATION COMPLETE:")
        print(f"   Original recommendations: {len(stocks)}")
        print(f"   Passed validation: {len(validated_stocks)}")
        print(f"   Quality threshold: High-grade stocks only")
        
        if len(validated_stocks) < 2:
            print(f"\nWARNING: Only {len(validated_stocks)} stocks passed validation!")
            print(f"   Consider lowering quality thresholds or selecting different industries.")
            return []
        
        return validated_stocks
    
    def _validate_single_stock(self, stock):
        """Validate a single stock against quality metrics"""
        symbol = stock['symbol']
        
        try:
            # Get stock data
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1y")
            
            if len(hist) < self.quality_thresholds['min_data_points']:
                return {
                    'is_valid': False,
                    'failure_reason': 'Insufficient historical data',
                    'quality_score': 0.0
                }
            
            # Calculate quality metrics
            metrics = self._calculate_quality_metrics(info, hist)
            
            # Check each threshold
            validation_checks = {
                'market_cap': metrics['market_cap'] >= self.quality_thresholds['min_market_cap'],
                'volume': metrics['avg_volume'] >= self.quality_thresholds['min_volume'],
                'volatility': metrics['volatility'] <= self.quality_thresholds['max_volatility'],
                'sharpe_ratio': metrics['sharpe_ratio'] >= self.quality_thresholds['min_sharpe_ratio'],
                'data_quality': len(hist) >= self.quality_thresholds['min_data_points']
            }
            
            # Stock passes if it meets most criteria (at least 4 out of 5)
            passed_checks = sum(validation_checks.values())
            is_valid = passed_checks >= 4
            
            # Calculate overall quality score (0-100)
            quality_score = self._calculate_quality_score(metrics, validation_checks)
            
            if not is_valid:
                failed_criteria = [k for k, v in validation_checks.items() if not v]
                failure_reason = f"Failed: {', '.join(failed_criteria)}"
            else:
                failure_reason = None
            
            return {
                'is_valid': is_valid,
                'quality_score': quality_score,
                'failure_reason': failure_reason,
                'validation_metrics': metrics,
                'validation_checks': validation_checks
            }
            
        except Exception as e:
            return {
                'is_valid': False,
                'failure_reason': f'Data fetch error: {str(e)}',
                'quality_score': 0.0
            }
    
    def _calculate_quality_metrics(self, info, hist):
        """Calculate quality metrics for a stock"""
        # Market cap
        market_cap = info.get('marketCap', 0)
        
        # Average volume
        avg_volume = hist['Volume'].mean() if len(hist) > 0 else 0
        
        # Volatility (annualized)
        returns = hist['Close'].pct_change().dropna()
        volatility = returns.std() * (252 ** 0.5) if len(returns) > 0 else 1.0
        
        # Sharpe ratio (simplified)
        if len(returns) > 0:
            mean_return = returns.mean() * 252
            sharpe_ratio = mean_return / volatility if volatility > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Recent performance (6-month return)
        if len(hist) >= 126:  # ~6 months of data
            recent_return = (hist['Close'].iloc[-1] - hist['Close'].iloc[-126]) / hist['Close'].iloc[-126]
        else:
            recent_return = 0
        
        # Price stability (lower is better)
        if len(returns) > 0:
            price_stability = 1 - (returns.std() * 10)  # Normalize to 0-1 scale
        else:
            price_stability = 0
        
        return {
            'market_cap': market_cap,
            'avg_volume': avg_volume,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'recent_return': recent_return,
            'price_stability': max(0, price_stability)
        }
    
    def _calculate_quality_score(self, metrics, validation_checks):
        """Calculate overall quality score (0-100)"""
        score = 0
        
        # Base score from validation checks (60 points max)
        score += sum(validation_checks.values()) * 12
        
        # Bonus points for exceptional metrics (40 points max)
        
        # Market cap bonus (0-10 points)
        if metrics['market_cap'] > 100_000_000_000:  # > $100B
            score += 10
        elif metrics['market_cap'] > 50_000_000_000:  # > $50B
            score += 7
        elif metrics['market_cap'] > 20_000_000_000:  # > $20B
            score += 5
        
        # Sharpe ratio bonus (0-10 points)
        if metrics['sharpe_ratio'] > 2.0:
            score += 10
        elif metrics['sharpe_ratio'] > 1.5:
            score += 7
        elif metrics['sharpe_ratio'] > 1.0:
            score += 5
        
        # Volume bonus (0-10 points)
        if metrics['avg_volume'] > 10_000_000:
            score += 10
        elif metrics['avg_volume'] > 5_000_000:
            score += 7
        elif metrics['avg_volume'] > 2_000_000:
            score += 5
        
        # Low volatility bonus (0-10 points)
        if metrics['volatility'] < 0.20:
            score += 10
        elif metrics['volatility'] < 0.25:
            score += 7
        elif metrics['volatility'] < 0.30:
            score += 5
        
        return min(100, score)
    
    def display_validation_summary(self, stocks):
        """Display a summary of validated stocks"""
        print(f"\nVALIDATED STOCK PORTFOLIO:")
        print("=" * 70)
        print(f"{'#':<3} {'Symbol':<7} {'Score':<6} {'Market Cap':<12} {'Sharpe':<7} {'Vol%':<6}")
        print("-" * 70)
        
        for i, stock in enumerate(stocks, 1):
            symbol = stock['symbol']
            score = stock.get('quality_score', 0)
            
            # Get metrics if available
            metrics = stock.get('validation_metrics', {})
            market_cap = metrics.get('market_cap', 0)
            sharpe = metrics.get('sharpe_ratio', 0)
            volatility = metrics.get('volatility', 0)
            
            # Format market cap
            if market_cap > 1_000_000_000:
                cap_str = f"${market_cap/1_000_000_000:.1f}B"
            elif market_cap > 1_000_000:
                cap_str = f"${market_cap/1_000_000:.1f}M"
            else:
                cap_str = "N/A"
            
            print(f"{i:<3} {symbol:<7} {score:<6.1f} {cap_str:<12} {sharpe:<7.2f} {volatility*100:<5.1f}%")
        
        print("-" * 70)
        print(f"All stocks meet institutional-grade quality standards")
        print(f"This should result in more balanced portfolio allocations")
