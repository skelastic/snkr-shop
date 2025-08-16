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

def generate_product_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

# Database stats endpoint
@app.get("/stats")
async def get_database_stats():
    products_count = await products_collection.count_documents({})
    skus_count = await skus_collection.count_documents({})
    available_skus_count = await skus_collection.count_documents({"stock_available": {"$gt": 0}})

    brands = await products_collection.distinct("brand")
    categories = await products_collection.distinct("category")

    return {
        "products_count": products_count,
        "skus_count": skus_count,
        "available_skus_count": available_skus_count,
        "brands_count": len(brands),
        "categories_count": len(categories),
        "brands": sorted(brands),
        "categories": sorted(categories)
    }

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
        {"$limit": 200},
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
    """
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
    """
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

    return SneakerResponse(
        sneakers=sneakers,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )

@app.get("/sneakers/{sneaker_id}", response_model=Sneaker)
async def get_sneaker(sneaker_id: str):
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

        sneaker = {
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
        return sneaker
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid sneaker ID: {str(e)}")

@app.get("/flash-sales")
async def get_flash_sales():
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

    return {"flash_sales": sneakers}

@app.get("/featured")
async def get_featured_sneakers():
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

    return {"featured": sneakers}

@app.get("/sneakers/{sneaker_id}/variants")
async def get_sneaker_variants(sneaker_id: str):
    """Get all available size/color variants for a specific product"""
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
            return {"variants": []}

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

        return {
            "product_id": str(product["_id"]),
            "product_name": product["name"],
            "variants": variants
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid product ID: {str(e)}")

@app.get("/brands")
async def get_brands():
    brands = await products_collection.distinct("brand")
    return {"brands": sorted(brands)}

@app.get("/categories")
async def get_categories():
    categories = await products_collection.distinct("category")
    return {"categories": sorted(categories)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)