import numpy as np
import pandas as pd
from scipy.optimize import minimize
import cvxpy as cp

class PortfolioOptimizer:
    def __init__(self):
        pass
    
    def calculate_portfolio_metrics(self, returns, weights):
        """Calculate portfolio return, volatility, and Sharpe ratio"""
        portfolio_return = np.sum(returns.mean() * weights) * 252  # Annualized
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
        
        return portfolio_return, portfolio_volatility
    
    def optimize_portfolio(self, price_data, method="max_sharpe"):
        """Optimize portfolio using Modern Portfolio Theory"""
        import time
        start_time = time.time()
        
        print(f"Starting portfolio optimization...")
        print(f"Data shape: {price_data.shape}")
        print(f"Method: {method}")
        
        # Calculate returns
        returns = price_data.pct_change().dropna()
        
        n_assets = len(returns.columns)
        print(f"Number of assets: {n_assets}")
        print(f"Data points: {len(returns)}")
        
        # Mean returns (annualized)
        mu = returns.mean() * 252
        
        # Covariance matrix (annualized)
        cov_matrix = returns.cov() * 252
        
        print(f"Computing optimization...")
        
        if method == "max_sharpe":
            result = self._maximize_sharpe_ratio(mu, cov_matrix, n_assets)
        elif method == "min_variance":
            result = self._minimize_variance(cov_matrix, n_assets)
        else:
            # Default to equal weights if optimization fails
            result = np.array([1/n_assets] * n_assets)
        
        end_time = time.time()
        optimization_time = end_time - start_time
        print(f"Optimization completed in {optimization_time:.2f} seconds")
        
        return result
    
    def _maximize_sharpe_ratio(self, mu, cov_matrix, n_assets, risk_free_rate=0.02):
        """Maximize Sharpe ratio using convex optimization"""
        try:
            print(f"Setting up optimization problem...")
            print(f"Assets: {n_assets}")
            
            # Define optimization variables
            weights = cp.Variable(n_assets)
            
            # Portfolio return and risk
            portfolio_return = cp.sum(cp.multiply(mu.values, weights))
            portfolio_risk = cp.quad_form(weights, cov_matrix.values)
            
            print(f"Trying unconstrained optimization first...")
            
            # Try unconstrained optimization first (only sum to 1 and non-negative)
            basic_constraints = [
                cp.sum(weights) == 1,  # Weights sum to 1
                weights >= 0           # Non-negative weights (long-only)
            ]
            
            # Objective: Maximize Sharpe ratio (return per unit risk)
            # We use return - 0.5 * risk as a proxy for Sharpe ratio
            objective = cp.Maximize(portfolio_return - 0.5 * portfolio_risk)
            
            # Solve unconstrained problem
            problem = cp.Problem(objective, basic_constraints)
            result = problem.solve(verbose=False)
            
            if problem.status in [cp.OPTIMAL, cp.OPTIMAL_INACCURATE]:
                unconstrained_weights = weights.value
                
                if unconstrained_weights is not None:
                    unconstrained_weights = np.array(unconstrained_weights)
                    unconstrained_weights = np.maximum(unconstrained_weights, 0)
                    unconstrained_weights = unconstrained_weights / np.sum(unconstrained_weights)
                    
                    # Check if any weight is too small (< 0.5%)
                    small_weights = unconstrained_weights < 0.005
                    num_small = np.sum(small_weights)
                    
                    if num_small == 0:
                        print(f"All weights significant, using unconstrained solution")
                        return unconstrained_weights
                    else:
                        print(f"{num_small} assets have tiny allocations (< 0.5%)")
                        print(f"Applying minimum 1% constraint for practical trading...")
            
            # Apply minimum allocation constraint if needed
            print(f"Applying constraints: min 1%, max 50% per asset")
            
            constrained_constraints = [
                cp.sum(weights) == 1,  # Weights sum to 1
                weights >= 0.01,       # Minimum 1% allocation (for practical trading)
                weights <= 0.5         # Maximum 50% allocation (for diversification)
            ]
            
            # Solve constrained problem
            constrained_problem = cp.Problem(objective, constrained_constraints)
            constrained_result = constrained_problem.solve(verbose=False)
            
            print(f"Constrained optimization status: {constrained_problem.status}")
            
            if constrained_problem.status in [cp.OPTIMAL, cp.OPTIMAL_INACCURATE]:
                optimal_weights = weights.value
                
                if optimal_weights is not None and len(optimal_weights) == n_assets:
                    optimal_weights = np.array(optimal_weights)
                    optimal_weights = np.maximum(optimal_weights, 0)
                    optimal_weights = optimal_weights / np.sum(optimal_weights)
                    
                    return optimal_weights
            
            print("Both optimizations failed, using equal weights")
            return np.array([1/n_assets] * n_assets)
                
        except Exception as e:
            print(f"Error in optimization: {e}")
            import traceback
            traceback.print_exc()
            return np.array([1/n_assets] * n_assets)
    
    def _minimize_variance(self, cov_matrix, n_assets):
        """Minimize portfolio variance"""
        try:
            weights = cp.Variable(n_assets)
            
            # Objective: minimize variance
            objective = cp.Minimize(cp.quad_form(weights, cov_matrix))
            
            # Constraints
            constraints = [
                cp.sum(weights) == 1,
                weights >= 0.01,
                weights <= 0.5
            ]
            
            problem = cp.Problem(objective, constraints)
            problem.solve()
            
            if problem.status == cp.OPTIMAL:
                return weights.value
            else:
                return np.array([1/n_assets] * n_assets)
                
        except Exception as e:
            print(f"Error in variance minimization: {e}")
            return np.array([1/n_assets] * n_assets)
    
    def calculate_risk_metrics(self, price_data, weights):
        """Calculate risk metrics for the optimized portfolio"""
        returns = price_data.pct_change().dropna()
        
        # Portfolio returns
        portfolio_returns = (returns * weights).sum(axis=1)
        
        # Annualized metrics
        annual_return = portfolio_returns.mean() * 252
        annual_volatility = portfolio_returns.std() * np.sqrt(252)
        sharpe_ratio = annual_return / annual_volatility if annual_volatility > 0 else 0
        
        # Value at Risk (95% confidence)
        var_95 = np.percentile(portfolio_returns, 5)
        
        # Maximum Drawdown
        cumulative_returns = (1 + portfolio_returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        
        return {
            "annual_return": float(annual_return),
            "annual_volatility": float(annual_volatility),
            "sharpe_ratio": float(sharpe_ratio),
            "var_95": float(var_95),
            "max_drawdown": float(max_drawdown)
        }
    
    def generate_explanation(self, symbols, weights, price_data):
        """Generate beginner-friendly explanation of the optimization"""
        try:            
            returns = price_data.pct_change().dropna()
            
            # Ensure symbols is a list and weights is a numpy array
            if not isinstance(symbols, list):
                symbols = list(symbols)
            weights = np.array(weights)
            
            if len(symbols) != len(weights):
                return "Portfolio optimization completed successfully."
            
            # Find highest weighted stock
            max_weight_idx = np.argmax(weights)
            max_stock = symbols[max_weight_idx]
            
            # Count stocks with minimum allocations (~1%)
            min_allocation_stocks = [(symbols[i], weights[i]) for i in range(len(symbols)) if weights[i] <= 0.015]
            
            # Simple, concise explanation
            explanation_parts = []
            explanation_parts.append("Portfolio optimized using Modern Portfolio Theory for best risk-return balance.")
            explanation_parts.append(f"Highest allocation: {max_stock} ({weights[max_weight_idx]:.1%}) - best risk-adjusted returns.")
            
            if len(min_allocation_stocks) > 0:
                explanation_parts.append(f"{len(min_allocation_stocks)} stocks received 1% minimum allocation for diversification.")
            
            return "\n".join(explanation_parts)
            
        except Exception as e:
            return "Portfolio optimization completed successfully."