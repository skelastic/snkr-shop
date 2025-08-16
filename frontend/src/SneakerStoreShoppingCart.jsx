import React, { useState, useEffect, useRef } from 'react';
import { Filter } from 'lucide-react';

// Import all components
import Header from './components/Header';
import HeroSection from './components/HeroSection';
import FlashSaleSection from './components/FlashSaleSection';
import FilterSection from './components/FilterSection';
import ProductCard from './components/ProductCard';
import Pagination from './components/Pagination';
import ShoppingCartPage from './components/ShoppingCartPage';

const API_BASE = 'http://localhost:8000';

const SneakerStoreShoppingCart = () => {
  // State management
  const [sneakers, setSneakers] = useState([]);
  const [flashSales, setFlashSales] = useState([]);
  const [featured, setFeatured] = useState([]);
  const [brands, setBrands] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedBrand, setSelectedBrand] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showFilters, setShowFilters] = useState(false);
  const [cart, setCart] = useState([]);
  const [showCartPage, setShowCartPage] = useState(false);
  const [showCartDropdown, setShowCartDropdown] = useState(false);
  const [promoCode, setPromoCode] = useState('');
  const [appliedPromo, setAppliedPromo] = useState(null);

  const cartDropdownRef = useRef(null);

  // Effects
  useEffect(() => {
    fetchInitialData();
    fetchSneakers();
  }, [currentPage, selectedBrand, selectedCategory, searchTerm]);

  // Close cart dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (cartDropdownRef.current && !cartDropdownRef.current.contains(event.target)) {
        setShowCartDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Debug cart updates
  useEffect(() => {
    console.log("Cart updated:", cart);
  }, [cart]);

  // Initialize cart from localStorage if available
  useEffect(() => {
    const savedCart = localStorage.getItem('cart');
    if (savedCart) {
      try {
        setCart(JSON.parse(savedCart));
      } catch (e) {
        console.error("Error parsing saved cart:", e);
      }
    }
  }, []);

  // Save cart to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('cart', JSON.stringify(cart));
  }, [cart]);

  // API functions
  const fetchInitialData = async () => {
    try {
      const [flashResponse, featuredResponse, brandsResponse, categoriesResponse] = await Promise.all([
        fetch(`${API_BASE}/flash-sales`),
        fetch(`${API_BASE}/featured`),
        fetch(`${API_BASE}/brands`),
        fetch(`${API_BASE}/categories`)
      ]);

      const [flashData, featuredData, brandsData, categoriesData] = await Promise.all([
        flashResponse.json(),
        featuredResponse.json(),
        brandsResponse.json(),
        categoriesResponse.json()
      ]);

      setFlashSales(flashData.flash_sales || []);
      setFeatured(featuredData.featured || []);
      setBrands(brandsData.brands || []);
      setCategories(categoriesData.categories || []);
    } catch (error) {
      console.error('Error fetching initial data:', error);
    }
  };

  const fetchSneakers = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: currentPage.toString(),
        per_page: '20'
      });

      if (searchTerm) params.append('search', searchTerm);
      if (selectedBrand) params.append('brand', selectedBrand);
      if (selectedCategory) params.append('category', selectedCategory);

      const response = await fetch(`${API_BASE}/sneakers?${params}`);
      const data = await response.json();

      setSneakers(data.sneakers || []);
      setTotalPages(data.total_pages || 1);
    } catch (error) {
      console.error('Error fetching sneakers:', error);
    } finally {
      setLoading(false);
    }
  };

  // Cart functions
  const addToCart = (sneaker) => {
    console.log("Adding to cart:", sneaker); // Debug log

    // Check if the sneaker has a valid ID (using _id as the identifier)
    if (!sneaker || !sneaker.id) {
      console.error("Invalid sneaker object (missing _id):", sneaker);
      return;
    }

    // Update the cart state with the new item or increment existing item's quantity
    setCart(prev => {
      // Make a deep copy of the previous cart to avoid reference issues
      const prevCart = [...prev];

      // Find if this product already exists in the cart using _id
      const existingIndex = prevCart.findIndex(item => item.id === sneaker.id);

      if (existingIndex >= 0) {
        // If the product exists, create a new array with the updated item
        const updatedCart = [...prevCart];
        updatedCart[existingIndex] = {
          ...updatedCart[existingIndex],
          quantity: updatedCart[existingIndex].quantity + 1
        };
        return updatedCart;
      } else {
        // If the product doesn't exist, add it as a new item with quantity 1
        return [...prevCart, { ...sneaker, quantity: 1 }];
      }
    });

    // Show dropdown briefly when item is added
    setShowCartDropdown(true);
    setTimeout(() => {
      if (!cartDropdownRef.current?.matches(':hover')) {
        setShowCartDropdown(false);
      }
    }, 2000);
  };

  const removeFromCart = (id) => {
    setCart(prev => prev.filter(item => item.id !== id));
  };

  const updateCartQuantity = (id, quantity) => {
    if (quantity === 0) {
      removeFromCart(id);
      return;
    }
    setCart(prev =>
      prev.map(item =>
        item.id === id ? { ...item, quantity } : item
      )
    );
  };

  const getTotalItems = () => {
    return cart.reduce((sum, item) => sum + item.quantity, 0);
  };

  const getTotalPrice = () => {
    return cart.reduce((sum, item) => {
      const price = item.sale_price || item.price;
      return sum + (price * item.quantity);
    }, 0);
  };

  // Promo code functions
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

  // Calculate cart totals for cart page
  const subtotal = getTotalPrice();
  const shipping = subtotal > 100 ? 0 : 9.99;
  const tax = subtotal * 0.08;
  const discount = appliedPromo ? subtotal * 0.1 : 0;
  const total = subtotal + shipping + tax - discount;

  // If showing cart page, render it instead of the main store
  if (showCartPage) {
    return (
      <ShoppingCartPage
        cart={cart}
        getTotalItems={getTotalItems}
        removeFromCart={removeFromCart}
        updateCartQuantity={updateCartQuantity}
        setShowCartPage={setShowCartPage}
        promoCode={promoCode}
        setPromoCode={setPromoCode}
        appliedPromo={appliedPromo}
        applyPromoCode={applyPromoCode}
        removePromoCode={removePromoCode}
        subtotal={subtotal}
        shipping={shipping}
        tax={tax}
        discount={discount}
        total={total}
      />
    );
  }

  // Main store render
  return (
    <div className="min-h-screen bg-gray-50">
      <Header
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
        cart={cart}
        showCartDropdown={showCartDropdown}
        setShowCartDropdown={setShowCartDropdown}
        setShowCartPage={setShowCartPage}
        cartDropdownRef={cartDropdownRef}
        updateCartQuantity={updateCartQuantity}
        getTotalItems={getTotalItems}
        getTotalPrice={getTotalPrice}
      />

      <HeroSection />

      <FlashSaleSection
        flashSales={flashSales}
        addToCart={addToCart}
      />

      <div className="flex items-center justify-between max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <h2 className="text-2xl font-bold text-gray-900">All Sneakers</h2>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="md:hidden flex items-center space-x-2 text-gray-600"
        >
          <Filter className="w-5 h-5" />
          <span>Filters</span>
        </button>
      </div>

      <FilterSection
        showFilters={showFilters}
        selectedBrand={selectedBrand}
        setSelectedBrand={setSelectedBrand}
        selectedCategory={selectedCategory}
        setSelectedCategory={setSelectedCategory}
        setSearchTerm={setSearchTerm}
        brands={brands}
        categories={categories}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {Array(8).fill(0).map((_, i) => (
              <div key={i} className="bg-white rounded-lg shadow-md overflow-hidden animate-pulse">
                <div className="bg-gray-300 h-64 w-full"></div>
                <div className="p-6">
                  <div className="bg-gray-300 h-4 rounded mb-2"></div>
                  <div className="bg-gray-300 h-3 rounded w-3/4 mb-2"></div>
                  <div className="bg-gray-300 h-3 rounded w-1/2"></div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {sneakers.map(sneaker => (
                <ProductCard
                  key={sneaker.id}
                  sneaker={sneaker}
                  addToCart={addToCart}
                />
              ))}
            </div>
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              setCurrentPage={setCurrentPage}
            />
          </>
        )}
      </main>

      {/* Debug section - remove in production */}
      {process.env.NODE_ENV === 'development' && (
        <div className="max-w-7xl mx-auto px-4 py-8 border-t">
          <h2 className="text-xl font-bold mb-4">Cart Content Debug:</h2>
          <pre className="bg-gray-100 p-4 rounded overflow-auto max-h-60">
            {JSON.stringify(cart, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default SneakerStoreShoppingCart;