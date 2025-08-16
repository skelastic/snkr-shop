import React from 'react';
import { Clock } from 'lucide-react';

const FlashSaleBanner = () => (
  <div className="bg-gradient-to-r from-red-500 to-pink-600 text-white py-3 px-4 text-center">
    <div className="flex items-center justify-center space-x-2">
      <Clock className="w-5 h-5 animate-pulse" />
      <span className="font-bold text-lg">FLASH SALE</span>
      <span className="hidden sm:inline">- Up to 40% off selected sneakers!</span>
      <span className="font-bold">Limited Time Only</span>
    </div>
  </div>
);

export default FlashSaleBanner;