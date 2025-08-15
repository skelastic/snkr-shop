import React from 'react';

const HeroSection = () => (
  <section className="bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white py-20">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="text-center">
        <h1 className="text-5xl md:text-7xl font-bold mb-6">
          JUST DO IT
        </h1>
        <p className="text-xl md:text-2xl mb-8 text-gray-300">
          Discover the latest drops and exclusive sneakers
        </p>
        <button className="bg-white text-black px-8 py-4 rounded-full font-bold text-lg hover:bg-gray-200 transition-colors">
          Shop Now
        </button>
      </div>
    </div>
  </section>
);

export default HeroSection;