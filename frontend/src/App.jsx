import './index.css';
import { useState, useEffect, useRef } from 'react';
import image from "/assets/piechart5.jpg"
import ExperienceSelection from './ExperienceSelection';
import IndustrySelection from './IndustrySelection';
import StockSelection from './StockSelection';
import PortfolioPieChart from './PortfolioPieChart';
import { API_BASE_URL } from './config';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function App() {

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const [showExperienceSelection, setShowExperienceSelection] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [showIndustrySelection, setShowIndustrySelection] = useState(false);
  const [showStockSelection, setShowStockSelection] = useState(false);
  const [selectedIndustries, setSelectedIndustries] = useState([]);
  const [showPieChart, setShowPieChart] = useState(false);
  const [finalStocks, setFinalStocks] = useState([]);
  const [showPortfolios, setShowPortfolios] = useState(false);
  const [portfolios, setPortfolios] = useState([]);
  const [selectedPortfolio, setSelectedPortfolio] = useState(null);
  const [portfolioError, setPortfolioError] = useState('');
  const modalRef = useRef();

  const PIE_COLORS = [
    '#2563eb', '#60a5fa', '#0ea5e9', '#38bdf8', '#818cf8', '#6366f1', '#1e40af', '#9333ea', '#06b6d4', '#f472b6'
  ];
  const renderModalPieLabel = ({ name, weight, cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * (percent > 0.08 ? 0.6 : 1.1);
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);
    const displayName = name.length > 18 ? name.slice(0, 16) + '…' : name;
    return (
      <text
        x={x}
        y={y}
        fill={percent > 0.08 ? '#222' : '#2563eb'}
        textAnchor={x > cx ? 'start' : 'end'}
        dominantBaseline="central"
        fontSize={percent > 0.08 ? 15 : 11}
        fontWeight={percent > 0.08 ? 700 : 500}
        stroke={percent > 0.08 ? 'white' : 'none'}
        strokeWidth={percent > 0.08 ? 0.5 : 0}
      >
        {percent > 0.08 ? `${displayName}: ${(weight * 100).toFixed(1)}%` : `${(weight * 100).toFixed(1)}%`}
      </text>
    );
  };

  // Used to check if backend is running
  const getHealthCheck = async () =>{
    const response = await fetch(`${API_BASE_URL}/api/health`);
    const data = await response.json();
    console.log(data.status);
  }

  useEffect(() => {
    getHealthCheck()
  }, []);

  // Check if user is still logged in on app load
  useEffect(() => {
    const checkSession = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/session/check`, { credentials: 'include' });
        if (res.status === 200) {
          // User is logged in
          setIsLoggedIn(true);
        }
      } catch (err) {
        console.log('Session check failed:', err);
      }
    };
    
    checkSession();
  }, []);

  //Login function
  const handleLogin = async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password, remember: rememberMe }),
        credentials: 'include' 
      });

      if (response.ok) {
        const data = await response.json();
        setIsLoggedIn(true);
        console.log("Login successful", data); //logic success
        setError(''); // Clear any previous errors
        
      } else {
        const errorData = await response.json();
        setError(errorData.error || "Login failed. Invalid credentials."); //incorrect username/password
      }
    } catch (err) {
      setError("Login failed."); //straight up failed
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  //Register function
  const handleRegister = async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        console.log("Registration successful!", data);
        setError(''); // clear prev errors
        setShowExperienceSelection(true); 
        setShowIndustrySelection(false);
        setUsername('');
        setPassword('');
      } else {
        const errorData = await response.json();
        setError(errorData.error || "Registration failed.");
      }
    } catch (err) {
      setError("Registration failed. Network or server error.");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExperienceSelection = (experience) => {
    if (experience === 'beginner') {
      setShowIndustrySelection(true);
    } else {
      // handle experienced path if needed later
    }
  };

  const fetchPortfolios = async () => {
    setPortfolioError('');
    console.log('🔍 Starting fetchPortfolios...');
    try {
      // First check if user is still logged in
      console.log('🔍 Checking session...');
      const sessionRes = await fetch(`${API_BASE_URL}/api/session/check`, { credentials: 'include' });
      console.log('🔍 Session check status:', sessionRes.status);
      const sessionData = await sessionRes.json();
      console.log('🔍 Session data:', sessionData);
      
      if (sessionRes.status !== 200) {
        // User not logged in, redirect to login
        console.log('❌ Session check failed, redirecting to login');
        setIsLoggedIn(false);
        setShowPortfolios(false);
        setError('Session expired. Please login again.');
        return;
      }
      
      console.log('✅ Session valid, fetching portfolios...');
      const res = await fetch(`${API_BASE_URL}/api/portfolio/list`, { credentials: 'include' });
      console.log('🔍 Portfolio list status:', res.status);
      const data = await res.json();
      console.log('🔍 Portfolio data:', data);
      
      if (res.status === 401) {
        // User not logged in, redirect to login
        console.log('❌ Portfolio list returned 401, redirecting to login');
        setIsLoggedIn(false);
        setShowPortfolios(false);
        setError('Session expired. Please login again.');
        return;
      }
      if (data.portfolios) {
        console.log('✅ Portfolios fetched successfully:', data.portfolios.length);
        setPortfolios(data.portfolios);
      } else {
        console.log('❌ No portfolios in response:', data);
        setPortfolioError(data.error || 'Failed to fetch portfolios.');
      }
    } catch (err) {
      console.error('❌ Error fetching portfolios:', err);
      setPortfolioError('Failed to fetch portfolios.');
    }
  };

  const handleLogout = async () => {
    try {
      await fetch(`${API_BASE_URL}/auth/logout`, {
        method: 'POST',
        credentials: 'include'
      });
      // Reset all state to return to login
      setIsLoggedIn(false);
      setShowExperienceSelection(false);
      setShowIndustrySelection(false);
      setShowStockSelection(false);
      setShowPieChart(false);
      setShowPortfolios(false);
      setSelectedIndustries([]);
      setFinalStocks([]);
      setPortfolios([]);
      setSelectedPortfolio(null);
      setUsername('');
      setPassword('');
    } catch (err) {
      console.error('Logout failed:', err);
    }
  };

  // If showing pie chart, render that
  if (showPieChart) {
    return (
      <PortfolioPieChart
        selectedStocks={finalStocks}
        onBack={() => {
          setShowPieChart(false);
          setShowExperienceSelection(false);
          setShowIndustrySelection(false);
          setShowStockSelection(false);
          setSelectedIndustries([]);
          setFinalStocks([]);
          // Do not log out the user
        }}
        onLogout={handleLogout}
        onNewPortfolio={() => {
          setShowPieChart(false);
          setShowExperienceSelection(false);
          setShowIndustrySelection(true);
          setSelectedIndustries([]);
          setFinalStocks([]);
        }}
        onViewPortfolios={async () => {
          setShowPieChart(false);
          setShowExperienceSelection(false);
          setShowIndustrySelection(false);
          setShowStockSelection(false);
          setSelectedIndustries([]);
          setFinalStocks([]);
          setShowPortfolios(true);
          // Keep user logged in and fetch portfolios
          await fetchPortfolios();
        }}
      />
    );
  }

  // If showing stock selection, render that
  if (showStockSelection) {
    return (
      <StockSelection
        industries={selectedIndustries}
        onConfirm={(stocks) => {
          setFinalStocks(stocks);
          setShowStockSelection(false);
          setShowPieChart(true);
        }}
      />
    );
  }

  // If showing industry selection, render that
  if (showIndustrySelection) {
    return (
      <IndustrySelection onConfirm={(industries) => {
        setSelectedIndustries(industries);
        setShowIndustrySelection(false);
        setShowStockSelection(true);
      }} />
    );
  }

  // If showing experience selection, render that instead of login/register
  if (showExperienceSelection) {
    return (
      <ExperienceSelection onExperienceSelect={handleExperienceSelection} />
    );
  }

  // Show portfolios list
  if (showPortfolios) {
    return (
      <section className="min-h-screen flex flex-col items-center justify-center font-mono bg-gradient-to-r from-cyan-500 via-indigo-500 to-sky-500">
        <h1 className="text-4xl font-bold text-white mb-8 drop-shadow-lg">Your Portfolios</h1>
        <div className="flex gap-4 mb-8">
          <button
            className="px-8 py-4 rounded-lg bg-white text-blue-700 font-bold text-2xl shadow-lg hover:bg-blue-100 transition"
            onClick={() => {
              setShowPortfolios(false);
              setShowExperienceSelection(false);
              setShowIndustrySelection(true);
              setSelectedIndustries([]);
              setFinalStocks([]);
            }}
          >
            New Portfolio
          </button>
          <button
            className="px-8 py-4 rounded-lg bg-red-500 text-white font-bold text-2xl shadow-lg hover:bg-red-600 transition"
            onClick={handleLogout}
          >
            Logout
          </button>
        </div>
        <div className="w-full max-w-5xl flex flex-row gap-6 overflow-x-auto pb-4">
          {portfolios.length === 0 && !portfolioError && (
            <div className="text-white text-xl">No portfolios found.</div>
          )}
          {portfolioError && <div className="text-red-500 bg-white p-2 rounded">{portfolioError}</div>}
          {portfolios.map((p) => (
            <div
              key={p.id}
              className="min-w-[260px] max-w-xs bg-white rounded-xl shadow-lg p-6 flex flex-col items-center cursor-pointer hover:scale-105 transition border-2 border-blue-200"
              onClick={() => setSelectedPortfolio(p)}
            >
              <div className="font-bold text-blue-700 text-lg mb-2 truncate w-full text-center">{p.name}</div>
              <div className="text-gray-500 text-sm mb-2">{new Date(p.created_at).toLocaleString('en-US', { timeZone: 'America/New_York' })}</div>
              <div className="text-blue-900 font-semibold">{p.stocks.length} stocks</div>
              <div className="text-green-600 font-bold mt-2">Projected Return: {p.projected_return ? (p.projected_return * 100).toFixed(2) + '%' : 'N/A'}</div>
            </div>
          ))}
        </div>
        {/* Modal for portfolio details */}
        {selectedPortfolio && (
          <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50" onClick={e => { if (e.target === modalRef.current) setSelectedPortfolio(null); }} ref={modalRef}>
            <div className="bg-white rounded-2xl shadow-2xl p-8 min-w-[340px] max-w-lg w-full relative">
              <button className="absolute top-2 right-2 text-2xl text-gray-400 hover:text-blue-600" onClick={() => setSelectedPortfolio(null)}>&times;</button>
              <h2 className="text-2xl font-bold text-blue-700 mb-4 text-center">{selectedPortfolio.name}</h2>
              <div className="text-gray-500 text-center mb-2">{new Date(selectedPortfolio.created_at).toLocaleString('en-US', { timeZone: 'America/New_York' })}</div>
              <div className="mb-4 text-center text-green-600 font-bold">Projected Return: {selectedPortfolio.projected_return ? (selectedPortfolio.projected_return * 100).toFixed(2) + '%' : 'N/A'}</div>
              <div className="flex flex-col items-center mb-4">
                <ResponsiveContainer width={320} height={320}>
                  <PieChart>
                    <Pie
                      data={selectedPortfolio.stocks}
                      dataKey="weight"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={120}
                      label={renderModalPieLabel}
                      labelLine={true}
                      minAngle={3}
                      paddingAngle={2}
                    >
                      {selectedPortfolio.stocks.map((entry, idx) => (
                        <Cell key={`cell-${idx}`} fill={PIE_COLORS[idx % PIE_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `${(value * 100).toFixed(2)}%`} contentStyle={{ fontSize: 14 }} />
                    <Legend layout="horizontal" verticalAlign="bottom" align="center" wrapperStyle={{ fontSize: 13, maxWidth: 320, whiteSpace: 'normal', textAlign: 'center' }} iconSize={14} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-blue-100">
                      <th className="p-2">Stock</th>
                      <th className="p-2">Industry</th>
                      <th className="p-2">Weight</th>
                      <th className="p-2">Quality</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedPortfolio.stocks.map((s, idx) => (
                      <tr key={s.symbol} className={idx % 2 === 0 ? 'bg-white' : 'bg-blue-50'}>
                        <td className="p-2 font-semibold text-blue-900">{s.name}</td>
                        <td className="p-2 text-gray-700">{s.industry}</td>
                        <td className="p-2 text-blue-700">{(s.weight * 100).toFixed(2)}%</td>
                        <td className="p-2 text-green-700">{s.quality_score ? s.quality_score.toFixed(1) : 'N/A'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </section>
    );
  }

  // After login, show View Portfolios button
  if (isLoggedIn && !showExperienceSelection && !showIndustrySelection && !showStockSelection && !showPieChart && !showPortfolios) {
    return (
      <section className="min-h-screen flex flex-col items-center justify-center font-mono bg-gradient-to-r from-cyan-500 via-indigo-500 to-sky-500">
        <h1 className="text-4xl font-bold text-white mb-8 drop-shadow-lg">Welcome to Optivest!</h1>
        <div className="flex gap-4 mb-8">
          <button
            className="px-8 py-4 rounded-lg bg-white text-blue-700 font-bold text-2xl shadow-lg hover:bg-blue-100 transition"
            onClick={async () => { setShowPortfolios(true); await fetchPortfolios(); }}
          >
            View Portfolios
          </button>
          <button
            className="px-8 py-4 rounded-lg bg-red-500 text-white font-bold text-2xl shadow-lg hover:bg-red-600 transition"
            onClick={handleLogout}
          >
            Logout
          </button>
        </div>
      </section>
    );
  }

  return (
    <>
    {/* Main Container via section tag */}
     <section className = "min-h-screen flex items-center justify-center font-mono bg-gradient-to-r from-cyan-500 from-10% via-indigo-500 via-50% to-sky-500 to-100%">
      <div className = "flex flex-row shadow-2xl rounded-2xl overflow-hidden bg-white/80 backdrop-blur-md transition-all duration-300 hover:shadow-3xl hover:-translate-y-2 hover:scale-105" style={{height: '600px', minWidth: '900px'}}>
        {/* Login Container */}
        <div className = "flex flex-col items-center justify-center text-center gap-8 bg-white flex-1 rounded-2xl rounded-tr-none rounded-br-none"> 
           <h1 className = "text-4xl font-bold"> {showRegister ? 'Register' : 'Welcome to Optivest'}</h1>
           
           {/* Username Input */}
           <div className = "flex flex-col text-2xl text-left gap-1">
              <span>Username</span>
              <input 
                type = "text" 
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className = "rounded-md p-1 border-2 outline-none focus:border-cyan-400 focus: bg-slate-50"
              />
           </div>

           {/* Password Input, same layout  */}
           <div className = "flex flex-col text-2xl text-left gap-1">
              <span>Password</span>
              <input 
                type = "password" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className = "rounded-md p-1 border-2 outline-none focus:border-cyan-400 focus: bg-slate-50"
              />
           
              {/* Remember me checkbox inside same password div, might remove later if logic doesn't work with backend*/}
              {!showRegister && (
                <div className = "flex gap-1 items-center">
                  <input type = "checkbox" checked={rememberMe} onChange={e => setRememberMe(e.target.checked)} />
                  <span className = "text-base">Remember me</span>
                </div>
              )}
           </div>

           {/* Error Display */}
           {error && (
             <div className="text-red-500 text-sm bg-red-100 p-2 rounded">
               {error}
             </div>
           )}

           <button 
             onClick={showRegister ? handleRegister : handleLogin}
             disabled={isLoading}
             className = "px-10 py-2 text-2xl rounded-md border-2 bg-gradient-to-tr from-green-400 to-blue-500 hover:from-cyan-400 hover:to-indigo-500 text-white disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105"
           > 
             {isLoading ? (showRegister ? 'Registering...' : 'Logging in...') : (showRegister ? 'Register' : 'Login')} 
           </button>
           <p> 
             {showRegister ? 'Already have an account?' : "Don't have an account?"} 
             <button 
               onClick={() => {
                 setShowRegister(!showRegister);
                 setError('');
                 setUsername('');
                 setPassword('');
               }}
               className = "text-blue-400 hover:underline ml-1"
             >
               {showRegister ? 'Login now' : 'Register now'}
             </button>
           </p>       
        </div>
        {/* Piechart Container */}
        <div className="flex-1 h-full">
          <img
            src={image}
            alt="PieChart"
            className="w-full h-full object-cover rounded-tr-2xl rounded-br-2xl"
            style={{display: 'block'}}
          />
        </div>
      </div>
    </section>
    </>
  )
}

export default App
