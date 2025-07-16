import React from 'react';

function ExperienceSelection({ onExperienceSelect }) {
  return (
    <section className="min-h-screen flex items-center justify-center font-mono bg-gradient-to-r from-cyan-500 from-10% via-indigo-500 via-50% to-sky-500 to-100%">
      <div className="flex flex-col items-center justify-center text-center gap-12">
        {/* Title */}
        <div className="text-center">
          <h1 className="text-6xl font-bold text-white mb-4 drop-shadow-lg">
            What is your portfolio experience?
          </h1>
          <p className="text-xl text-white/80 font-light">
            Choose your path to portfolio optimization
          </p>
        </div>
        
        {/* Buttons Container */}
        <div className="flex flex-row gap-12 justify-center items-center">
          {/* Beginner Button */}
          <button 
            onClick={() => onExperienceSelect('beginner')}
            className="group relative px-16 py-8 text-3xl rounded-2xl border-2 border-white/20 bg-white/10 backdrop-blur-md text-white transition-all duration-500 transform hover:scale-110 hover:bg-white/20 hover:shadow-2xl hover:shadow-white/20"
          >
            <div className="absolute inset-0 rounded-2xl bg-gradient-to-tr from-green-400/20 to-blue-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <span className="relative z-10 flex items-center gap-3">
              <span className="text-4xl"></span>
              <span>I'm a Beginner</span>
            </span>
          </button>
          
          {/* Experienced Button */}
          <button 
            onClick={() => onExperienceSelect('experienced')}
            className="group relative px-16 py-8 text-3xl rounded-2xl border-2 border-white/20 bg-white/10 backdrop-blur-md text-white transition-all duration-500 transform hover:scale-110 hover:bg-white/20 hover:shadow-2xl hover:shadow-white/20"
          >
            <div className="absolute inset-0 rounded-2xl bg-gradient-to-tr from-purple-400/20 to-indigo-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <span className="relative z-10 flex items-center gap-3">
              <span className="text-4xl"></span>
              <span>I Already Have a Portfolio</span>
            </span>
          </button>
        </div>
        
        {/* Decorative elements */}
        <div className="absolute top-20 left-20 w-32 h-32 bg-white/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 right-20 w-40 h-40 bg-blue-400/20 rounded-full blur-3xl"></div>
        <div className="absolute top-1/2 left-10 w-24 h-24 bg-cyan-400/20 rounded-full blur-2xl"></div>
      </div>
    </section>
  );
}

export default ExperienceSelection; 