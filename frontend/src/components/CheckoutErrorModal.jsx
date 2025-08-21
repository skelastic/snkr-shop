import React, { useEffect, useState } from 'react';
import { AlertTriangle, X, Server } from 'lucide-react';

const CheckoutErrorModal = ({ isOpen, onClose }) => {
  const [requestCount, setRequestCount] = useState(0);

  // Close modal when ESC key is pressed
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEsc);
    }

    return () => {
      document.removeEventListener('keydown', handleEsc);
    };
  }, [isOpen, onClose]);

  // Prevent scrolling when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'auto';
    }

    return () => {
      document.body.style.overflow = 'auto';
    };
  }, [isOpen]);

  // Simulate a counter for the request spike
  useEffect(() => {
    if (isOpen) {
      let count = 0;
      const interval = setInterval(() => {
        count += Math.floor(Math.random() * 500) + 200;
        if (count > 10000) {
          count = 10000;
          clearInterval(interval);
        }
        setRequestCount(count);
      }, 100);

      return () => clearInterval(interval);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop with transparency */}
      <div
        className="absolute inset-0 bg-black bg-opacity-50 backdrop-blur-sm"
        onClick={onClose}
      ></div>

      {/* Modal Content */}
      <div className="bg-white rounded-lg shadow-2xl p-8 max-w-md w-full mx-4 relative z-10 animate-bounce-in">
        <div className="absolute top-4 right-4">
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="text-center">
          <div className="bg-red-100 p-4 rounded-full inline-flex items-center justify-center mb-6">
            <AlertTriangle className="w-10 h-10 text-red-600" />
          </div>

          <h2 className="text-2xl font-bold text-gray-900 mb-4">Checkout Failure</h2>

          <p className="text-gray-700 text-lg mb-6">
            Our engineering team is deploying a fix. Please try again in 5 minutes.
          </p>

          {/* Request spike indicator
          <div className="bg-gray-100 rounded-lg p-4 mb-6">
            <div className="flex items-center justify-center space-x-2 mb-2">
              <Server className="w-5 h-5 text-gray-600" />
              <span className="font-medium text-gray-700">Load Test in Progress</span>
            </div>
            <div className="w-full bg-gray-300 rounded-full h-2.5 mb-1">
              <div
                className="bg-red-600 h-2.5 rounded-full"
                style={{ width: `${(requestCount / 10000) * 100}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-600">
              Simulating {requestCount.toLocaleString()} / 10,000 requests
            </p>
          </div>*/}

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

export default CheckoutErrorModal;