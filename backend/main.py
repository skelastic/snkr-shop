from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
import os
from bson import ObjectId
import asyncio
import random
import string
import redis.asyncio as redis
import json
import hashlib

app = FastAPI(title="Sneaker Store API", version="1.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGODB_URL)
database = client.sneaker_store
products_collection = database.products
skus_collection = database.skus
inventory_log_collection = database.inventory_log
users_collection = database.users
orders_collection = database.orders

# Redis connection
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Cache configuration
CACHE_TTL = {
    "sneakers": 300,      # 5 minutes for product listings
    "sneaker_detail": 600, # 10 minutes for individual products
    "variants": 300,       # 5 minutes for product variants
    "flash_sales": 120,    # 2 minutes for flash sales (more dynamic)
    "featured": 600,       # 10 minutes for featured products
    "brands": 3600,        # 1 hour for brands (rarely change)
    "categories": 3600,    # 1 hour for categories (rarely change)
    "stats": 300           # 5 minutes for stats
}

# Pydantic models
class Product(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    product_id: str
    name: str
    brand: str
    category: str
    description: str
    base_price: float
    images: dict
    release_date: datetime
    materials: List[str]
    technology: List[str]
    available_sizes: List[float]
    available_colors: List[str]
    is_featured: bool = False
    rating: float
    reviews_count: int
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class SKU(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    sku: str
    product_id: str
    size: float
    color_code: str
    color_name: str
    price: float
    sale_price: Optional[float] = None
    stock_quantity: int
    stock_reserved: int = 0
    stock_available: int
    weight: float
    dimensions: dict
    barcode: str
    supplier_code: str
    warehouse_location: str
    is_flash_sale: bool = False
    flash_sale_end: Optional[datetime] = None
    # Denormalized fields for performance
    brand: str
    category: str
    product_name: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class Sneaker(BaseModel):
    """Legacy model for backward compatibility - combines Product + SKU data"""
    id: Optional[str] = Field(default=None, alias="_id")
    sku: str
    name: str
    brand: str
    price: float
    sale_price: Optional[float] = None
    description: str
    category: str
    sizes: List[float]
    colors: List[str]
    image_url: str
    stock_quantity: int
    rating: float
    reviews_count: int
    is_featured: bool = False
    is_flash_sale: bool = False
    flash_sale_end: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class SneakerResponse(BaseModel):
    sneakers: List[Sneaker]
    total: int
    page: int
    per_page: int
    total_pages: int

class User(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    email: str
    name: str
    created_at: datetime = Field(default_factory=datetime.now)

class CartItem(BaseModel):
    sneaker_id: str
    size: float
    quantity: int

class Order(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    items: List[CartItem]
    total_amount: float
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.now)

# Helper function to generate random SKU
def generate_sku():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def generate_product_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

# Cache utility functions
def generate_cache_key(prefix: str, **kwargs) -> str:
    """Generate a consistent cache key from parameters"""
    # Sort kwargs to ensure consistent key generation
    # Filter out None values and convert everything to strings
    filtered_params = {k: str(v) for k, v in kwargs.items() if v is not None}
    sorted_params = sorted(filtered_params.items())
    param_string = "&".join([f"{k}={v}" for k, v in sorted_params])

    # Create a hash of the parameters to keep keys short
    if param_string:
        param_hash = hashlib.md5(param_string.encode()).hexdigest()[:8]
        return f"{prefix}:{param_hash}"
    return prefix

async def get_cached_data(cache_key: str):
    """Get data from Redis cache"""
    try:
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            print(f"📥 Found cached data for key: {cache_key}")
            return json.loads(cached_data)
        else:
            print(f"🚫 No cached data found for key: {cache_key}")
        return None
    except Exception as e:
        print(f"❌ Cache get error for key {cache_key}: {e}")
        return None

async def set_cached_data(cache_key: str, data: dict, ttl: int):
    """Set data in Redis cache with TTL"""
    try:
        # Custom JSON encoder to handle datetime and ObjectId
        def json_encoder(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, ObjectId):
                return str(obj)
            return str(obj)

        json_data = json.dumps(data, default=json_encoder)
        await redis_client.setex(cache_key, ttl, json_data)
        print(f"💾 Cached data for key: {cache_key} (TTL: {ttl}s)")
    except Exception as e:
        print(f"❌ Cache set error for key {cache_key}: {e}")

async def invalidate_cache_pattern(pattern: str):
    """Invalidate all cache keys matching a pattern"""
    try:
        keys = await redis_client.keys(pattern)
        if keys:
            await redis_client.delete(*keys)
    except Exception as e:
        print(f"Cache invalidation error: {e}")

async def clear_all_cache():
    """Clear all cache (useful for development)"""
    try:
        await redis_client.flushdb()
    except Exception as e:
        print(f"Cache clear error: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up connections on shutdown"""
    try:
        await redis_client.close()
        print("✅ Redis connection closed")
    except Exception as e:
        print(f"❌ Error closing Redis connection: {e}")

# Database stats endpoint
@app.get("/stats")
async def get_database_stats():
    # 🔍 Check cache first
    cache_key = generate_cache_key("stats")
    cached_stats = await get_cached_data(cache_key)
    if cached_stats:
        print(f"📦 Cache HIT for stats")
        return cached_stats

    print(f"🔄 Cache MISS for stats - querying database")

    products_count = await products_collection.count_documents({})
    skus_count = await skus_collection.count_documents({})
    available_skus_count = await skus_collection.count_documents({"stock_available": {"$gt": 0}})

    brands = await products_collection.distinct("brand")
    categories = await products_collection.distinct("category")

    stats_data = {
        "products_count": products_count,
        "skus_count": skus_count,
        "available_skus_count": available_skus_count,
        "brands_count": len(brands),
        "categories_count": len(categories),
        "brands": sorted(brands),
        "categories": sorted(categories)
    }

    # 💾 Cache the result
    await set_cached_data(cache_key, stats_data, CACHE_TTL["stats"])

    return stats_data

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Sneaker Store API is running!"}

@app.get("/sneakers", response_model=SneakerResponse)
async def get_sneakers(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    brand: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    featured_only: Optional[bool] = False,
    flash_sale_only: Optional[bool] = False
):
    # 🔍 Generate cache key and check cache first
    cache_key = generate_cache_key(
        "sneakers",
        page=page,
        per_page=per_page,
        brand=brand,
        category=category,
        min_price=min_price,
        max_price=max_price,
        search=search,
        featured_only=featured_only,
        flash_sale_only=flash_sale_only
    )

    print(f"🔑 Generated cache key: {cache_key}")

    cached_response = await get_cached_data(cache_key)
    if cached_response:
        print(f"📦 Cache HIT for sneakers query: {cache_key}")
        return SneakerResponse(**cached_response)

    print(f"🔄 Cache MISS for sneakers query: {cache_key} - querying database")

    # Build base filter for products
    match_filter = {}

    if brand:
        match_filter["brand"] = {"$regex": brand, "$options": "i"}
    if category:
        match_filter["category"] = {"$regex": category, "$options": "i"}
    if search:
        match_filter["name"] = {"$regex": search, "$options": "i"}
    if featured_only:
        match_filter["is_featured"] = True

    # Build the aggregation pipeline
    pipeline = [
        {"$match": match_filter},
        {"$limit": 100},  # Limit to first 1000 products for performance
        {
            "$lookup": {
                "from": "skus",
                "localField": "product_id",
                "foreignField": "product_id",
                "as": "variants"
            }
        },
        {
            "$addFields": {
                "total_stock": {"$sum": "$variants.stock_available"},
                "min_price": {"$min": "$variants.price"},
                "variant_count": {"$size": "$variants"}
            }
        }
    ]

    # Add variant-level filters if needed
    variant_filters = []
    if min_price is not None or max_price is not None or flash_sale_only:
        variant_match = {}
        if min_price is not None:
            variant_match["price"] = {"$gte": min_price}
        if max_price is not None:
            variant_match.setdefault("price", {})["$lte"] = max_price
        if flash_sale_only:
            variant_match["is_flash_sale"] = True
            variant_match["flash_sale_end"] = {"$gt": datetime.now()}

        # Filter variants and recalculate aggregated fields
        pipeline.extend([
            {
                "$addFields": {
                    "filtered_variants": {
                        "$filter": {
                            "input": "$variants",
                            "cond": {
                                "$and": [
                                    {"$gt": ["$this.stock_available", 0]},
                                    *[{f"${op}": [f"$this.{field}", value]}
                                      for field, condition in variant_match.items()
                                      for op, value in (condition.items() if isinstance(condition, dict) else [("eq", condition)])]
                                ]
                            }
                        }
                    }
                }
            },
            {
                "$match": {
                    "filtered_variants": {"$ne": []}
                }
            },
            {
                "$addFields": {
                    "variants": "$filtered_variants",
                    "total_stock": {"$sum": "$filtered_variants.stock_available"},
                    "min_price": {"$min": "$filtered_variants.price"},
                    "variant_count": {"$size": "$filtered_variants"}
                }
            }
        ])
    else:
        # Just filter out variants with no stock
        pipeline.extend([
            {
                "$addFields": {
                    "variants": {
                        "$filter": {
                            "input": "$variants",
                            "cond": {"$gt": ["$this.stock_available", 0]}
                        }
                    }
                }
            },
            {
                "$match": {
                    "variants": {"$ne": []}
                }
            },
            {
                "$addFields": {
                    "total_stock": {"$sum": "$variants.stock_available"},
                    "min_price": {"$min": "$variants.price"},
                    "variant_count": {"$size": "$variants"}
                }
            }
        ])

    # Get total count for pagination
    count_pipeline = pipeline + [{"$count": "total"}]
    count_result = await products_collection.aggregate(count_pipeline).to_list(length=1)
    total = count_result[0]["total"] if count_result else 0

    # Add pagination and sorting
    skip = (page - 1) * per_page
    total_pages = (total + per_page - 1) // per_page

    paginated_pipeline = pipeline + [
        {"$sort": {"min_price": 1, "name": 1}},
        {"$skip": skip},
        {"$limit": per_page}
    ]

    # Execute the aggregation
    cursor = products_collection.aggregate(paginated_pipeline)
    results = await cursor.to_list(length=per_page)

    # Convert to legacy Sneaker format
    sneakers = []
    for product in results:
        # Get representative variant (lowest price)
        representative_variant = min(product["variants"], key=lambda x: x["price"]) if product["variants"] else None

        if not representative_variant:
            continue

        # Extract all unique sizes and colors
        all_sizes = sorted(list(set(variant["size"] for variant in product["variants"])))
        all_colors = list(set(variant["color_name"] for variant in product["variants"]))

        sneaker = {
            "id": str(product["_id"]),
            "sku": representative_variant["sku"],
            "name": product["name"],
            "brand": product["brand"],
            "price": product["min_price"],
            "sale_price": representative_variant.get("sale_price"),
            "description": product["description"],
            "category": product["category"],
            "sizes": all_sizes,
            "colors": all_colors,
            "image_url": product["images"]["main"],
            "stock_quantity": product["total_stock"],
            "rating": product["rating"],
            "reviews_count": product["reviews_count"],
            "is_featured": product["is_featured"],
            "is_flash_sale": representative_variant["is_flash_sale"],
            "flash_sale_end": representative_variant.get("flash_sale_end"),
            "created_at": product["created_at"]
        }
        sneakers.append(sneaker)

    # 📦 Prepare response data
    response_data = {
        "sneakers": sneakers,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages
    }

    # 💾 Cache the result in Redis
    await set_cached_data(cache_key, response_data, CACHE_TTL["sneakers"])

    return SneakerResponse(**response_data)

@app.get("/sneakers/{sneaker_id}", response_model=Sneaker)
async def get_sneaker(sneaker_id: str):
    # 🔍 Check cache first
    cache_key = generate_cache_key("sneaker_detail", sneaker_id=sneaker_id)
    cached_sneaker = await get_cached_data(cache_key)
    if cached_sneaker:
        print(f"📦 Cache HIT for sneaker {sneaker_id}")
        return Sneaker(**cached_sneaker)

    print(f"🔄 Cache MISS for sneaker {sneaker_id} - querying database")

    try:
        # Try to find by product _id first
        product = await products_collection.find_one({"_id": ObjectId(sneaker_id)})

        if not product:
            # Fallback: try to find by SKU _id and get the product
            sku = await skus_collection.find_one({"_id": ObjectId(sneaker_id)})
            if not sku:
                raise HTTPException(status_code=404, detail="Sneaker not found")

            product = await products_collection.find_one({"product_id": sku["product_id"]})
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")

        # Get all SKUs for this product
        skus = await skus_collection.find(
            {"product_id": product["product_id"], "stock_available": {"$gt": 0}}
        ).to_list(length=None)

        if not skus:
            raise HTTPException(status_code=404, detail="No available variants found")

        # Get the representative SKU (lowest price)
        representative_sku = min(skus, key=lambda x: x["price"])

        # Aggregate data
        all_sizes = sorted(list(set(sku["size"] for sku in skus)))
        all_colors = list(set(sku["color_name"] for sku in skus))
        total_stock = sum(sku["stock_available"] for sku in skus)
        min_price = min(sku["price"] for sku in skus)

        sneaker_data = {
            "id": str(product["_id"]),
            "sku": representative_sku["sku"],
            "name": product["name"],
            "brand": product["brand"],
            "price": min_price,
            "sale_price": representative_sku.get("sale_price"),
            "description": product["description"],
            "category": product["category"],
            "sizes": all_sizes,
            "colors": all_colors,
            "image_url": product["images"]["main"],
            "stock_quantity": total_stock,
            "rating": product["rating"],
            "reviews_count": product["reviews_count"],
            "is_featured": product["is_featured"],
            "is_flash_sale": representative_sku["is_flash_sale"],
            "flash_sale_end": representative_sku.get("flash_sale_end"),
            "created_at": product["created_at"]
        }

        # 💾 Cache the result
        await set_cached_data(cache_key, sneaker_data, CACHE_TTL["sneaker_detail"])

        return Sneaker(**sneaker_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid sneaker ID: {str(e)}")

@app.get("/flash-sales")
async def get_flash_sales():
    # 🔍 Check cache first
    cache_key = generate_cache_key("flash_sales")
    cached_flash_sales = await get_cached_data(cache_key)
    if cached_flash_sales:
        print(f"📦 Cache HIT for flash sales")
        return cached_flash_sales

    print(f"🔄 Cache MISS for flash sales - querying database")

    current_time = datetime.now()

    # Get products with flash sale SKUs
    pipeline = [
        {"$match": {
            "is_flash_sale": True,
            "flash_sale_end": {"$gt": current_time},
            "stock_available": {"$gt": 0}
        }},
        {"$lookup": {
            "from": "products",
            "localField": "product_id",
            "foreignField": "product_id",
            "as": "product_info"
        }},
        {"$unwind": "$product_info"},
        {
            "$group": {
                "_id": "$product_id",
                "product": {"$first": "$product_info"},
                "representative_sku": {"$first": "$$ROOT"},
                "all_sizes": {"$addToSet": "$size"},
                "all_colors": {"$addToSet": "$color_name"},
                "total_stock": {"$sum": "$stock_available"}
            }
        },
        {"$limit": 10}
    ]

    cursor = skus_collection.aggregate(pipeline)
    results = await cursor.to_list(length=10)

    sneakers = []
    for item in results:
        product = item["product"]
        sku = item["representative_sku"]

        sneaker = {
            "id": str(product["_id"]),
            "sku": sku["sku"],
            "name": product["name"],
            "brand": product["brand"],
            "price": sku["price"],
            "sale_price": sku.get("sale_price"),
            "description": product["description"],
            "category": product["category"],
            "sizes": sorted(item["all_sizes"]),
            "colors": item["all_colors"],
            "image_url": product["images"]["main"],
            "stock_quantity": item["total_stock"],
            "rating": product["rating"],
            "reviews_count": product["reviews_count"],
            "is_featured": product["is_featured"],
            "is_flash_sale": sku["is_flash_sale"],
            "flash_sale_end": sku.get("flash_sale_end"),
            "created_at": product["created_at"]
        }
        sneakers.append(sneaker)

    flash_sales_data = {"flash_sales": sneakers}

    # 💾 Cache the result
    await set_cached_data(cache_key, flash_sales_data, CACHE_TTL["flash_sales"])

    return flash_sales_data

@app.get("/featured")
async def get_featured_sneakers():
    # 🔍 Check cache first
    cache_key = generate_cache_key("featured")
    cached_featured = await get_cached_data(cache_key)
    if cached_featured:
        print(f"📦 Cache HIT for featured sneakers")
        return cached_featured

    print(f"🔄 Cache MISS for featured sneakers - querying database")

    # Get featured products with their representative SKUs
    pipeline = [
        {"$match": {"is_featured": True}},
        {"$lookup": {
            "from": "skus",
            "localField": "product_id",
            "foreignField": "product_id",
            "as": "skus"
        }},
        {"$unwind": "$skus"},
        {"$match": {"skus.stock_available": {"$gt": 0}}},
        {
            "$group": {
                "_id": "$product_id",
                "product": {"$first": "$$ROOT"},
                "representative_sku": {
                    "$min": {
                        "price": "$skus.price",
                        "sku_data": "$skus"
                    }
                },
                "all_sizes": {"$addToSet": "$skus.size"},
                "all_colors": {"$addToSet": "$skus.color_name"},
                "total_stock": {"$sum": "$skus.stock_available"}
            }
        },
        {"$limit": 8}
    ]

    cursor = products_collection.aggregate(pipeline)
    results = await cursor.to_list(length=8)

    sneakers = []
    for item in results:
        product = item["product"]
        sku_data = item["representative_sku"]["sku_data"]

        sneaker = {
            "id": str(product["_id"]),
            "sku": sku_data["sku"],
            "name": product["name"],
            "brand": product["brand"],
            "price": item["representative_sku"]["price"],
            "sale_price": sku_data.get("sale_price"),
            "description": product["description"],
            "category": product["category"],
            "sizes": sorted(item["all_sizes"]),
            "colors": item["all_colors"],
            "image_url": product["images"]["main"],
            "stock_quantity": item["total_stock"],
            "rating": product["rating"],
            "reviews_count": product["reviews_count"],
            "is_featured": product["is_featured"],
            "is_flash_sale": sku_data["is_flash_sale"],
            "flash_sale_end": sku_data.get("flash_sale_end"),
            "created_at": product["created_at"]
        }
        sneakers.append(sneaker)

    featured_data = {"featured": sneakers}

    # 💾 Cache the result
    await set_cached_data(cache_key, featured_data, CACHE_TTL["featured"])

    return featured_data

@app.get("/sneakers/{sneaker_id}/variants")
async def get_sneaker_variants(sneaker_id: str):
    """Get all available size/color variants for a specific product"""
    # 🔍 Check cache first
    cache_key = generate_cache_key("variants", sneaker_id=sneaker_id)
    cached_variants = await get_cached_data(cache_key)
    if cached_variants:
        print(f"📦 Cache HIT for variants {sneaker_id}")
        return cached_variants

    print(f"🔄 Cache MISS for variants {sneaker_id} - querying database")

    try:
        # Get the product first
        product = await products_collection.find_one({"_id": ObjectId(sneaker_id)})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Get all SKUs for this product
        skus = await skus_collection.find(
            {"product_id": product["product_id"], "stock_available": {"$gt": 0}}
        ).sort("price", 1).to_list(length=None)

        if not skus:
            variants_data = {"variants": []}
        else:
            variants = []
            for sku in skus:
                variant = {
                    "sku_id": str(sku["_id"]),
                    "sku": sku["sku"],
                    "size": sku["size"],
                    "color_name": sku["color_name"],
                    "color_code": sku["color_code"],  # Keep original format (e.g., "TB")
                    "price": sku["price"],
                    "sale_price": sku.get("sale_price"),
                    "stock_available": sku["stock_available"],
                    "is_flash_sale": sku["is_flash_sale"],
                    "flash_sale_end": sku.get("flash_sale_end")
                }
                variants.append(variant)

            variants_data = {
                "product_id": str(product["_id"]),
                "product_name": product["name"],
                "variants": variants
            }

        # 💾 Cache the result
        await set_cached_data(cache_key, variants_data, CACHE_TTL["variants"])

        return variants_data

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid product ID: {str(e)}")

@app.get("/brands")
async def get_brands():
    # 🔍 Check cache first
    cache_key = generate_cache_key("brands")
    cached_brands = await get_cached_data(cache_key)
    if cached_brands:
        print(f"📦 Cache HIT for brands")
        return cached_brands

    print(f"🔄 Cache MISS for brands - querying database")

    brands = await products_collection.distinct("brand")
    brands_data = {"brands": sorted(brands)}

    # 💾 Cache the result
    await set_cached_data(cache_key, brands_data, CACHE_TTL["brands"])

    return brands_data

@app.get("/categories")
async def get_categories():
    # 🔍 Check cache first
    cache_key = generate_cache_key("categories")
    cached_categories = await get_cached_data(cache_key)
    if cached_categories:
        print(f"📦 Cache HIT for categories")
        return cached_categories

    print(f"🔄 Cache MISS for categories - querying database")

    categories = await products_collection.distinct("category")
    categories_data = {"categories": sorted(categories)}

    # 💾 Cache the result
    await set_cached_data(cache_key, categories_data, CACHE_TTL["categories"])

    return categories_data

# Cache management endpoints (optional - for development/debugging)
@app.post("/cache/clear")
async def clear_cache():
    """Clear all cache entries (development only)"""
    await clear_all_cache()
    return {"message": "Cache cleared successfully"}

@app.post("/cache/invalidate/{pattern}")
async def invalidate_cache(pattern: str):
    """Invalidate cache entries matching a pattern (development only)"""
    await invalidate_cache_pattern(f"{pattern}*")
    return {"message": f"Cache entries matching '{pattern}*' invalidated"}

@app.get("/debug/cache-keys")
async def debug_cache_keys():
    """Debug endpoint to see all cache keys (development only)"""
    try:
        keys = await redis_client.keys("*")
        key_data = {}
        for key in keys:
            ttl = await redis_client.ttl(key)
            key_data[key] = {"ttl": ttl}
        return {"cache_keys": key_data}
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug/sneakers-nocache")
async def debug_sneakers_nocache(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    brand: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    featured_only: Optional[bool] = False,
    flash_sale_only: Optional[bool] = False
):
    """Debug endpoint - same as /sneakers but bypasses cache"""
    print(f"🔧 DEBUG: Bypassing cache for sneakers query")

    # Build base filter for products
    match_filter = {}

    if brand:
        match_filter["brand"] = {"$regex": brand, "$options": "i"}
    if category:
        match_filter["category"] = {"$regex": category, "$options": "i"}
    if search:
        match_filter["name"] = {"$regex": search, "$options": "i"}
    if featured_only:
        match_filter["is_featured"] = True

    print(f"🔍 Match filter: {match_filter}")

    # Build the aggregation pipeline
    pipeline = [
        {"$match": match_filter},
        {"$limit": 100},  # Limit to first 1000 products for performance
        {
            "$lookup": {
                "from": "skus",
                "localField": "product_id",
                "foreignField": "product_id",
                "as": "variants"
            }
        },
        {
            "$addFields": {
                "total_stock": {"$sum": "$variants.stock_available"},
                "min_price": {"$min": "$variants.price"},
                "variant_count": {"$size": "$variants"}
            }
        }
    ]

    # Add variant-level filters if needed
    variant_filters = []
    if min_price is not None or max_price is not None or flash_sale_only:
        variant_match = {}
        if min_price is not None:
            variant_match["price"] = {"$gte": min_price}
        if max_price is not None:
            variant_match.setdefault("price", {})["$lte"] = max_price
        if flash_sale_only:
            variant_match["is_flash_sale"] = True
            variant_match["flash_sale_end"] = {"$gt": datetime.now()}

        # Filter variants and recalculate aggregated fields
        pipeline.extend([
            {
                "$addFields": {
                    "filtered_variants": {
                        "$filter": {
                            "input": "$variants",
                            "cond": {
                                "$and": [
                                    {"$gt": ["$this.stock_available", 0]},
                                    *[{f"${op}": [f"$this.{field}", value]}
                                      for field, condition in variant_match.items()
                                      for op, value in (condition.items() if isinstance(condition, dict) else [("eq", condition)])]
                                ]
                            }
                        }
                    }
                }
            },
            {
                "$match": {
                    "filtered_variants": {"$ne": []}
                }
            },
            {
                "$addFields": {
                    "variants": "$filtered_variants",
                    "total_stock": {"$sum": "$filtered_variants.stock_available"},
                    "min_price": {"$min": "$filtered_variants.price"},
                    "variant_count": {"$size": "$filtered_variants"}
                }
            }
        ])
    else:
        # Just filter out variants with no stock
        pipeline.extend([
            {
                "$addFields": {
                    "variants": {
                        "$filter": {
                            "input": "$variants",
                            "cond": {"$gt": ["$this.stock_available", 0]}
                        }
                    }
                }
            },
            {
                "$match": {
                    "variants": {"$ne": []}
                }
            },
            {
                "$addFields": {
                    "total_stock": {"$sum": "$variants.stock_available"},
                    "min_price": {"$min": "$variants.price"},
                    "variant_count": {"$size": "$variants"}
                }
            }
        ])

    # Get total count for pagination
    count_pipeline = pipeline + [{"$count": "total"}]
    count_result = await products_collection.aggregate(count_pipeline).to_list(length=1)
    total = count_result[0]["total"] if count_result else 0

    print(f"📊 Total products found: {total}")

    # Add pagination and sorting
    skip = (page - 1) * per_page
    total_pages = (total + per_page - 1) // per_page

    paginated_pipeline = pipeline + [
        {"$sort": {"min_price": 1, "name": 1}},
        {"$skip": skip},
        {"$limit": per_page}
    ]

    # Execute the aggregation
    cursor = products_collection.aggregate(paginated_pipeline)
    results = await cursor.to_list(length=per_page)

    print(f"📦 Products returned: {len(results)}")

    # Convert to legacy Sneaker format
    sneakers = []
    for product in results:
        # Get representative variant (lowest price)
        representative_variant = min(product["variants"], key=lambda x: x["price"]) if product["variants"] else None

        if not representative_variant:
            continue

        # Extract all unique sizes and colors
        all_sizes = sorted(list(set(variant["size"] for variant in product["variants"])))
        all_colors = list(set(variant["color_name"] for variant in product["variants"]))

        sneaker = {
            "id": str(product["_id"]),
            "sku": representative_variant["sku"],
            "name": product["name"],
            "brand": product["brand"],
            "price": product["min_price"],
            "sale_price": representative_variant.get("sale_price"),
            "description": product["description"],
            "category": product["category"],
            "sizes": all_sizes,
            "colors": all_colors,
            "image_url": product["images"]["main"],
            "stock_quantity": product["total_stock"],
            "rating": product["rating"],
            "reviews_count": product["reviews_count"],
            "is_featured": product["is_featured"],
            "is_flash_sale": representative_variant["is_flash_sale"],
            "flash_sale_end": representative_variant.get("flash_sale_end"),
            "created_at": product["created_at"]
        }
        sneakers.append(sneaker)

    # 📦 Prepare response data
    response_data = {
        "sneakers": sneakers,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages
    }

    return response_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)