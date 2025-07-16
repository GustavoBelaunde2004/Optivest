import './index.css';
import { useState, useEffect } from 'react';
import image from "/assets/piechart5.jpg"

function App() {

  const [healthData, setHealthData] = useState('');

  const getHealthCheck = async () =>{
    const response = await fetch("http://localhost:5000/api/health");
    const data = await response.json();
    setHealthData(data.status);
    console.log(data.status);
  }

  useEffect(() => {
    getHealthCheck()
  }, []);


  return (
    <>
    {/* Main Container via section tag */}
     <section className = "min-h-screen flex items-center justify-center font-mono bg-gradient-to-r from-cyan-500 from-10% via-indigo-500 via-50% to-sky-500 to-100%">
      <div className = "flex flex-row shadow-2xl rounded-2xl overflow-hidden bg-white/80 backdrop-blur-md transition-all duration-300 hover:shadow-3xl hover:-translate-y-2 hover:scale-105" style={{height: '600px', minWidth: '900px'}}>
        {/* Login Container */}
        <div className = "flex flex-col items-center justify-center text-center gap-8 bg-white flex-1 rounded-2xl rounded-tr-none rounded-br-none"> 
           <h1 className = "text-4xl font-bold"> Welcome</h1>
           
           {/* Username Input */}
           <div className = "flex flex-col text-2xl text-left gap-1">
              <span>Username</span>
              <input type = "text" className = "rounded-md p-1 border-2 outline-none focus:border-cyan-400 focus: bg-slate-50"/>
           </div>

           {/* Password Input, same layout  */}
           <div className = "flex flex-col text-2xl text-left gap-1">
              <span>Password</span>
              <input type = "password" className = "rounded-md p-1 border-2 outline-none focus:border-cyan-400 focus: bg-slate-50"/>
           
              {/* Remember me checkbox inside same password div, might remove later if logic doesn't work with backend*/}
              <div className = "flex gap-1 items-center">
                <input type = "checkbox"/>
                <span className = "text-base">Remember me</span>
              </div>
           </div>

           <button className = "px-10 py-2 text-2xl rounded-md border-2 bg-gradient-to-tr from-green-400 to-blue-500 hover:from-pink-500 hover:to-yellow-500 text-white"> Login </button>
           <p> Don't have an account? <a href = "#" className = "text-blue-400 hover:underline">Register now</a></p>       
        </div>
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
