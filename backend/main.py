from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import os
import asyncio
import random
import string
import redis.asyncio as redis
import json
import hashlib
import uuid
from sqlalchemy.sql import func, and_, or_
from sqlalchemy.orm import joinedload

app = FastAPI(title="Sneaker Store API", version="1.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PostgreSQL connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin@localhost:5432/sneaker_store")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    brand = Column(String(100), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    base_price = Column(Float, nullable=False)
    images = Column(JSON)  # Store as JSON: {"main": "url", "gallery": ["url1", "url2"]}
    release_date = Column(DateTime, nullable=False)
    materials = Column(ARRAY(String))  # PostgreSQL array of strings
    technology = Column(ARRAY(String))  # PostgreSQL array of strings
    available_sizes = Column(ARRAY(Float))  # PostgreSQL array of floats
    available_colors = Column(ARRAY(String))  # PostgreSQL array of strings
    is_featured = Column(Boolean, default=False, index=True)
    rating = Column(Float, default=0.0)
    reviews_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationship
    skus = relationship("SKU", back_populates="product")

    # Indexes for performance
    __table_args__ = (
        Index('idx_product_brand_category', 'brand', 'category'),
        Index('idx_product_featured_brand', 'is_featured', 'brand'),
        Index('idx_product_name_search', 'name'),
    )

class SKU(Base):
    __tablename__ = "skus"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    product_id = Column(String(20), ForeignKey('products.product_id'), nullable=False, index=True)
    size = Column(Float, nullable=False)
    color_code = Column(String(10), nullable=False)
    color_name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False, index=True)
    sale_price = Column(Float, nullable=True)
    stock_quantity = Column(Integer, nullable=False, default=0)
    stock_reserved = Column(Integer, nullable=False, default=0)
    stock_available = Column(Integer, nullable=False, default=0, index=True)
    weight = Column(Float)
    dimensions = Column(JSON)  # Store as JSON: {"length": 28.3, "width": 12.3, "height": 10.7}
    barcode = Column(String(50))
    supplier_code = Column(String(50))
    warehouse_location = Column(String(50))
    is_flash_sale = Column(Boolean, default=False, index=True)
    flash_sale_end = Column(DateTime, nullable=True)

    # Denormalized fields for performance
    brand = Column(String(100), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    product_name = Column(String(255), nullable=False)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationship
    product = relationship("Product", back_populates="skus")

    # Indexes for performance
    __table_args__ = (
        Index('idx_sku_product_stock', 'product_id', 'stock_available'),
        Index('idx_sku_flash_sale', 'is_flash_sale', 'flash_sale_end'),
        Index('idx_sku_price_stock', 'price', 'stock_available'),
        Index('idx_sku_brand_category_stock', 'brand', 'category', 'stock_available'),
    )

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())

class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    items = Column(JSON)  # Store cart items as JSON
    total_amount = Column(Float, nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=func.now())

# Create tables
Base.metadata.create_all(bind=engine)

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

# Pydantic models for API responses
class ProductResponse(BaseModel):
    id: str
    product_id: str
    name: str
    brand: str
    category: str
    description: str
    base_price: float
    images: Dict[str, Any]
    release_date: datetime
    materials: List[str]
    technology: List[str]
    available_sizes: List[float]
    available_colors: List[str]
    is_featured: bool = False
    rating: float
    reviews_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SKUResponse(BaseModel):
    id: str
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
    dimensions: Dict[str, Any]
    barcode: str
    supplier_code: str
    warehouse_location: str
    is_flash_sale: bool = False
    flash_sale_end: Optional[datetime] = None
    brand: str
    category: str
    product_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Sneaker(BaseModel):
    """Legacy model for backward compatibility - combines Product + SKU data"""
    id: str
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
    created_at: datetime

class SneakerResponse(BaseModel):
    sneakers: List[Sneaker]
    total: int
    page: int
    per_page: int
    total_pages: int

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True

class CartItem(BaseModel):
    sneaker_id: str
    size: float
    quantity: int

class OrderResponse(BaseModel):
    id: str
    user_id: str
    items: List[CartItem]
    total_amount: float
    status: str = "pending"
    created_at: datetime

    class Config:
        from_attributes = True

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper functions
def generate_sku():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def generate_product_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

