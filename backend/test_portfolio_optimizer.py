import unittest
from portfolio_optimizer import optimize_portfolio
from stock_validator import validate_stock
from stock_data_service import get_stock_data
from models import Portfolio, Stock

class TestPortfolioOptimizer(unittest.TestCase):
    def test_optimize_portfolio_basic(self):
        stocks = [Stock('AAPL', 0.5), Stock('GOOG', 0.5)]
        portfolio = Portfolio(stocks)
        result = optimize_portfolio(portfolio)
        self.assertIsNotNone(result)

    def test_optimize_portfolio_empty(self):
        portfolio = Portfolio([])
        result = optimize_portfolio(portfolio)
        self.assertEqual(result, None)

    def test_validate_stock_valid(self):
        self.assertTrue(validate_stock('AAPL'))

    def test_validate_stock_invalid(self):
        self.assertFalse(validate_stock('INVALID'))

    def test_get_stock_data(self):
        data = get_stock_data('AAPL')
        self.assertIsInstance(data, dict)

    def test_portfolio_total_weight(self):
        stocks = [Stock('AAPL', 0.6), Stock('GOOG', 0.4)]
        portfolio = Portfolio(stocks)
        total_weight = sum(stock.weight for stock in portfolio.stocks)
        self.assertAlmostEqual(total_weight, 1.0)

if __name__ == '__main__':
    unittest.main()
