# Portfolio Optimizer

An intelligent portfolio optimization application that helps users build diversified investment portfolios based on their experience level, preferred industries, and risk tolerance. The app uses AI-powered stock recommendations and modern portfolio theory to create optimized asset allocations.

## Features

- **User Authentication**: Secure login and registration system with session management
- **Experience-Based Recommendations**: Tailored portfolio suggestions based on investment experience
- **Industry Selection**: Choose from 12+ industry sectors for diversified investments
- **AI-Powered Stock Analysis**: Leverages Google's Gemini AI for intelligent stock recommendations
- **Portfolio Optimization**: Uses Modern Portfolio Theory (Markowitz optimization) for optimal asset allocation
- **Interactive Visualizations**: Beautiful pie charts showing portfolio composition using Recharts
- **Portfolio Management**: Save, view, and manage multiple portfolios
- **Real-time Stock Data**: Integration with Yahoo Finance for up-to-date market information

## Architecture

### Frontend
- **React 19** with Vite for modern, fast development
- **Tailwind CSS** for responsive, utility-first styling
- **Recharts** for interactive data visualizations
- **ESLint** for code quality and consistency

### Backend
- **Flask** web framework with SQLAlchemy ORM
- **SQLite** database for user and portfolio storage
- **Google Gemini AI** for intelligent stock analysis
- **Yahoo Finance API** integration via yfinance
- **CVXPY** for convex optimization (portfolio optimization)
- **NumPy & Pandas** for numerical computations
- **Flask-CORS** for cross-origin resource sharing

## Installation

### Prerequisites
- Node.js (v16 or higher)
- Python 3.8+
- Google Gemini API key

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the backend directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_secret_key_here
```

5. Run the Flask application:
```bash
python app.py
```

The backend will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 🔧 Configuration

### Environment Variables

**Backend (.env)**:
- `GEMINI_API_KEY`: Your Google Gemini AI API key
- `SECRET_KEY`: Flask session secret key

**Frontend**:
- API base URL is configured in `src/config.js`

## Usage

1. **Register/Login**: Create an account or log in to access the portfolio optimizer
2. **Select Experience Level**: Choose your investment experience level)
3. **Choose Industries**: Select industries you're interested in investing in
4. **Stock Selection**: Review AI-recommended stocks or add custom stocks
5. **Portfolio Optimization**: Generate an optimized portfolio allocation
6. **Save Portfolio**: Save your portfolio for future reference
7. **View Results**: Analyze your portfolio with interactive charts

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/industries` - Get available industries
- `POST /api/stocks/recommend` - Get stock recommendations
- `POST /api/portfolio/optimize` - Optimize portfolio allocation
- `POST /api/portfolio/save` - Save portfolio
- `GET /api/portfolios` - Get user portfolios
- Authentication endpoints under `/auth/`

For detailed API documentation, see `backend/API_DOCUMENTATION.md`

## Portfolio Optimization

The application uses Modern Portfolio Theory to optimize portfolios by:
- Minimizing risk for a given level of expected return
- Maximizing return for a given level of risk
- Finding the efficient frontier of optimal portfolios
- Incorporating correlation analysis between assets


## 📄 License

This project is open source and available under the MIT License.