# Cache utility functions
def generate_cache_key(prefix: str, **kwargs) -> str:
    """Generate a consistent cache key from parameters"""
    filtered_params = {}
    for k, v in kwargs.items():
        if v is not None:
            if isinstance(v, bool):
                filtered_params[k] = str(v).lower()
            else:
                filtered_params[k] = str(v)

    sorted_params = sorted(filtered_params.items())
    param_string = "&".join([f"{k}={v}" for k, v in sorted_params])

    if param_string:
        param_hash = hashlib.md5(param_string.encode()).hexdigest()[:8]
        return f"{prefix}:{param_hash}"
    return prefix

def get_sneakers_cache_key(
    page: int = 1,
    per_page: int = 20,
    brand: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    featured_only: Optional[bool] = False,
    flash_sale_only: Optional[bool] = False
) -> str:
    """Generate a consistent cache key for sneakers endpoint"""
    return generate_cache_key(
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

async def get_cached_data(cache_key: str):
    """Get data from Redis cache"""
    try:
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            print(f"🔥 Found cached data for key: {cache_key}")
            return json.loads(cached_data)
        else:
            print(f"🚫 No cached data found for key: {cache_key}")
        return None
    except Exception as e:
        print(f"⚠ Cache get error for key {cache_key}: {e}")
        return None

async def set_cached_data(cache_key: str, data: dict, ttl: int):
    """Set data in Redis cache with TTL"""
    try:
        def json_encoder(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, uuid.UUID):
                return str(obj)
            return str(obj)

        json_data = json.dumps(data, default=json_encoder)
        await redis_client.setex(cache_key, ttl, json_data)
        print(f"💾 Cached data for key: {cache_key} (TTL: {ttl}s)")
    except Exception as e:
        print(f"⚠ Cache set error for key {cache_key}: {e}")

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
        print(f"⚠ Error closing Redis connection: {e}")

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Sneaker Store API is running!"}

@app.get("/stats")
async def get_database_stats(db: Session = Depends(get_db)):
    # 🔍 Check cache first
    cache_key = generate_cache_key("stats")
    cached_stats = await get_cached_data(cache_key)
    if cached_stats:
        print(f"📦 Cache HIT for stats")
        return cached_stats

    print(f"📄 Cache MISS for stats - querying database")

    products_count = db.query(Product).count()
    skus_count = db.query(SKU).count()
    available_skus_count = db.query(SKU).filter(SKU.stock_available > 0).count()

    brands = db.query(Product.brand).distinct().all()
    categories = db.query(Product.category).distinct().all()

    stats_data = {
        "products_count": products_count,
        "skus_count": skus_count,
        "available_skus_count": available_skus_count,
        "brands_count": len(brands),
        "categories_count": len(categories),
        "brands": sorted([brand[0] for brand in brands]),
        "categories": sorted([category[0] for category in categories])
    }

    # 💾 Cache the result
    await set_cached_data(cache_key, stats_data, CACHE_TTL["stats"])

    return stats_data

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
    flash_sale_only: Optional[bool] = False,
    db: Session = Depends(get_db)
):
    # 🔍 Generate consistent cache key
    cache_key = get_sneakers_cache_key(
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

    print(f"📄 Cache MISS for sneakers query: {cache_key} - querying database")

    # Build base query
    query = db.query(Product).join(SKU, Product.product_id == SKU.product_id)

    # Apply filters
    if brand:
        query = query.filter(Product.brand.ilike(f"%{brand}%"))
    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    if featured_only:
        query = query.filter(Product.is_featured == True)
    if min_price is not None:
        query = query.filter(SKU.price >= min_price)
    if max_price is not None:
        query = query.filter(SKU.price <= max_price)
    if flash_sale_only:
        query = query.filter(
            and_(
                SKU.is_flash_sale == True,
                SKU.flash_sale_end > func.now()
            )
        )

    # Filter only products with available stock
    query = query.filter(SKU.stock_available > 0)

    # Group by product to avoid duplicates and get distinct products
    query = query.distinct(Product.id)

    # Get total count for pagination
    total = query.count()

    # Apply pagination
    skip = (page - 1) * per_page
    total_pages = (total + per_page - 1) // per_page

    # Get products with their SKUs
    products = query.offset(skip).limit(per_page).all()

    # Convert to legacy Sneaker format
    sneakers = []
    for product in products:
        # Get all available SKUs for this product
        available_skus = db.query(SKU).filter(
            and_(
                SKU.product_id == product.product_id,
                SKU.stock_available > 0
            )
        ).all()

        if not available_skus:
            continue

        # Apply additional filters to SKUs if needed
        filtered_skus = available_skus
        if min_price is not None:
            filtered_skus = [sku for sku in filtered_skus if sku.price >= min_price]
        if max_price is not None:
            filtered_skus = [sku for sku in filtered_skus if sku.price <= max_price]
        if flash_sale_only:
            current_time = datetime.now()
            filtered_skus = [sku for sku in filtered_skus
                           if sku.is_flash_sale and sku.flash_sale_end and sku.flash_sale_end > current_time]

        if not filtered_skus:
            continue

        # Get representative SKU (lowest price)
        representative_sku = min(filtered_skus, key=lambda x: x.price)

        # Aggregate data
        all_sizes = sorted(list(set(sku.size for sku in filtered_skus)))
        all_colors = list(set(sku.color_name for sku in filtered_skus))
        total_stock = sum(sku.stock_available for sku in filtered_skus)
        min_price_val = min(sku.price for sku in filtered_skus)

        # Handle images - check if it's a dict or list/other format
        image_url = ""
        if product.images:
            if isinstance(product.images, dict):
                image_url = product.images.get("main", "")
            elif isinstance(product.images, list) and len(product.images) > 0:
                image_url = product.images[0]  # Use first image if it's a list
            elif isinstance(product.images, str):
                image_url = product.images  # Direct string

        sneaker = {
            "id": str(product.id),
            "sku": representative_sku.sku,
            "name": product.name,
            "brand": product.brand,
            "price": min_price_val,
            "sale_price": representative_sku.sale_price,
            "description": product.description,
            "category": product.category,
            "sizes": all_sizes,
            "colors": all_colors,
            "image_url": image_url,
            "stock_quantity": total_stock,
            "rating": product.rating,
            "reviews_count": product.reviews_count,
            "is_featured": product.is_featured,
            "is_flash_sale": representative_sku.is_flash_sale,
            "flash_sale_end": representative_sku.flash_sale_end,
            "created_at": product.created_at
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
async def get_sneaker(sneaker_id: str, db: Session = Depends(get_db)):
    # 🔍 Check cache first
    cache_key = generate_cache_key("sneaker_detail", sneaker_id=sneaker_id)
    cached_sneaker = await get_cached_data(cache_key)
    if cached_sneaker:
        print(f"📦 Cache HIT for sneaker {sneaker_id}")
        return Sneaker(**cached_sneaker)

    print(f"📄 Cache MISS for sneaker {sneaker_id} - querying database")

    try:
        # Try to find by product UUID first
        try:
            product_uuid = uuid.UUID(sneaker_id)
            product = db.query(Product).filter(Product.id == product_uuid).first()
        except ValueError:
            # If not a valid UUID, try to find by SKU ID
            try:
                sku_uuid = uuid.UUID(sneaker_id)
                sku = db.query(SKU).filter(SKU.id == sku_uuid).first()
                if not sku:
                    raise HTTPException(status_code=404, detail="Sneaker not found")
                product = db.query(Product).filter(Product.product_id == sku.product_id).first()
            except ValueError:
                raise HTTPException(status_code=404, detail="Invalid sneaker ID format")

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Get all available SKUs for this product
        skus = db.query(SKU).filter(
            and_(
                SKU.product_id == product.product_id,
                SKU.stock_available > 0
            )
        ).all()

        if not skus:
            raise HTTPException(status_code=404, detail="No available variants found")

        # Get the representative SKU (lowest price)
        representative_sku = min(skus, key=lambda x: x.price)

        # Aggregate data
        all_sizes = sorted(list(set(sku.size for sku in skus)))
        all_colors = list(set(sku.color_name for sku in skus))
        total_stock = sum(sku.stock_available for sku in skus)
        min_price = min(sku.price for sku in skus)

        # Handle images safely
        image_url = ""
        if product.images:
            if isinstance(product.images, dict):
                image_url = product.images.get("main", "")
            elif isinstance(product.images, list) and len(product.images) > 0:
                image_url = product.images[0]
            elif isinstance(product.images, str):
                image_url = product.images

        sneaker_data = {
            "id": str(product.id),
            "sku": representative_sku.sku,
            "name": product.name,
            "brand": product.brand,
            "price": min_price,
            "sale_price": representative_sku.sale_price,
            "description": product.description,
            "category": product.category,
            "sizes": all_sizes,
            "colors": all_colors,
            "image_url": image_url,
            "stock_quantity": total_stock,
            "rating": product.rating,
            "reviews_count": product.reviews_count,
            "is_featured": product.is_featured,
            "is_flash_sale": representative_sku.is_flash_sale,
            "flash_sale_end": representative_sku.flash_sale_end,
            "created_at": product.created_at
        }

        # 💾 Cache the result
        await set_cached_data(cache_key, sneaker_data, CACHE_TTL["sneaker_detail"])

        return Sneaker(**sneaker_data)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=f"Invalid sneaker ID: {str(e)}")

@app.get("/flash-sales")
async def get_flash_sales(db: Session = Depends(get_db)):
    # 🔍 Check cache first
    cache_key = generate_cache_key("flash_sales")
    cached_flash_sales = await get_cached_data(cache_key)
    if cached_flash_sales:
        print(f"📦 Cache HIT for flash sales")
        return cached_flash_sales

    print(f"📄 Cache MISS for flash sales - querying database")

    current_time = datetime.now()

    # Get products with flash sale SKUs
    flash_sale_skus = db.query(SKU).join(Product, SKU.product_id == Product.product_id).filter(
        and_(
            SKU.is_flash_sale == True,
            SKU.flash_sale_end > current_time,
            SKU.stock_available > 0
        )
    ).limit(10).all()

    # Group by product
    products_dict = {}
    for sku in flash_sale_skus:
        if sku.product_id not in products_dict:
            products_dict[sku.product_id] = {
                'product': sku.product,
                'skus': [],
                'representative_sku': sku
            }
        products_dict[sku.product_id]['skus'].append(sku)

        # Update representative SKU if this one is cheaper
        if sku.price < products_dict[sku.product_id]['representative_sku'].price:
            products_dict[sku.product_id]['representative_sku'] = sku

    sneakers = []
    for product_data in products_dict.values():
        product = product_data['product']
        skus = product_data['skus']
        representative_sku = product_data['representative_sku']

        all_sizes = sorted(list(set(sku.size for sku in skus)))
        all_colors = list(set(sku.color_name for sku in skus))
        total_stock = sum(sku.stock_available for sku in skus)

        # Handle images safely
        image_url = ""
        if product.images:
            if isinstance(product.images, dict):
                image_url = product.images.get("main", "")
            elif isinstance(product.images, list) and len(product.images) > 0:
                image_url = product.images[0]
            elif isinstance(product.images, str):
                image_url = product.images

        sneaker = {
            "id": str(product.id),
            "sku": representative_sku.sku,
            "name": product.name,
            "brand": product.brand,
            "price": representative_sku.price,
            "sale_price": representative_sku.sale_price,
            "description": product.description,
            "category": product.category,
            "sizes": all_sizes,
            "colors": all_colors,
            "image_url": image_url,
            "stock_quantity": total_stock,
            "rating": product.rating,
            "reviews_count": product.reviews_count,
            "is_featured": product.is_featured,
            "is_flash_sale": representative_sku.is_flash_sale,
            "flash_sale_end": representative_sku.flash_sale_end,
            "created_at": product.created_at
        }
        sneakers.append(sneaker)

    flash_sales_data = {"flash_sales": sneakers}

    # 💾 Cache the result
    await set_cached_data(cache_key, flash_sales_data, CACHE_TTL["flash_sales"])

    return flash_sales_data

@app.get("/featured")
async def get_featured_sneakers(db: Session = Depends(get_db)):
    # 🔍 Check cache first
    cache_key = generate_cache_key("featured")
    cached_featured = await get_cached_data(cache_key)
    if cached_featured:
        print(f"📦 Cache HIT for featured sneakers")
        return cached_featured

    print(f"📄 Cache MISS for featured sneakers - querying database")

    # Get featured products with their cheapest available SKUs
    featured_products = db.query(Product).filter(Product.is_featured == True).limit(8).all()

    sneakers = []
    for product in featured_products:
        # Get available SKUs for this product
        available_skus = db.query(SKU).filter(
            and_(
                SKU.product_id == product.product_id,
                SKU.stock_available > 0
            )
        ).all()

        if not available_skus:
            continue

        # Get representative SKU (lowest price)
        representative_sku = min(available_skus, key=lambda x: x.price)

        all_sizes = sorted(list(set(sku.size for sku in available_skus)))
        all_colors = list(set(sku.color_name for sku in available_skus))
        total_stock = sum(sku.stock_available for sku in available_skus)

        # Handle images safely
        image_url = ""
        if product.images:
            if isinstance(product.images, dict):
                image_url = product.images.get("main", "")
            elif isinstance(product.images, list) and len(product.images) > 0:
                image_url = product.images[0]
            elif isinstance(product.images, str):
                image_url = product.images

        sneaker = {
            "id": str(product.id),
            "sku": representative_sku.sku,
            "name": product.name,
            "brand": product.brand,
            "price": representative_sku.price,
            "sale_price": representative_sku.sale_price,
            "description": product.description,
            "category": product.category,
            "sizes": all_sizes,
            "colors": all_colors,
            "image_url": image_url,
            "stock_quantity": total_stock,
            "rating": product.rating,
            "reviews_count": product.reviews_count,
            "is_featured": product.is_featured,
            "is_flash_sale": representative_sku.is_flash_sale,
            "flash_sale_end": representative_sku.flash_sale_end,
            "created_at": product.created_at
        }
        sneakers.append(sneaker)

    featured_data = {"featured": sneakers}

    # 💾 Cache the result
    await set_cached_data(cache_key, featured_data, CACHE_TTL["featured"])

    return featured_data

@app.get("/sneakers/{sneaker_id}/variants")
async def get_sneaker_variants(sneaker_id: str, db: Session = Depends(get_db)):
    """Get all available size/color variants for a specific product"""
    # 🔍 Check cache first
    cache_key = generate_cache_key("variants", sneaker_id=sneaker_id)
    cached_variants = await get_cached_data(cache_key)
    if cached_variants:
        print(f"📦 Cache HIT for variants {sneaker_id}")
        return cached_variants

    print(f"📄 Cache MISS for variants {sneaker_id} - querying database")

    try:
        # Get the product first
        try:
            product_uuid = uuid.UUID(sneaker_id)
            product = db.query(Product).filter(Product.id == product_uuid).first()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid product ID format")

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Get all SKUs for this product
        skus = db.query(SKU).filter(
            and_(
                SKU.product_id == product.product_id,
                SKU.stock_available > 0
            )
        ).order_by(SKU.price).all()

        if not skus:
            variants_data = {"variants": []}
        else:
            variants = []
            for sku in skus:
                variant = {
                    "sku_id": str(sku.id),
                    "sku": sku.sku,
                    "size": sku.size,
                    "color_name": sku.color_name,
                    "color_code": sku.color_code,
                    "price": sku.price,
                    "sale_price": sku.sale_price,
                    "stock_available": sku.stock_available,
                    "is_flash_sale": sku.is_flash_sale,
                    "flash_sale_end": sku.flash_sale_end
                }
                variants.append(variant)

            variants_data = {
                "product_id": str(product.id),
                "product_name": product.name,
                "variants": variants
            }

        # 💾 Cache the result
        await set_cached_data(cache_key, variants_data, CACHE_TTL["variants"])

        return variants_data

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=f"Invalid product ID: {str(e)}")

