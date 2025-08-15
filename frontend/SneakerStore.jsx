import React, { useState, useEffect } from 'react';
import { Search, ShoppingBag, User, Heart, Menu, X, Star, Clock, Filter } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

const SneakerStore = () => {
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

  useEffect(() => {
    fetchInitialData();
    fetchSneakers();
  }, [currentPage, selectedBrand, selectedCategory, searchTerm]);

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

  const addToCart = (sneaker) => {
    setCart(prev => {
      const existing = prev.find(item => item.id === sneaker.id);
      if (existing) {
        return prev.map(item => 
          item.id === sneaker.id 
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      }
      return [...prev, { ...sneaker, quantity: 1 }];
    });
  };

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

  const Header = () => (
    <header className="bg-white shadow-md sticky top-0 z-50">
      <FlashSaleBanner />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <div className="text-2xl font-bold text-black">
              SNKR<span className="text-red-500">STORE</span>
            </div>
          </div>
          
          <nav className="hidden md:flex space-x-8">
            <a href="#" className="text-gray-700 hover:text-black font-medium">New & Featured</a>
            <a href="#" className="text-gray-700 hover:text-black font-medium">Men</a>
            <a href="#" className="text-gray-700 hover:text-black font-medium">Women</a>
            <a href="#" className="text-gray-700 hover:text-black font-medium">Kids</a>
            <a href="#" className="text-gray-700 hover:text-black font-medium">Sale</a>
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
            <Heart className="w-6 h-6 text-gray-700 hover:text-black cursor-pointer" />
            <div className="relative cursor-pointer">
              <ShoppingBag className="w-6 h-6 text-gray-700 hover:text-black" />
              {cart.length > 0 && (
                <span className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs">
                  {cart.reduce((sum, item) => sum + item.quantity, 0)}
                </span>
              )}
            </div>
            <User className="w-6 h-6 text-gray-700 hover:text-black cursor-pointer" />
          </div>
        </div>
      </div>
    </header>
  );

  const HeroSection = () => (
    <section className="bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-5xl md:text-7xl font-bold mb-6">
            JUST DO IT
          </h1>
          <p className="text-xl md:text-2xl mb-8 text-gray-300">
            Discover the latest drops and exclusive sneakers
          </p>
          <button className="bg-white text-black px-8 py-4 rounded-full font-bold text-lg hover:bg-gray-200 transition-colors">
            Shop Now
          </button>
        </div>
      </div>
    </section>
  );

  const FlashSaleSection = () => {
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
              <ProductCard key={sneaker.id} sneaker={sneaker} isFlashSale />
            ))}
          </div>
        </div>
      </section>
    );
  };

  const ProductCard = ({ sneaker, isFlashSale = false }) => (
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

  const FilterSection = () => (
    <div className={`bg-white border-b ${showFilters ? 'block' : 'hidden'} md:block`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex flex-wrap gap-4">
          <select
            value={selectedBrand}
            onChange={(e) => setSelectedBrand(e.target.value)}
            className="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-black"
          >
            <option value="">All Brands</option>
            {brands.map(brand => (
              <option key={brand} value={brand}>{brand}</option>
            ))}
          </select>
          
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-black"
          >
            <option value="">All Categories</option>
            {categories.map(category => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>
          
          <button
            onClick={() => {
              setSelectedBrand('');
              setSelectedCategory('');
              setSearchTerm('');
            }}
            className="px-4 py-2 text-gray-600 hover:text-black"
          >
            Clear All
          </button>
        </div>
      </div>
    </div>
  );

  const Pagination = () => {
    if (totalPages <= 1) return null;

    return (
      <div className="flex justify-center items-center space-x-2 py-8">
        <button
          onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
          disabled={currentPage === 1}
          className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50"
        >
          Previous
        </button>
        
        <span className="px-4 py-2">
          Page {currentPage} of {totalPages}
        </span>
        
        <button
          onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
          disabled={currentPage === totalPages}
          className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50"
        >
          Next
        </button>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <HeroSection />
      <FlashSaleSection />
      
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
      
      <FilterSection />
      
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
                <ProductCard key={sneaker.id} sneaker={sneaker} />
              ))}
            </div>
            <Pagination />
          </>
        )}
      </main>
    </div>
  );
};

export default SneakerStore;