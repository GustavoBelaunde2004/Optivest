from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    portfolios = db.relationship('Portfolio', backref='user', lazy=True)


class ValidatedStock(db.Model):
    __tablename__ = 'validated_stocks'
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(120))
    description = db.Column(db.Text)
    industry = db.Column(db.String(80))
    current_price = db.Column(db.Float)
    market_cap = db.Column(db.Float)
    quality_score = db.Column(db.Float)
    validation_metrics = db.Column(db.Text)   
    validation_checks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Portfolio(db.Model):
    __tablename__ = 'portfolios'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    projected_return = db.Column(db.Float)

    stocks = db.relationship('PortfolioStock', backref='portfolio', lazy=True)


class PortfolioStock(db.Model):
    __tablename__ = 'portfolio_stocks'
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id'), nullable=False)
    stock_symbol = db.Column(db.String(10), db.ForeignKey('validated_stocks.symbol'), nullable=False)
    weight = db.Column(db.Float, nullable=False)
