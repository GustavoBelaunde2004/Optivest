# Portfolio Optimizer Backend API

## Overview
DOCS for Backend API   

## Base URL
```
http://localhost:5000
```

## API Endpoints

### 1. Health Check
**GET** `/api/health`

**Response:**
```json
{
  "status": "healthy",
  "message": "Portfolio Optimizer API is running"
}
```

### 2. Get Industries
**GET** `/api/industries`

**Response:**
```json
{
  "industries": [
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
}
```

### 3. Get Stock Recommendations
**POST** `/api/stocks/recommend`

**Request Body:**
```json
{
  "industries": ["Technology", "Healthcare", "Finance"]
}
```

**Response:**
```json
{
  "stocks": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "industry": "Technology",
      "description": "Leading technology company with strong market position",
      "current_price": "N/A",
      "market_cap": "N/A",
      "quality_score": 85.0
    }
  ]
}
```

**Notes:**
- Takes 1-2 minutes due to AI generation + quality validation
- Returns 8 highest-quality stocks (scored 80-95)
- All stocks pass institutional-grade validation filters

### 4. Optimize Portfolio
**POST** `/api/portfolio/optimize`

**Request Body:**
```json
{
  "stocks": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "industry": "Technology",
      "description": "Leading technology company"
    }
  ],
  "investment_amount": 10000,
  "data_period": "2y"
}
```

**Response:**
```json
{
  "allocations": [
    {
      "symbol": "AAPL",
      "weight": 0.25,
      "amount": 2500.0,
      "name": "Apple Inc."
    }
  ],
  "explanation": "Portfolio allocation explanation...",
  "total_investment": 10000,
  "risk_metrics": {
    "annual_return": 0.12,
    "annual_volatility": 0.18,
    "sharpe_ratio": 0.67,
    "max_drawdown": 0.15
  },
  "performance_info": {
    "total_time": "2.05s",
    "data_fetch_time": "2.01s",
    "optimization_time": "0.03s",
    "explanation_time": "0.01s",
    "metrics_time": "0.01s"
  }
}
```

**Data Period Options:**
- `"3mo"` - 3 months (~63 trading days)
- `"6mo"` - 6 months (~126 trading days)  
- `"1y"` - 1 year (~252 trading days)
- `"2y"` - 2 years (~504 trading days) - **Default**

## Error Responses

All endpoints return error responses in this format:
```json
{
  "error": "Error message description"
}
```

**Common Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid input)
- `500` - Internal Server Error

## Quality Validation

Stock recommendations go through comprehensive validation:
- **Market Cap**: >$10B
- **Volume**: >1M daily shares
- **Volatility**: <40% annual
- **Sharpe Ratio**: >0.5
- **Data Quality**: Sufficient historical data

## Performance Notes

- **Stock Recommendations**: 60-120 seconds (AI + validation)
- **Portfolio Optimization**: 2-5 seconds
- **Concurrent Requests**: Supported
- **Rate Limits**: None currently implemented

## Environment Setup

Required environment variables in `backend/.env`:
```
GEMINI_API_KEY=your_gemini_api_key_here
```


