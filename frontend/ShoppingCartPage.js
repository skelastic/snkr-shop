// This should be saved as src/ShoppingCartPage.js
import React, { useState } from 'react';
import { Minus, Plus, Trash2, ShoppingBag, ArrowLeft, Heart, Tag } from 'lucide-react';

const ShoppingCartPage = ({ cart, setCart, onBackToStore }) => {
  const [promoCode, setPromoCode] = useState('');
  const [appliedPromo, setAppliedPromo] = useState(null);

  // Calculate totals
  const subtotal = cart.reduce((sum, item) => {
    const price = item.sale_price || item.price;
    return sum + (price * item.quantity);
  }, 0);

  const shipping = subtotal > 100 ? 0 : 9.99;
  const tax = subtotal * 0.08; // 8% tax
  const discount = appliedPromo ? subtotal * 0.1 : 0; // 10% discount
  const total = subtotal + shipping + tax - discount;

  const updateQuantity = (id, newQuantity) => {
    if (newQuantity === 0) {
      removeItem(id);
      return;
    }
    
    setCart(prevCart =>
      prevCart.map(item =>
        item.id === id ? { ...item, quantity: newQuantity } : item
      )
    );
  };

  const removeItem = (id) => {
    setCart(prevCart => prevCart.filter(item => item.id !== id));
  };

  const applyPromoCode = () => {
    const validCodes = ['FLASH10', 'SAVE10', 'FIRST10'];
    if (validCodes.includes(promoCode.toUpperCase())) {
      setAppliedPromo(promoCode.toUpperCase());
      setPromoCode('');
    } else {
      alert('Invalid promo code');
    }
  };

  const removePromoCode = () => {
    setAppliedPromo(null);
  };

  if (cart.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <div className="bg-white rounded-lg shadow-lg p-12">
            <ShoppingBag className="w-24 h-24 text-gray-300 mx-auto mb-6" />
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Your cart is empty</h2>
            <p className="text-gray-600 mb-8 text-lg">
              Looks like you haven't added any sneakers to your cart yet.
            </p>
            <button
              onClick={onBackToStore}
              className="bg-black text-white px-8 py-4 rounded-full font-medium hover:bg-gray-800 transition-colors text-lg"
            >
              Continue Shopping
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center">
            <button
              onClick={onBackToStore}
              className="flex items-center text-gray-600 hover:text-black transition-colors mr-4"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Continue Shopping
            </button>
            <h1 className="text-3xl font-bold text-gray-900">Shopping Cart</h1>
          </div>
          <div className="text-gray-600">
            {cart.reduce((sum, item) => sum + item.quantity, 0)} items
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Cart Items */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-xl font-semibold">Cart Items</h2>
              </div>
              
              <div className="divide-y divide-gray-200">
                {cart.map((item) => (
                  <div key={item.id} className="p-6 hover:bg-gray-50 transition-colors">
                    <div className="flex items-start space-x-4">
                      {/* Product Image */}
                      <div className="relative">
                        <img
                          src={item.image_url}
                          alt={item.name}
                          className="w-24 h-24 object-cover rounded-lg"
                        />
                        {item.is_flash_sale && (
                          <div className="absolute -top-2 -right-2 bg-red-500 text-white text-xs px-2 py-1 rounded-full">
                            SALE
                          </div>
                        )}
                      </div>

                      {/* Product Details */}
                      <div className="flex-1 min-w-0">
                        <div className="flex justify-between items-start">
                          <div>
                            <h3 className="text-lg font-medium text-gray-900 truncate">
                              {item.name}
                            </h3>
                            <p className="text-sm text-gray-500 mt-1">{item.category}</p>
                            {item.sizes && item.sizes.length > 0 && (
                              <p className="text-sm text-gray-500">Size: {item.sizes[0]}</p>
                            )}
                            {item.colors && item.colors.length > 0 && (
                              <p className="text-sm text-gray-500">Color: {item.colors[0]}</p>
                            )}
                          </div>
                          
                          <button
                            onClick={() => removeItem(item.id)}
                            className="text-gray-400 hover:text-red-500 transition-colors"
                          >
                            <Trash2 className="w-5 h-5" />
                          </button>
                        </div>

                        {/* Price and Quantity Controls */}
                        <div className="flex items-center justify-between mt-4">
                          <div className="flex items-center space-x-3">
                            <button
                              onClick={() => updateQuantity(item.id, item.quantity - 1)}
                              className="w-8 h-8 rounded-full border border-gray-300 flex items-center justify-center hover:bg-gray-100 transition-colors"
                            >
                              <Minus className="w-4 h-4" />
                            </button>
                            <span className="font-medium text-lg w-8 text-center">{item.quantity}</span>
                            <button
                              onClick={() => updateQuantity(item.id, item.quantity + 1)}
                              className="w-8 h-8 rounded-full border border-gray-300 flex items-center justify-center hover:bg-gray-100 transition-colors"
                            >
                              <Plus className="w-4 h-4" />
                            </button>
                          </div>

                          <div className="text-right">
                            {item.sale_price ? (
                              <>
                                <div className="text-lg font-bold text-red-600">
                                  ${(item.sale_price * item.quantity).toFixed(2)}
                                </div>
                                <div className="text-sm text-gray-500 line-through">
                                  ${(item.price * item.quantity).toFixed(2)}
                                </div>
                              </>
                            ) : (
                              <div className="text-lg font-bold text-gray-900">
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
            </div>
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6 sticky top-8">
              <h2 className="text-xl font-semibold mb-6">Order Summary</h2>

              {/* Promo Code */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Promo Code
                </label>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={promoCode}
                    onChange={(e) => setPromoCode(e.target.value)}
                    placeholder="Enter code"
                    className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-black"
                  />
                  <button
                    onClick={applyPromoCode}
                    className="bg-gray-900 text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors"
                  >
                    Apply
                  </button>
                </div>
                
                {appliedPromo && (
                  <div className="mt-2 flex items-center justify-between bg-green-50 border border-green-200 rounded-lg p-3">
                    <div className="flex items-center">
                      <Tag className="w-4 h-4 text-green-600 mr-2" />
                      <span className="text-sm font-medium text-green-800">{appliedPromo}</span>
                    </div>
                    <button
                      onClick={removePromoCode}
                      className="text-green-600 hover:text-green-800"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                )}
              </div>

              {/* Price Breakdown */}
              <div className="space-y-3 mb-6">
                <div className="flex justify-between">
                  <span className="text-gray-600">Subtotal</span>
                  <span className="font-medium">${subtotal.toFixed(2)}</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-600">Shipping</span>
                  <span className="font-medium">
                    {shipping === 0 ? (
                      <span className="text-green-600">FREE</span>
                    ) : (
                      `$${shipping.toFixed(2)}`
                    )}
                  </span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-600">Tax</span>
                  <span className="font-medium">${tax.toFixed(2)}</span>
                </div>
                
                {discount > 0 && (
                  <div className="flex justify-between text-green-600">
                    <span>Discount</span>
                    <span className="font-medium">-${discount.toFixed(2)}</span>
                  </div>
                )}
                
                <div className="border-t pt-3">
                  <div className="flex justify-between text-lg font-bold">
                    <span>Total</span>
                    <span>${total.toFixed(2)}</span>
                  </div>
                </div>
              </div>

              {/* Free Shipping Banner */}
              {subtotal < 100 && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-6">
                  <p className="text-sm text-blue-800">
                    Add <span className="font-semibold">${(100 - subtotal).toFixed(2)}</span> more for FREE shipping!
                  </p>
                </div>
              )}

              {/* Checkout Button */}
              <button className="w-full bg-black text-white py-4 rounded-lg font-medium hover:bg-gray-800 transition-colors text-lg mb-4">
                Proceed to Checkout
              </button>

              {/* Security Badge */}
              <div className="text-center text-sm text-gray-500">
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span>Secure Checkout</span>
                </div>
                <p className="mt-1">Your payment information is protected</p>
              </div>
            </div>
          </div>
        </div>

        {/* Recently Viewed or Recommendations */}
        <div className="mt-12">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">You might also like</h3>
          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-gray-500 text-center py-8">
              Recommended products will appear here based on your cart items
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ShoppingCartPage;