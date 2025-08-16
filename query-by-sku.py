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

# Database initialization and population
@app.on_event("startup")
async def startup_event():
    # Create indexes for better performance
    await sneakers_collection.create_index([("brand", 1), ("category", 1)])
    await sneakers_collection.create_index([("price", 1)])
    await sneakers_collection.create_index([("is_featured", 1)])
    await sneakers_collection.create_index([("is_flash_sale", 1)])
    await sneakers_collection.create_index([("name", "text"), ("description", "text")])

# Data population endpoint (run once to populate database)
@app.post("/populate-data")
async def populate_sneakers():
    existing_count = await sneakers_collection.count_documents({})
    if existing_count >= 1000:  # Reduced for demo purposes
        return {"message": f"Database already has {existing_count} sneakers"}

    brands = ["Nike", "Adidas", "Jordan", "Puma", "New Balance", "Converse", "Vans", "Reebok"]
    categories = ["Running", "Basketball", "Lifestyle", "Training", "Skateboarding", "Tennis"]
    colors = ["Black", "White", "Red", "Blue", "Green", "Gray", "Brown", "Pink", "Yellow", "Purple"]

    sneakers_to_insert = []

    # Generate 1000 sneakers for demo (you can increase this number)
    for i in range(1000):
        brand = random.choice(brands)
        category = random.choice(categories)

        # Flash sale logic - 10% of sneakers are on flash sale
        is_flash_sale = random.random() < 0.1
        flash_sale_end = None
        sale_price = None

        base_price = round(random.uniform(60, 300), 2)

        if is_flash_sale:
            flash_sale_end = datetime.now() + timedelta(hours=random.randint(1, 72))
            sale_price = round(base_price * random.uniform(0.6, 0.8), 2)

        sneaker = {
            "sku": generate_sku(),
            "name": f"{brand} {category} {random.choice(['Pro', 'Elite', 'Max', 'Air', 'Ultra', 'Boost'])}-{i+1}",
            "brand": brand,
            "price": base_price,
            "sale_price": sale_price,
            "description": f"Premium {category.lower()} sneaker from {brand} featuring cutting-edge technology and superior comfort.",
            "category": category,
            "sizes": [size/2 for size in range(12, 32)],  # US sizes 6-16
            "colors": random.sample(colors, random.randint(1, 3)),
            "image_url": f"https://picsum.photos/400/400?random={i+1}",
            "stock_quantity": random.randint(0, 100),
            "rating": round(random.uniform(3.0, 5.0), 1),
            "reviews_count": random.randint(10, 500),
            "is_featured": random.random() < 0.2,  # 20% are featured
            "is_flash_sale": is_flash_sale,
            "flash_sale_end": flash_sale_end,
            "created_at": datetime.now()
        }
        sneakers_to_insert.append(sneaker)

    await sneakers_collection.insert_many(sneakers_to_insert)
    return {"message": f"Successfully populated {len(sneakers_to_insert)} sneakers"}

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
    # Build filter query for products collection first
    product_filter = {}

    if brand:
        product_filter["brand"] = {"$regex": brand, "$options": "i"}
    if category:
        product_filter["category"] = {"$regex": category, "$options": "i"}
    if search:
        product_filter["name"] = {"$regex": search, "$options": "i"}
    if featured_only:
        product_filter["is_featured"] = True

    # Get matching products first
    products_cursor = products_collection.find(product_filter)
    products = await products_cursor.to_list(length=None)

    if not products:
        return SneakerResponse(sneakers=[], total=0, page=page, per_page=per_page, total_pages=0)

    product_ids = [product["product_id"] for product in products]

    # Build SKU filter based on product matches and additional filters
    sku_filter = {
        "product_id": {"$in": product_ids},
        "stock_available": {"$gt": 0}
    }

    if min_price is not None:
        sku_filter["price"] = {"$gte": min_price}
    if max_price is not None:
        sku_filter.setdefault("price", {})["$lte"] = max_price
    if flash_sale_only:
        sku_filter["is_flash_sale"] = True
        sku_filter["flash_sale_end"] = {"$gt": datetime.now()}

    # Aggregate to get one representative SKU per product
    pipeline = [
        {"$match": sku_filter},
        # Group by product_id and get the first SKU (could be modified to get best price, etc.)
        {"$sort": {"price": 1}},  # Sort by price to get cheapest variant first
        {"$group": {
            "_id": "$product_id",
            "representative_sku": {"$first": "$ROOT"}
        }},
        # Lookup product information
        {"$lookup": {
            "from": "products",
            "localField": "_id",
            "foreignField": "product_id",
            "as": "product_info"
        }},
        {"$unwind": "$product_info"},
        # Add computed fields
        {"$addFields": {
            "representative_sku.all_sizes": "$product_info.available_sizes",
            "representative_sku.all_colors": "$product_info.available_colors",
            "representative_sku.description": "$product_info.description",
            "representative_sku.rating": "$product_info.rating",
            "representative_sku.reviews_count": "$product_info.reviews_count",
            "representative_sku.is_featured": "$product_info.is_featured",
            "representative_sku.images": "$product_info.images"
        }}
    ]

    # Get total count before pagination
    total_pipeline = pipeline + [{"$count": "total"}]
    total_result = await skus_collection.aggregate(total_pipeline).to_list(length=1)
    total = total_result[0]["total"] if total_result else 0

    # Add pagination
    skip = (page - 1) * per_page
    total_pages = (total + per_page - 1) // per_page

    paginated_pipeline = pipeline + [
        {"$skip": skip},
        {"$limit": per_page}
    ]

    cursor = skus_collection.aggregate(paginated_pipeline)
    results = await cursor.to_list(length=per_page)

    # Convert to legacy Sneaker format for frontend compatibility
    sneakers = []
    for item in results:
        sku = item["representative_sku"]

        sneaker = {
            "id": str(sku["_id"]),
            "product_id": sku["product_id"],  # Add product_id for detail page navigation
            "sku": sku["sku"],
            "name": sku["product_name"],
            "brand": sku["brand"],
            "price": sku["price"],
            "sale_price": sku.get("sale_price"),
            "description": sku["description"],
            "category": sku["category"],
            "sizes": sku["all_sizes"],  # All available sizes for this product
            "colors": sku["all_colors"],  # All available colors for this product
            "image_url": sku["images"]["main"],
            "stock_quantity": sku["stock_available"],
            "rating": sku["rating"],
            "reviews_count": sku["reviews_count"],
            "is_featured": sku["is_featured"],
            "is_flash_sale": sku["is_flash_sale"],
            "flash_sale_end": sku.get("flash_sale_end"),
            "created_at": sku["created_at"]
        }
        sneakers.append(sneaker)

    return SneakerResponse(
        sneakers=sneakers,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )

