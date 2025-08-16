import React from 'react';
import { Heart, Star } from 'lucide-react';

const ProductCard = ({ sneaker, isFlashSale = false, addToCart, onProductClick }) => (
  <div className={`bg-white rounded-lg shadow-md overflow-hidden hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 ${isFlashSale ? 'ring-2 ring-red-500' : ''}`}>
    {isFlashSale && (
      <div className="bg-red-500 text-white text-center py-1 text-sm font-bold animate-pulse">
        FLASH SALE
      </div>
    )}
    <div
      className="relative cursor-pointer"
      onClick={() => onProductClick && onProductClick(sneaker.product_id)}
    >
      <img
        src={sneaker.image_url}
        alt={sneaker.name}
        className="w-full h-64 object-cover transition-transform duration-300 hover:scale-105"
      />
      <Heart className="absolute top-4 right-4 w-6 h-6 text-white hover:text-red-500 cursor-pointer transition-colors duration-200" />
    </div>
    <div className="p-6">
      <h3
        className="font-bold text-lg mb-2 truncate cursor-pointer hover:text-gray-700 transition-colors"
        onClick={() => onProductClick && onProductClick(sneaker.product_id)}
      >
        {sneaker.name}
      </h3>
      <p className="text-gray-600 mb-2">{sneaker.category}</p>
      <div className="flex items-center mb-2">
        <Star className="w-4 h-4 text-yellow-400 fill-current" />
        <span className="ml-1 text-sm text-gray-600">{sneaker.rating} ({sneaker.reviews_count})</span>
      </div>

      {/* Available sizes and colors preview */}
      <div className="mb-3 space-y-1">
        <div className="text-xs text-gray-500">
          Sizes: {sneaker.sizes.length > 3
            ? `${sneaker.sizes.slice(0, 3).join(', ')} +${sneaker.sizes.length - 3} more`
            : sneaker.sizes.join(', ')
          }
        </div>
        <div className="text-xs text-gray-500">
          Colors: {sneaker.colors.length > 2
            ? `${sneaker.colors.slice(0, 2).join(', ')} +${sneaker.colors.length - 2} more`
            : sneaker.colors.join(', ')
          }
        </div>
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
          {/* Show price range if multiple variants */}
          {sneaker.sizes.length > 1 && (
            <div className="text-xs text-gray-500">Starting from</div>
          )}
        </div>
        <div className="flex space-x-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onProductClick && onProductClick(sneaker.product_id);
            }}
            className="bg-gray-100 text-gray-700 px-3 py-2 rounded-lg hover:bg-gray-200 transition-colors text-sm"
          >
            View Details
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              addToCart(sneaker);
            }}
            className="bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-800 hover:scale-105 transition-all duration-200 text-sm"
          >
            Quick Add
          </button>
        </div>
      </div>
    </div>
  </div>
);

export default ProductCard;