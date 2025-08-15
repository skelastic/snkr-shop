import React from 'react';
import { Heart, Star } from 'lucide-react';

const ProductCard = ({ sneaker, isFlashSale = false, addToCart }) => (
  <div className={`bg-white rounded-lg shadow-md overflow-hidden hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 ${isFlashSale ? 'ring-2 ring-red-500' : ''}`}>
    {isFlashSale && (
      <div className="bg-red-500 text-white text-center py-1 text-sm font-bold animate-pulse">
        FLASH SALE
      </div>
    )}
    <div className="relative">
      <img
        src={sneaker.image_url}
        alt={sneaker.name}
        className="w-full h-64 object-cover transition-transform duration-300 hover:scale-105"
      />
      <Heart className="absolute top-4 right-4 w-6 h-6 text-white hover:text-red-500 cursor-pointer transition-colors duration-200" />
    </div>
    <div className="p-6">
      <h3 className="font-bold text-lg mb-2 truncate">{sneaker.name}</h3>
      <p className="text-gray-600 mb-2">{sneaker.category}</p>
      <div className="flex items-center mb-2">
        <Star className="w-4 h-4 text-yellow-400 fill-current" />
        <span className="ml-1 text-sm text-gray-600">{sneaker.rating} ({sneaker.reviews_count})</span>
      </div>
      <div className="flex items-center justify-between">
        <div>
          {sneaker.sale_price ? (
            <>
              <span className="text-lg font-bold text-red-600">${sneaker.sale_price}</span>
              <span className="ml-2 text-sm text-gray-500 line-through">${sneaker.price}</span>
            </>
          ) : (
            <span className="text-lg font-bold text-gray-900">${sneaker.price}</span>
          )}
        </div>
        <button
          onClick={() => addToCart(sneaker)}
          className="bg-black text-white px-4 py-2 rounded-full hover:bg-gray-800 hover:scale-105 transition-all duration-200"
        >
          Add to Cart
        </button>
      </div>
    </div>
  </div>
);

export default ProductCard;