@app.get("/brands")
async def get_brands(db: Session = Depends(get_db)):
    # 🔍 Check cache first
    cache_key = generate_cache_key("brands")
    cached_brands = await get_cached_data(cache_key)
    if cached_brands:
        print(f"📦 Cache HIT for brands")
        return cached_brands

    print(f"📄 Cache MISS for brands - querying database")

    brands = db.query(Product.brand).distinct().all()
    brands_data = {"brands": sorted([brand[0] for brand in brands])}

    # 💾 Cache the result
    await set_cached_data(cache_key, brands_data, CACHE_TTL["brands"])

    return brands_data

@app.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    # 🔍 Check cache first
    cache_key = generate_cache_key("categories")
    cached_categories = await get_cached_data(cache_key)
    if cached_categories:
        print(f"📦 Cache HIT for categories")
        return cached_categories

    print(f"📄 Cache MISS for categories - querying database")

    categories = db.query(Product.category).distinct().all()
    categories_data = {"categories": sorted([category[0] for category in categories])}

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

@app.get("/debug/warm-cache")
async def debug_warm_cache(db: Session = Depends(get_db)):
    """Debug endpoint to warm up cache with some test data"""
    print("🔥 Warming up cache with test queries...")

    # Warm up cache for common queries
    test_queries = [
        {"page": 1, "per_page": 20},
        {"page": 2, "per_page": 20},
        {"page": 1, "per_page": 20, "brand": "Nike"},
        {"page": 1, "per_page": 20, "featured_only": True},
    ]

    warmed_keys = []
    for query in test_queries:
        cache_key = get_sneakers_cache_key(**query)

        # Check if already cached
        cached = await get_cached_data(cache_key)
        if not cached:
            print(f"📄 Cache warming: {cache_key} with query {query}")
            # Make the actual query to populate cache
            try:
                # Call the sneakers endpoint directly with these params
                response = await get_sneakers(db=db, **query)
                warmed_keys.append(cache_key)
                print(f"✅ Warmed cache key: {cache_key}")
            except Exception as e:
                print(f"⚠ Failed to warm cache key {cache_key}: {e}")
        else:
            print(f"♻️ Cache key already exists: {cache_key}")

    return {
        "message": "Cache warming completed",
        "warmed_keys": warmed_keys,
        "test_queries": test_queries
    }

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
    flash_sale_only: Optional[bool] = False,
    db: Session = Depends(get_db)
):
    """Debug endpoint - same as /sneakers but bypasses cache"""
    print(f"🔧 DEBUG: Bypassing cache for sneakers query")

    # Build base query
    query = db.query(Product).join(SKU, Product.product_id == SKU.product_id)

    # Apply filters
    if brand:
        query = query.filter(Product.brand.ilike(f"%{brand}%"))
    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    if featured_only:
        query = query.filter(Product.is_featured == True)
    if min_price is not None:
        query = query.filter(SKU.price >= min_price)
    if max_price is not None:
        query = query.filter(SKU.price <= max_price)
    if flash_sale_only:
        query = query.filter(
            and_(
                SKU.is_flash_sale == True,
                SKU.flash_sale_end > func.now()
            )
        )

    # Filter only products with available stock
    query = query.filter(SKU.stock_available > 0)

    # Group by product to avoid duplicates and get distinct products
    query = query.distinct(Product.id)

    print(f"🔍 Query filters applied")

    # Get total count for pagination
    total = query.count()
    print(f"📊 Total products found: {total}")

    # Apply pagination
    skip = (page - 1) * per_page
    total_pages = (total + per_page - 1) // per_page

    # Get products with their SKUs
    products = query.offset(skip).limit(per_page).all()
    print(f"📦 Products returned: {len(products)}")

    # Convert to legacy Sneaker format
    sneakers = []
    for product in products:
        # Get all available SKUs for this product
        available_skus = db.query(SKU).filter(
            and_(
                SKU.product_id == product.product_id,
                SKU.stock_available > 0
            )
        ).all()

        if not available_skus:
            continue

        # Apply additional filters to SKUs if needed
        filtered_skus = available_skus
        if min_price is not None:
            filtered_skus = [sku for sku in filtered_skus if sku.price >= min_price]
        if max_price is not None:
            filtered_skus = [sku for sku in filtered_skus if sku.price <= max_price]
        if flash_sale_only:
            current_time = datetime.now()
            filtered_skus = [sku for sku in filtered_skus
                           if sku.is_flash_sale and sku.flash_sale_end and sku.flash_sale_end > current_time]

        if not filtered_skus:
            continue

        # Get representative SKU (lowest price)
        representative_sku = min(filtered_skus, key=lambda x: x.price)

        # Aggregate data
        all_sizes = sorted(list(set(sku.size for sku in filtered_skus)))
        all_colors = list(set(sku.color_name for sku in filtered_skus))
        total_stock = sum(sku.stock_available for sku in filtered_skus)
        min_price_val = min(sku.price for sku in filtered_skus)

        # Handle images safely
        image_url = ""
        if product.images:
            if isinstance(product.images, dict):
                image_url = product.images.get("main", "")
            elif isinstance(product.images, list) and len(product.images) > 0:
                image_url = product.images[0]
            elif isinstance(product.images, str):
                image_url = product.images

        sneaker = {
            "id": str(product.id),
            "sku": representative_sku.sku,
            "name": product.name,
            "brand": product.brand,
            "price": min_price_val,
            "sale_price": representative_sku.sale_price,
            "description": product.description,
            "category": product.category,
            "sizes": all_sizes,
            "colors": all_colors,
            "image_url": image_url,
            "stock_quantity": total_stock,
            "rating": product.rating,
            "reviews_count": product.reviews_count,
            "is_featured": product.is_featured,
            "is_flash_sale": representative_sku.is_flash_sale,
            "flash_sale_end": representative_sku.flash_sale_end,
            "created_at": product.created_at
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