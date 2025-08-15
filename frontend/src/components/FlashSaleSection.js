import React from 'react';
import { Clock } from 'lucide-react';
import ProductCard from './ProductCard';

const FlashSaleSection = ({ flashSales, addToCart }) => {
  if (flashSales.length === 0) return null;

  return (
    <section className="py-12 bg-red-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-3xl font-bold text-gray-900">Flash Sale</h2>
          <div className="flex items-center text-red-600">
            <Clock className="w-5 h-5 mr-2" />
            <span className="font-bold">Ends Soon!</span>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {flashSales.slice(0, 4).map(sneaker => (
            <ProductCard 
              key={sneaker.id} 
              sneaker={sneaker} 
              isFlashSale={true}
              addToCart={addToCart}
            />
          ))}
        </div>
      </div>
    </section>
  );
};

export default FlashSaleSection;