@app.get("/products/{product_id}")
async def get_product_details(product_id: str):
    try:
        # Get product information
        product = await products_collection.find_one({"product_id": product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Get all SKUs for this product
        skus_cursor = skus_collection.find({"product_id": product_id})
        skus = await skus_cursor.to_list(length=None)

        if not skus:
            raise HTTPException(status_code=404, detail="No variants found for this product")

        # Organize SKUs by size and color for easier frontend handling
        variants = []
        for sku in skus:
            variant = {
                "id": str(sku["_id"]),
                "sku": sku["sku"],
                "size": sku["size"],
                "color_code": sku["color_code"],
                "color_name": sku["color_name"],
                "price": sku["price"],
                "sale_price": sku.get("sale_price"),
                "stock_quantity": sku["stock_quantity"],
                "stock_available": sku["stock_available"],
                "is_flash_sale": sku["is_flash_sale"],
                "flash_sale_end": sku.get("flash_sale_end"),
                "weight": sku["weight"],
                "dimensions": sku["dimensions"],
                "barcode": sku["barcode"]
            }
            variants.append(variant)

        # Get unique sizes and colors for filtering
        available_sizes = sorted(list(set([sku["size"] for sku in skus if sku["stock_available"] > 0])))
        available_colors = list({sku["color_code"]: sku["color_name"] for sku in skus if sku["stock_available"] > 0}.items())

        # Calculate price range
        prices = [sku["sale_price"] if sku.get("sale_price") else sku["price"] for sku in skus if sku["stock_available"] > 0]
        price_range = {
            "min": min(prices) if prices else 0,
            "max": max(prices) if prices else 0
        }

        # Check if any variant is on flash sale
        has_flash_sale = any(sku["is_flash_sale"] for sku in skus)

        # Prepare response
        product_details = {
            "product_id": product["product_id"],
            "name": product["name"],
            "brand": product["brand"],
            "category": product["category"],
            "description": product["description"],
            "base_price": product["base_price"],
            "price_range": price_range,
            "images": product["images"],
            "materials": product["materials"],
            "technology": product["technology"],
            "available_sizes": available_sizes,
            "available_colors": available_colors,
            "is_featured": product["is_featured"],
            "has_flash_sale": has_flash_sale,
            "rating": product["rating"],
            "reviews_count": product["reviews_count"],
            "release_date": product["release_date"],
            "variants": variants,
            "total_variants": len(variants),
            "available_variants": len([v for v in variants if v["stock_available"] > 0])
        }

        return product_details

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error retrieving product details: {str(e)}")

@app.get("/sneakers/{sneaker_id}")
async def get_sneaker_by_sku_id(sneaker_id: str):
    """Legacy endpoint - gets specific SKU details"""
    try:
        # Get SKU document
        sku = await skus_collection.find_one({"_id": ObjectId(sneaker_id)})
        if not sku:
            raise HTTPException(status_code=404, detail="Sneaker not found")

        # Get related product document
        product = await products_collection.find_one({"product_id": sku["product_id"]})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Convert to legacy format
        sneaker = {
            "id": str(sku["_id"]),
            "product_id": sku["product_id"],
            "sku": sku["sku"],
            "name": product["name"],
            "brand": sku["brand"],
            "price": sku["price"],
            "sale_price": sku.get("sale_price"),
            "description": product["description"],
            "category": sku["category"],
            "sizes": [sku["size"]],
            "colors": [sku["color_name"]],
            "image_url": product["images"]["main"],
            "stock_quantity": sku["stock_available"],
            "rating": product["rating"],
            "reviews_count": product["reviews_count"],
            "is_featured": product["is_featured"],
            "is_flash_sale": sku["is_flash_sale"],
            "flash_sale_end": sku.get("flash_sale_end"),
            "created_at": sku["created_at"]
        }
        return sneaker
    except:
        raise HTTPException(status_code=400, detail="Invalid sneaker ID")

@app.get("/flash-sales")
async def get_flash_sales():
    current_time = datetime.now()
    pipeline = [
        {"$match": {
            "is_flash_sale": True,
            "flash_sale_end": {"$gt": current_time},
            "stock_available": {"$gt": 0}
        }},
        {"$limit": 10},
        {"$lookup": {
            "from": "products",
            "localField": "product_id",
            "foreignField": "product_id",
            "as": "product_info"
        }},
        {"$unwind": "$product_info"}
    ]

    cursor = skus_collection.aggregate(pipeline)
    results = await cursor.to_list(length=10)

    sneakers = []
    for item in results:
        sku = item
        product = item["product_info"]

        sneaker = {
            "id": str(sku["_id"]),
            "sku": sku["sku"],
            "name": product["name"],
            "brand": sku["brand"],
            "price": sku["price"],
            "sale_price": sku.get("sale_price"),
            "description": product["description"],
            "category": sku["category"],
            "sizes": [sku["size"]],
            "colors": [sku["color_name"]],
            "image_url": product["images"]["main"],
            "stock_quantity": sku["stock_available"],
            "rating": product["rating"],
            "reviews_count": product["reviews_count"],
            "is_featured": product["is_featured"],
            "is_flash_sale": sku["is_flash_sale"],
            "flash_sale_end": sku.get("flash_sale_end"),
            "created_at": sku["created_at"]
        }
        sneakers.append(sneaker)

    return {"flash_sales": sneakers}

@app.get("/featured")
async def get_featured_sneakers():
    # Get featured products first
    featured_product_ids = await products_collection.distinct(
        "product_id",
        {"is_featured": True}
    )

    # Get SKUs for featured products
    pipeline = [
        {"$match": {
            "product_id": {"$in": featured_product_ids},
            "stock_available": {"$gt": 0}
        }},
        {"$limit": 8},
        {"$lookup": {
            "from": "products",
            "localField": "product_id",
            "foreignField": "product_id",
            "as": "product_info"
        }},
        {"$unwind": "$product_info"}
    ]

    cursor = skus_collection.aggregate(pipeline)
    results = await cursor.to_list(length=8)

    sneakers = []
    for item in results:
        sku = item
        product = item["product_info"]

        sneaker = {
            "id": str(sku["_id"]),
            "sku": sku["sku"],
            "name": product["name"],
            "brand": sku["brand"],
            "price": sku["price"],
            "sale_price": sku.get("sale_price"),
            "description": product["description"],
            "category": sku["category"],
            "sizes": [sku["size"]],
            "colors": [sku["color_name"]],
            "image_url": product["images"]["main"],
            "stock_quantity": sku["stock_available"],
            "rating": product["rating"],
            "reviews_count": product["reviews_count"],
            "is_featured": product["is_featured"],
            "is_flash_sale": sku["is_flash_sale"],
            "flash_sale_end": sku.get("flash_sale_end"),
            "created_at": sku["created_at"]
        }
        sneakers.append(sneaker)

    return {"featured": sneakers}

@app.get("/brands")
async def get_brands():
    brands = await skus_collection.distinct("brand")
    return {"brands": sorted(brands)}

@app.get("/categories")
async def get_categories():
    categories = await skus_collection.distinct("category")
    return {"categories": sorted(categories)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)