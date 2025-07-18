import { useState, useEffect } from 'react';
import { API_BASE_URL } from './config';

function IndustrySelection({ onConfirm }) {
  const [industries, setIndustries] = useState([]); //state for industries
  const [selected, setSelected] = useState([]); //state for selected industries
  const [loading, setLoading] = useState(true); //state for loading
  const [error, setError] = useState(''); //state for error when fetching industries
  const [limitMsg, setLimitMsg] = useState(''); // state for limit message

  //fetch industries from backend
  useEffect(() => {
    fetch(`${API_BASE_URL}/api/industries`)
      .then(res => res.json())
      .then(data => {
        setIndustries(data.industries || []);
        setLoading(false);
      })
      .catch(() => {
        setError('Failed to load industries.');
        setLoading(false);
      });
  }, []);

  const toggleIndustry = (industry) => {
    setLimitMsg('');
    setSelected(sel => {
      if (sel.includes(industry)) {
        return sel.filter(i => i !== industry);
      } else if (sel.length < 3) {
        return [...sel, industry];
      } else {
        setLimitMsg('You can select up to 3 industries.');
        return sel;
      }
    });
  };

  //if loading, show loading message
  if (loading) return <div className="text-center text-xl">Loading industries...</div>;
  if (error) return <div className="text-center text-red-500">{error}</div>;

  return (
    <section className="min-h-screen flex flex-col items-center justify-center font-mono bg-gradient-to-r from-cyan-500 via-indigo-500 to-sky-500">
      <h1 className="text-4xl font-bold text-white mb-8 drop-shadow-lg">What industries are you interested in?</h1>
      {/* Industry buttons, inspo pinterest with tilt*/}
      <div className="w-full max-w-4xl flex flex-wrap gap-6 justify-center items-center mb-8">
        {industries.map((industry, idx) => (
          <button
            key={industry}
            onClick={() => toggleIndustry(industry)}
            disabled={!selected.includes(industry) && selected.length >= 3}
            //if selected, show blue, if not, show white
            className={`transition-all duration-300 px-8 py-6 rounded-2xl shadow-lg text-xl font-semibold cursor-pointer select-none border-2 
              ${selected.includes(industry) ? 'bg-blue-400/80 text-white border-blue-600 scale-105' : 'bg-white/80 text-blue-900 border-blue-200 hover:bg-blue-100 hover:scale-105'} 
              ${!selected.includes(industry) && selected.length >= 3 ? 'opacity-50 cursor-not-allowed' : ''}
              ${idx % 3 === 0 ? 'rotate-2' : idx % 3 === 1 ? '-rotate-2' : 'rotate-1'}
            `}
            style={{ minWidth: '200px', minHeight: '80px', boxShadow: '0 4px 24px 0 rgba(0,0,0,0.08)' }} 
          >
            {industry}
          </button>
        ))}
      </div>
      {limitMsg && <div className="text-red-500 mb-4 text-lg font-semibold">{limitMsg}</div>}
      {/* Confirm button*/}
      <button
        onClick={() => onConfirm(selected)}
        disabled={selected.length === 0}
        className="px-10 py-3 text-2xl rounded-md border-2 bg-gradient-to-tr from-green-400 to-blue-500 hover:from-cyan-400 hover:to-indigo-500 text-white disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105"
      >
        Confirm
      </button>
    </section>
  );
}

export default IndustrySelection; 