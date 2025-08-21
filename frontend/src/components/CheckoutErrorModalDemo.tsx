import { useState } from 'react';
import { AlertTriangle, X, ShoppingBag } from 'lucide-react';

// CheckoutErrorModal Component
const CheckoutErrorModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop with transparency */}
      <div
        className="absolute inset-0 bg-black bg-opacity-50"
        style={{ backdropFilter: 'blur(4px)' }}
        onClick={onClose}
      ></div>
      
      {/* Modal Content */}
      <div 
        className="bg-white rounded-lg shadow-2xl p-8 max-w-md w-full mx-4 relative z-10"
        style={{ 
          animation: 'bounceIn 0.5s ease-out',
          boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
        }}
      >
        <div className="absolute top-4 right-4">
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>
        
        <div className="text-center">
          <div 
            className="bg-red-100 p-4 rounded-full inline-flex items-center justify-center mb-6"
            style={{ 
              animation: 'errorPulse 2s infinite',
              boxShadow: '0 0 0 0 rgba(220, 38, 38, 0.4)'
            }}
          >
            <AlertTriangle className="w-10 h-10 text-red-600" />
          </div>
          
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Checkout Failure</h2>
          
          <p className="text-gray-700 text-lg mb-6">
            We're working on a fix. Please try again in 5 minutes. 🙏🏽🙏🏽🙏🏽
          </p>
          
          <button
            onClick={onClose}
            className="bg-black text-white py-3 px-6 rounded-lg font-medium hover:bg-gray-800 transition-colors"
          >
            Return to Cart
          </button>
        </div>
      </div>
    </div>
  );
};

// Demo Checkout Page
export default function CheckoutErrorDemo() {
  const [isErrorModalOpen, setIsErrorModalOpen] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  
  const handleCheckout = () => {
    setIsProcessing(true);
    
    // Simulate API call with a delay
    setTimeout(() => {
      setIsProcessing(false);
      setIsErrorModalOpen(true);
    }, 1500);
  };
  
  return (
    <div className="bg-gray-50 p-8 rounded-lg">
      <CheckoutErrorModal 
        isOpen={isErrorModalOpen} 
        onClose={() => setIsErrorModalOpen(false)} 
      />
      
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-6">Order Summary</h2>
        
        <div className="space-y-3 mb-6">
          <div className="flex justify-between">
            <span className="text-gray-600">Subtotal</span>
            <span className="font-medium">$249.95</span>
          </div>
          
          <div className="flex justify-between">
            <span className="text-gray-600">Shipping</span>
            <span className="text-green-600 font-medium">FREE</span>
          </div>
          
          <div className="flex justify-between">
            <span className="text-gray-600">Tax</span>
            <span className="font-medium">$20.00</span>
          </div>
          
          <div className="border-t pt-3">
            <div className="flex justify-between text-lg font-bold">
              <span>Total</span>
              <span>$269.95</span>
            </div>
          </div>
        </div>
        
        <button 
          onClick={handleCheckout}
          disabled={isProcessing}
          className={`w-full ${
            isProcessing 
              ? 'bg-gray-400 cursor-not-allowed' 
              : 'bg-black hover:bg-gray-800'
          } text-white py-4 rounded-lg font-medium transition-colors text-lg mb-4 relative`}
        >
          {isProcessing ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </span>
          ) : (
            'Proceed to Checkout'
          )}
        </button>
        
        <div className="text-center text-sm text-gray-500">
          <div className="flex items-center justify-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span>Secure Checkout</span>
          </div>
        </div>
      </div>
      
      <div className="mt-6 text-center">
        <p className="text-gray-500 text-sm">
          Click the "Proceed to Checkout" button to see the error modal.
        </p>
      </div>
      
      <style jsx>{`
        @keyframes bounceIn {
          0% {
            opacity: 0;
            transform: scale(0.8) translateY(1000px);
          }
          60% {
            opacity: 1;
            transform: scale(1.05) translateY(-10px);
          }
          80% {
            transform: scale(0.95) translateY(5px);
          }
          100% {
            transform: scale(1) translateY(0);
          }
        }
        
        @keyframes errorPulse {
          0%, 100% {
            box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.4);
          }
          50% {
            box-shadow: 0 0 0 10px rgba(220, 38, 38, 0);
          }
        }
      `}</style>
    </div>
  );
}