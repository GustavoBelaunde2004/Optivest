import './index.css';
import { useState, useEffect } from 'react';
import image from "/assets/piechart5.jpg"
import ExperienceSelection from './ExperienceSelection';
import IndustrySelection from './IndustrySelection';

function App() {

  const [healthData, setHealthData] = useState(''); //keep this for backend health check
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const [showExperienceSelection, setShowExperienceSelection] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [showIndustrySelection, setShowIndustrySelection] = useState(false);

  // Used to check if backend is running
  const getHealthCheck = async () =>{
    const response = await fetch("http://localhost:5000/api/health");
    const data = await response.json();
    setHealthData(data.status);
    console.log(data.status);
  }

  useEffect(() => {
    getHealthCheck()
  }, []);

  //Login function
  const handleLogin = async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await fetch("http://localhost:5000/auth/login", {
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
      const response = await fetch("http://localhost:5000/auth/register", {
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
        setShowExperienceSelection(true); // Show experience selection
        setShowIndustrySelection(false); // Reset industry selection
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
      // handle experienced path if needed
    }
  };

  // If showing industry selection, render that
  if (showIndustrySelection) {
    return (
      <IndustrySelection onConfirm={(industries) => {
        // setSelectedIndustries(industries); // Not needed for now
        // TODO: proceed to next step with selected industries
        // For now, just log them and stay on this screen
        console.log('Selected industries:', industries);
      }} />
    );
  }

  // If showing experience selection, render that instead of login/register
  if (showExperienceSelection) {
    return (
      <ExperienceSelection onExperienceSelect={handleExperienceSelection} />
    );
  }

  return (
    <>
    {/* Main Container via section tag */}
     <section className = "min-h-screen flex items-center justify-center font-mono bg-gradient-to-r from-cyan-500 from-10% via-indigo-500 via-50% to-sky-500 to-100%">
      <div className = "flex flex-row shadow-2xl rounded-2xl overflow-hidden bg-white/80 backdrop-blur-md transition-all duration-300 hover:shadow-3xl hover:-translate-y-2 hover:scale-105" style={{height: '600px', minWidth: '900px'}}>
        {/* Login Container */}
        <div className = "flex flex-col items-center justify-center text-center gap-8 bg-white flex-1 rounded-2xl rounded-tr-none rounded-br-none"> 
           <h1 className = "text-4xl font-bold"> {showRegister ? 'Register' : 'Welcome'}</h1>
           
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
