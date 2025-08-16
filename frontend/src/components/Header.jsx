import React from 'react';
import { Search, ShoppingBag, User, Heart } from 'lucide-react';
import FlashSaleBanner from './FlashSaleBanner';
import CartDropdown from './CartDropdown';

const Header = ({ 
  searchTerm, 
  setSearchTerm, 
  cart, 
  showCartDropdown, 
  setShowCartDropdown,
  setShowCartPage,
  cartDropdownRef,
  updateCartQuantity,
  getTotalItems,
  getTotalPrice 
}) => {
  return (
    <header className="bg-white shadow-md sticky top-0 z-50">
      <FlashSaleBanner />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <button
              onClick={() => setShowCartPage(false)}
              className="text-2xl font-bold text-black cursor-pointer hover:text-gray-700 transition-colors"
            >
              SNKR<span className="text-red-500">STORE</span>
            </button>
          </div>

          <nav className="hidden md:flex space-x-8">
            <a href="#" className="text-gray-700 hover:text-black font-medium transition-colors">New & Featured</a>
            <a href="#" className="text-gray-700 hover:text-black font-medium transition-colors">Men</a>
            <a href="#" className="text-gray-700 hover:text-black font-medium transition-colors">Women</a>
            <a href="#" className="text-gray-700 hover:text-black font-medium transition-colors">Kids</a>
            <a href="#" className="text-gray-700 hover:text-black font-medium transition-colors">Sale</a>
          </nav>

          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-black"
              />
            </div>
            <Heart className="w-6 h-6 text-gray-700 hover:text-black cursor-pointer transition-colors" />

            {/* Cart Icon with Dropdown */}
            <div
              className="relative"
              onMouseEnter={() => setShowCartDropdown(true)}
              onMouseLeave={() => setShowCartDropdown(false)}
            >
              <div className="relative cursor-pointer">
                <ShoppingBag
                  className="w-6 h-6 text-gray-700 hover:text-black transition-colors"
                  onClick={() => setShowCartPage(true)}
                />
                {getTotalItems() > 0 && (
                  <span className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs font-semibold animate-bounce-in">
                    {getTotalItems()}
                  </span>
                )}
              </div>

              {/* Cart Dropdown */}
              {showCartDropdown && (
                <CartDropdown
                  cart={cart}
                  cartDropdownRef={cartDropdownRef}
                  setShowCartDropdown={setShowCartDropdown}
                  setShowCartPage={setShowCartPage}
                  updateCartQuantity={updateCartQuantity}
                  getTotalItems={getTotalItems}
                  getTotalPrice={getTotalPrice}
                />
              )}
            </div>

            <User className="w-6 h-6 text-gray-700 hover:text-black cursor-pointer transition-colors" />
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;