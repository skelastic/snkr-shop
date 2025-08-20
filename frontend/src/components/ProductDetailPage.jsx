import React, { useState, useEffect } from 'react';
import { ArrowLeft, Star, Heart, ShoppingBag, Truck, Shield, RotateCcw, Tag } from 'lucide-react';

const ProductDetailPage = ({ productId, onBack, addToCart }) => {
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedSize, setSelectedSize] = useState('');
  const [selectedColor, setSelectedColor] = useState('');
  const [selectedVariant, setSelectedVariant] = useState(null);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  useEffect(() => {
    fetchProductDetails();
  }, [productId]);

  useEffect(() => {
    if (selectedSize && selectedColor) {
      findSelectedVariant();
    }
  }, [selectedSize, selectedColor, product]);

  const fetchProductDetails = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/products/${productId}`);
      if (response.ok) {
        const data = await response.json();
        setProduct(data);

        // Set default selections
        if (data.available_sizes.length > 0) {
          setSelectedSize(data.available_sizes[0]);
        }
        if (data.available_colors.length > 0) {
          setSelectedColor(data.available_colors[0][0]); // color_code
        }
      } else {
        console.error('Failed to fetch product details');
      }
    } catch (error) {
      console.error('Error fetching product details:', error);
    } finally {
      setLoading(false);
    }
  };

  const findSelectedVariant = () => {
    if (!product) return;

    const variant = product.variants.find(v =>
      v.size === selectedSize && v.color_code === selectedColor
    );
    setSelectedVariant(variant);
  };

  const handleAddToCart = () => {
    if (!selectedVariant) return;

    // Create a sneaker object compatible with the cart system
    const sneakerForCart = {
      id: selectedVariant.id,
      sku: selectedVariant.sku,
      name: product.name,
      brand: product.brand,
      price: selectedVariant.price,
      sale_price: selectedVariant.sale_price,
      description: product.description,
      category: product.category,
      sizes: [selectedVariant.size],
      colors: [selectedVariant.color_name],
      image_url: product.images.main,
      stock_quantity: selectedVariant.stock_available,
      rating: product.rating,
      reviews_count: product.reviews_count,
      is_featured: product.is_featured,
      is_flash_sale: selectedVariant.is_flash_sale,
      flash_sale_end: selectedVariant.flash_sale_end,
      created_at: new Date().toISOString()
    };

    addToCart(sneakerForCart);
  };

  const getColorName = (colorCode) => {
    const colorMap = product.available_colors.find(([code]) => code === colorCode);
    return colorMap ? colorMap[1] : colorCode;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black"></div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Product not found</h2>
          <button
            onClick={onBack}
            className="bg-black text-white px-6 py-3 rounded-lg hover:bg-gray-800 transition-colors"
          >
            Back to Products
          </button>
        </div>
      </div>
    );
  }

  const currentPrice = selectedVariant?.sale_price || selectedVariant?.price || product.price_range.min;
  const originalPrice = selectedVariant?.price || product.price_range.max;
  const isOnSale = selectedVariant?.sale_price && selectedVariant.sale_price < selectedVariant.price;
  const isAvailable = selectedVariant?.stock_available > 0;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <button
            onClick={onBack}
            className="flex items-center text-gray-600 hover:text-black transition-colors"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back to Products
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Product Images */}
          <div className="space-y-4">
            <div className="aspect-square bg-white rounded-lg overflow-hidden shadow-md">
              <img
                src={product.images.gallery[currentImageIndex] || product.images.main}
                alt={product.name}
                className="w-full h-full object-cover"
              />
            </div>

            {/* Image Thumbnails */}
            <div className="grid grid-cols-4 gap-2">
              {[product.images.main, ...product.images.gallery].map((image, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentImageIndex(index)}
                  className={`aspect-square bg-white rounded-lg overflow-hidden shadow-sm border-2 transition-colors ${
                    currentImageIndex === index ? 'border-black' : 'border-transparent hover:border-gray-300'
                  }`}
                >
                  <img
                    src={image}
                    alt={`${product.name} ${index + 1}`}
                    className="w-full h-full object-cover"
                  />
                </button>
              ))}
            </div>
          </div>

          {/* Product Info */}
          <div className="space-y-6">
            {/* Basic Info */}
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <span className="text-sm font-medium text-gray-500 uppercase tracking-wide">
                  {product.brand}
                </span>
                {product.is_featured && (
                  <span className="bg-yellow-100 text-yellow-800 text-xs font-medium px-2 py-1 rounded">
                    Featured
                  </span>
                )}
                {selectedVariant?.is_flash_sale && (
                  <span className="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded animate-pulse">
                    FLASH SALE
                  </span>
                )}
              </div>
              <h1 className="text-3xl font-bold text-gray-900 mb-4">{product.name}</h1>

              {/* Rating */}
              <div className="flex items-center space-x-2 mb-4">
                <div className="flex items-center">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      className={`w-5 h-5 ${
                        i < Math.floor(product.rating)
                          ? 'text-yellow-400 fill-current'
                          : 'text-gray-300'
                      }`}
                    />
                  ))}
                </div>
                <span className="text-sm text-gray-600">
                  {product.rating} ({product.reviews_count} reviews)
                </span>
              </div>

              {/* Price */}
              <div className="flex items-center space-x-3 mb-6">
                <span className="text-3xl font-bold text-gray-900">
                  ${currentPrice.toFixed(2)}
                </span>
                {isOnSale && (
                  <span className="text-xl text-gray-500 line-through">
                    ${originalPrice.toFixed(2)}
                  </span>
                )}
                {product.price_range.min !== product.price_range.max && !selectedVariant && (
                  <span className="text-sm text-gray-500">
                    ${product.price_range.min.toFixed(2)} - ${product.price_range.max.toFixed(2)}
                  </span>
                )}
              </div>
            </div>

            {/* Size Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Size: {selectedSize && `US ${selectedSize}`}
              </label>
              <div className="grid grid-cols-6 gap-2">
                {product.available_sizes.map((size) => (
                  <button
                    key={size}
                    onClick={() => setSelectedSize(size)}
                    className={`py-3 text-sm font-medium rounded-lg border-2 transition-colors ${
                      selectedSize === size
                        ? 'border-black bg-black text-white'
                        : 'border-gray-300 bg-white text-gray-900 hover:border-gray-400'
                    }`}
                  >
                    {size}
                  </button>
                ))}
              </div>
            </div>

            {/* Color Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Color: {selectedColor && getColorName(selectedColor)}
              </label>
              <div className="flex flex-wrap gap-3">
                {product.available_colors.map(([colorCode, colorName]) => (
                  <button
                    key={colorCode}
                    onClick={() => setSelectedColor(colorCode)}
                    className={`px-4 py-2 text-sm font-medium rounded-lg border-2 transition-colors ${
                      selectedColor === colorCode
                        ? 'border-black bg-black text-white'
                        : 'border-gray-300 bg-white text-gray-900 hover:border-gray-400'
                    }`}
                  >
                    {colorName}
                  </button>
                ))}
              </div>
            </div>

            {/* Stock Status */}
            {selectedVariant && (
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">Stock Status:</span>
                  <span className={`text-sm font-medium ${
                    isAvailable ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {isAvailable
                      ? `${selectedVariant.stock_available} in stock`
                      : 'Out of stock'
                    }
                  </span>
                </div>
                {selectedVariant.sku && (
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-sm font-medium text-gray-700">SKU:</span>
                    <span className="text-sm text-gray-600">{selectedVariant.sku}</span>
                  </div>
                )}
              </div>
            )}

            {/* Add to Cart */}
            <div className="flex space-x-4">
              <button
                onClick={handleAddToCart}
                disabled={!isAvailable || !selectedVariant}
                className={`flex-1 flex items-center justify-center space-x-2 py-4 rounded-lg font-medium transition-colors ${
                  isAvailable && selectedVariant
                    ? 'bg-black text-white hover:bg-gray-800'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                <ShoppingBag className="w-5 h-5" />
                <span>{isAvailable ? 'Add to Cart' : 'Out of Stock'}</span>
              </button>

              <button className="p-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                <Heart className="w-5 h-5 text-gray-600" />
              </button>
            </div>

            {/* Product Details */}
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-3">Description</h3>
                <p className="text-gray-700 leading-relaxed">{product.description}</p>
              </div>

              {/* Features */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-3">Features</h3>
                <div className="space-y-2">
                  <div className="flex items-center space-x-3">
                    <Tag className="w-4 h-4 text-gray-500" />
                    <span className="text-sm text-gray-700">
                      Materials: {product.materials.join(', ')}
                    </span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <Shield className="w-4 h-4 text-gray-500" />
                    <span className="text-sm text-gray-700">
                      Technology: {product.technology.join(', ')}
                    </span>
                  </div>
                </div>
              </div>

              {/* Shipping & Returns */}
              <div className="border-t pt-6">
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <Truck className="w-5 h-5 text-gray-500" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">Free Shipping</p>
                      <p className="text-sm text-gray-600">On orders over $100</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <RotateCcw className="w-5 h-5 text-gray-500" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">Free Returns</p>
                      <p className="text-sm text-gray-600">30-day return policy</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <Shield className="w-5 h-5 text-gray-500" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">Authenticity Guaranteed</p>
                      <p className="text-sm text-gray-600">100% authentic products</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Variant Information Table */}
        <div className="mt-12">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">All Available Variants</h3>
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Size
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Color
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Price
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Stock
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      SKU
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {product.variants.map((variant) => (
                    <tr key={variant.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        US {variant.size}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {variant.color_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div className="flex items-center space-x-2">
                          <span className={variant.sale_price ? 'line-through text-gray-500' : 'font-medium'}>
                            ${variant.price.toFixed(2)}
                          </span>
                          {variant.sale_price && (
                            <span className="font-medium text-red-600">
                              ${variant.sale_price.toFixed(2)}
                            </span>
                          )}
                          {variant.is_flash_sale && (
                            <span className="bg-red-100 text-red-800 text-xs font-medium px-2 py-1 rounded">
                              SALE
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          variant.stock_available > 0
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {variant.stock_available > 0
                            ? `${variant.stock_available} in stock`
                            : 'Out of stock'
                          }
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">
                        {variant.sku}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button
                          onClick={() => {
                            setSelectedSize(variant.size);
                            setSelectedColor(variant.color_code);
                          }}
                          disabled={variant.stock_available === 0}
                          className={`${
                            variant.stock_available > 0
                              ? 'text-black hover:text-gray-700'
                              : 'text-gray-400 cursor-not-allowed'
                          }`}
                        >
                          {variant.stock_available > 0 ? 'Select' : 'Unavailable'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetailPage;