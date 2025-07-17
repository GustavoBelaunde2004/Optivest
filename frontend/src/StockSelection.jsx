import React, { useEffect, useState } from 'react';

function StockSelection({ industries, onConfirm }) {
  const [stocks, setStocks] = useState([]);
  const [selected, setSelected] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showChat, setShowChat] = useState(false);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [chatError, setChatError] = useState('');
  const [chatResult, setChatResult] = useState(null);

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

  // Handle chatbox submit for custom stock
  const handleChatSubmit = async (e) => {
    e.preventDefault();
    setChatLoading(true);
    setChatError('');
    setChatResult(null);
    try {
      // Send the custom stock symbol/name to backend for validation/info (using Gemini logic)
      const response = await fetch('http://localhost:5000/api/stocks/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ industries, custom_stock: chatInput }),
      });
      const data = await response.json();
      if (data.stocks && data.stocks.length > 0) {
        setChatResult(data.stocks[0]);
      } else {
        setChatError(data.error || 'No info found for that stock.');
      }
    } catch {
      setChatError('Failed to fetch stock info.');
    } finally {
      setChatLoading(false);
    }
  };

  // Add custom stock to selection
  const addCustomStock = () => {
    if (chatResult) {
      setSelected(sel =>
        sel.some(s => s.symbol === chatResult.symbol)
          ? sel
          : [...sel, chatResult]
      );
      setShowChat(false);
      setChatInput('');
      setChatResult(null);
    }
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
      {/* Other button and chatbox */}
      <div className="flex flex-col items-center w-full max-w-2xl">
        {!showChat && (
          <button
            onClick={() => setShowChat(true)}
            className="mt-4 px-8 py-3 text-xl rounded-md border-2 bg-gradient-to-tr from-purple-400 to-indigo-500 text-white hover:from-cyan-400 hover:to-indigo-500 transition-all duration-300 transform hover:scale-105"
          >
            Other
          </button>
        )}
        {showChat && (
          <form onSubmit={handleChatSubmit} className="w-full flex flex-col items-center mt-4 gap-2">
            <input
              type="text"
              value={chatInput}
              onChange={e => setChatInput(e.target.value)}
              placeholder="Type a stock symbol or name..."
              className="w-full max-w-md px-4 py-2 rounded border-2 border-blue-700 focus:border-blue-900 outline-none bg-white text-blue-900"
              required
            />
            <button
              type="submit"
              disabled={chatLoading || !chatInput}
              className="px-6 py-2 rounded bg-blue-500 text-white font-semibold disabled:opacity-50"
            >
              {chatLoading ? 'Searching...' : 'Ask Gemini'}
            </button>
            {chatError && (
              <div className="text-red-500 text-sm">
                {chatError === 'Please select at least one industry'
                  ? 'Type at least one industry.'
                  : chatError}
              </div>
            )}
            {chatResult && (
              <div className="bg-white/90 rounded p-4 mt-2 shadow w-full max-w-md flex flex-col items-start">
                <div className="font-bold text-lg mb-1">{chatResult.name} <span className="text-base font-normal">({chatResult.symbol})</span></div>
                <div className="text-base mb-1">{chatResult.description}</div>
                <div className="text-sm text-blue-900/70">Industry: {chatResult.industry}</div>
                <div className="text-sm text-blue-900/70">Price: {chatResult.current_price} | Market Cap: {chatResult.market_cap}</div>
                {chatResult.quality_score && <div className="text-xs text-green-700 mt-1">Quality Score: {chatResult.quality_score}</div>}
                <button
                  type="button"
                  onClick={addCustomStock}
                  className="mt-2 px-4 py-1 rounded bg-green-500 text-white font-semibold"
                >
                  Add to Selection
                </button>
              </div>
            )}
            <button
              type="button"
              onClick={() => { setShowChat(false); setChatInput(''); setChatResult(null); setChatError(''); }}
              className="mt-2 text-blue-900 underline font-semibold"
            >
              Cancel
            </button>
          </form>
        )}
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