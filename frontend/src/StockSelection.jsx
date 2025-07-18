import React, { useEffect, useState } from 'react';

function StockSelection({ industries, onConfirm }) {
  const [stocks, setStocks] = useState([]);
  const [selected, setSelected] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Fetch recommended stocks when industries change
  useEffect(() => {
    setLoading(true);
    setError('');
    fetch('http://localhost:5000/api/stocks/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ industries }),
    })
      .then(res => res.json())
      .then(data => {
        if (data.stocks) {
          setStocks(data.stocks);
        } else {
          setError(data.error || 'No stocks found.');
        }
        setLoading(false);
      })
      .catch(() => {
        setError('Failed to fetch stocks.');
        setLoading(false);
      });
  }, [industries]);

  // Toggle selection of a stock
  const toggleStock = (stock) => {
    setSelected(sel => {
      if (sel.some(s => s.symbol === stock.symbol)) {
        return sel.filter(s => s.symbol !== stock.symbol);
      } else if (sel.length < 10) {
        return [...sel, stock];
      } else {
        return sel; // Do not add more than 10
      }
    });
  };

  if (loading) return (
    <section className="min-h-screen flex flex-col items-center justify-center font-mono bg-gradient-to-r from-cyan-500 via-indigo-500 to-sky-500">
      <div className="flex flex-col items-center justify-center">
        <svg className="animate-spin h-12 w-12 text-blue-200 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path>
        </svg>
        <div className="text-2xl text-white font-semibold drop-shadow">Loading stocks...</div>
      </div>
    </section>
  );
  if (error) return <div className="text-center text-red-500">{error}</div>;

  return (
    <section className="min-h-screen flex flex-col items-center justify-center font-mono bg-gradient-to-r from-cyan-500 via-indigo-500 to-sky-500">
      <h1 className="text-4xl font-bold text-white mb-2 drop-shadow-lg">Select stocks you're interested in</h1>
      <div className="text-lg text-white/90 mb-6">Suggested: Choose at least 5 stocks</div>
      <div className="w-full max-w-6xl flex flex-wrap gap-6 justify-center items-stretch mb-8">
        {stocks.slice(0, 10).map((stock, idx) => (
          <button
            key={stock.symbol}
            onClick={() => toggleStock(stock)}
            disabled={selected.length >= 10 && !selected.some(s => s.symbol === stock.symbol)}
            className={`transition-all duration-300 px-5 py-5 rounded-2xl shadow-lg text-left text-base font-semibold cursor-pointer select-none border-2 
              ${selected.some(s => s.symbol === stock.symbol) ? 'bg-blue-400/80 text-white border-blue-600 scale-105' : 'bg-white/80 text-blue-900 border-blue-200 hover:bg-blue-100 hover:scale-105'} 
              ${idx % 4 === 0 ? 'rotate-2' : idx % 4 === 1 ? '-rotate-2' : idx % 4 === 2 ? 'rotate-1' : '-rotate-1'}
              ${selected.length >= 10 && !selected.some(s => s.symbol === stock.symbol) ? 'opacity-50 cursor-not-allowed' : ''}
            `}
            style={{ minWidth: '230px', minHeight: '160px', maxWidth: '250px', boxShadow: '0 4px 24px 0 rgba(0,0,0,0.08)', display: 'block', verticalAlign: 'top', whiteSpace: 'normal', wordBreak: 'break-word' }}
          >
            <div className="font-bold text-lg mb-1">{stock.name} <span className="text-base font-normal">({stock.symbol})</span></div>
            <div className="text-sm mb-1">{stock.description}</div>
            <div className="text-xs text-blue-900/70 mb-1">Industry: {stock.industry}</div>
            <div className="text-xs text-blue-900/70 mb-1">Price: {stock.current_price} | Market Cap: {stock.market_cap}</div>
            {stock.quality_score && <div className="text-xs text-green-700 mt-1">Quality Score: {stock.quality_score}</div>}
          </button>
        ))}
      </div>
      {/* Confirm selection button */}
      <button
        onClick={() => onConfirm(selected)}
        disabled={selected.length < 5}
        className="mt-8 px-10 py-3 text-2xl rounded-md border-2 border-blue-700 bg-gradient-to-tr from-green-400 to-blue-500 hover:from-cyan-400 hover:to-indigo-500 text-white disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105"
      >
        Confirm
      </button>
    </section>
  );
}

export default StockSelection; 