import React from 'react';

const FilterSection = ({ 
  showFilters, 
  selectedBrand, 
  setSelectedBrand, 
  selectedCategory, 
  setSelectedCategory, 
  setSearchTerm,
  brands, 
  categories 
}) => (
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
          className="px-4 py-2 text-gray-600 hover:text-black transition-colors"
        >
          Clear All
        </button>
      </div>
    </div>
  </div>
);

export default FilterSection;