#!/bin/bash

# Script to populate the hybrid database with 100K products and 500K SKUs

echo "🚀 Starting Hybrid Database Population"
echo "Target: 100,000 products × 5 SKUs each = 500,000 SKUs"
echo "=================================================="

# Check if MongoDB is running
echo "Checking MongoDB connection..."
if ! mongosh --host localhost:27017 --eval "db.runCommand('ping')" > /dev/null 2>&1; then
    echo "❌ MongoDB is not running. Please start MongoDB first:"
    echo "   docker run -d --name sneaker-mongo -p 27017:27017 \\"
    echo "     -e MONGO_INITDB_ROOT_USERNAME=admin \\"
    echo "     -e MONGO_INITDB_ROOT_PASSWORD=password123 \\"
    echo "     mongo:7.0"
    exit 1
fi

echo "✅ MongoDB is running"

# Install Python dependencies if needed
echo "Installing Python dependencies..."
pip install motor pymongo asyncio > /dev/null 2>&1

# Run the population script
echo "🔄 Starting population process..."
echo "This will take approximately 15-30 minutes for 100K products"
echo "Progress will be shown every 1000 products"
echo ""

python3 << 'EOF'
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.getcwd())

# Import and run the population script
from hybrid_population_script import main

if __name__ == "__main__":
    asyncio.run(main())
EOF

echo ""
echo "🎉 Population completed!"
echo ""
echo "Database Statistics:"
echo "===================="

# Get final counts
mongosh --host localhost:27017 --quiet --eval "
use sneaker_store;
const products = db.products.countDocuments({});
const skus = db.skus.countDocuments({});
const featured = db.products.countDocuments({is_featured: true});
const flashSales = db.skus.countDocuments({is_flash_sale: true});

print('Products: ' + products.toLocaleString());
print('SKUs: ' + skus.toLocaleString());
print('Featured Products: ' + featured.toLocaleString());
print('Flash Sale SKUs: ' + flashSales.toLocaleString());
print('Average SKUs per Product: ' + (skus/products).toFixed(1));
"

echo ""
echo "🔧 API Endpoints Available:"
echo "=========================="
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "Frontend: http://localhost:3000"
echo ""
echo "Sample API calls:"
echo "GET /sneakers - List all available sneakers"
echo "GET /flash-sales - Get flash sale items"
echo "GET /featured - Get featured products"
echo "GET /brands - List all brands"
echo "GET /categories - List all categories"
echo ""
echo "Ready for e-commerce! 🛒"