import React from 'react';
import { ShoppingBag } from 'lucide-react';

const CartDropdown = ({
  cart,
  cartDropdownRef,
  setShowCartDropdown,
  setShowCartPage,
  updateCartQuantity,
  getTotalItems,
  getTotalPrice
}) => (
  <div
    ref={cartDropdownRef}
    className="absolute top-full right-0 mt-2 w-80 bg-white rounded-lg shadow-xl border z-50"
    onMouseEnter={() => setShowCartDropdown(true)}
    onMouseLeave={() => setShowCartDropdown(false)}
  >
    <div className="p-4 border-b">
      <h3 className="font-semibold text-lg">Shopping Cart ({getTotalItems()})</h3>
    </div>

    {cart.length === 0 ? (
      <div className="p-6 text-center">
        <ShoppingBag className="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <p className="text-gray-500">Your cart is empty</p>
      </div>
    ) : (
      <>
        <div className="max-h-64 overflow-y-auto">
          {cart.map((item) => (
            <div key={item.id} className="p-4 border-b hover:bg-gray-50 transition-colors">
              <div className="flex items-center space-x-3">
                <img
                  src={item.image_url}
                  alt={item.name}
                  className="w-12 h-12 object-cover rounded"
                />
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-sm truncate">{item.name}</h4>
                  <p className="text-xs text-gray-500">{item.category}</p>
                  <div className="flex items-center justify-between mt-1">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => updateCartQuantity(item.id, item.quantity - 1)}
                        className="w-6 h-6 rounded border flex items-center justify-center hover:bg-gray-100"
                      >
                        -
                      </button>
                      <span className="text-sm font-medium">{item.quantity}</span>
                      <button
                        onClick={() => updateCartQuantity(item.id, item.quantity + 1)}
                        className="w-6 h-6 rounded border flex items-center justify-center hover:bg-gray-100"
                      >
                        +
                      </button>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-semibold">
                        ${((item.sale_price || item.price) * item.quantity).toFixed(2)}
                      </div>
                      {item.sale_price && (
                        <div className="text-xs text-gray-500 line-through">
                          ${(item.price * item.quantity).toFixed(2)}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="p-4 border-t bg-gray-50">
          <div className="flex justify-between items-center mb-3">
            <span className="font-semibold">Total:</span>
            <span className="font-bold text-lg">${getTotalPrice().toFixed(2)}</span>
          </div>
          <button
            onClick={() => {
              setShowCartPage(true);
              setShowCartDropdown(false);
            }}
            className="w-full bg-black text-white py-2 rounded-lg font-medium hover:bg-gray-800 transition-colors"
          >
            View Cart & Checkout
          </button>
        </div>
      </>
    )}
  </div>
);

export default CartDropdown;