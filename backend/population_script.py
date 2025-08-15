import asyncio
import random
import string
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection
MONGODB_URL = "mongodb://admin:password123@localhost:27017/sneaker_store?authSource=admin"

async def generate_advanced_sneaker_data():
    """Generate large dataset of sneaker products"""
    
    # Extended brand data with real brand characteristics
    brands_data = {
        "Nike": {
            "price_range": (80, 350),
            "categories": ["Running", "Basketball", "Lifestyle", "Training"],
            "signature_models": ["Air Max", "Air Force", "Dunk", "Blazer", "React", "Zoom"]
        },
        "Adidas": {
            "price_range": (70, 300),
            "categories": ["Running", "Basketball", "Lifestyle", "Soccer"],
            "signature_models": ["Ultraboost", "Stan Smith", "Gazelle", "Superstar", "NMD", "Yeezy"]
        },
        "Jordan": {
            "price_range": (120, 500),
            "categories": ["Basketball", "Lifestyle"],
            "signature_models": ["Air Jordan 1", "Air Jordan 3", "Air Jordan 4", "Air Jordan 11", "Air Jordan 12"]
        },
        "New Balance": {
            "price_range": (60, 250),
            "categories": ["Running", "Lifestyle", "Walking"],
            "signature_models": ["990", "574", "327", "2002R", "Fresh Foam"]
        },
        "Puma": {
            "price_range": (50, 200),
            "categories": ["Running", "Lifestyle", "Soccer", "Training"],
            "signature_models": ["Suede", "RS-X", "Cali", "Future Rider", "Clyde"]
        },
        "Converse": {
            "price_range": (40, 120),
            "categories": ["Lifestyle", "Skateboarding"],
            "signature_models": ["Chuck Taylor", "Chuck 70", "One Star", "Jack Purcell"]
        },
        "Vans": {
            "price_range": (45, 150),
            "categories": ["Skateboarding", "Lifestyle"],
            "signature_models": ["Old Skool", "Authentic", "Era", "Slip-On", "Sk8-Hi"]
        },
        "Reebok": {
            "price_range": (55, 180),
            "categories": ["Running", "Training", "Lifestyle"],
            "signature_models": ["Classic Leather", "Club C", "Pump", "Fury", "Question"]
        },
        "ASICS": {
            "price_range": (70, 220),
            "categories": ["Running", "Training", "Lifestyle"],
            "signature_models": ["Gel-Lyte", "Gel-Kayano", "Gel-Nimbus", "Tiger", "Onitsuka"]
        },
        "Under Armour": {
            "price_range": (60, 200),
            "categories": ["Basketball", "Running", "Training"],
            "signature_models": ["Curry", "HOVR", "Charged", "Flow", "Project Rock"]
        }
    }
    
    # Color combinations
    color_combinations = [
        ["Black", "White"], ["White", "Black"], ["Red", "White"], ["Blue", "White"],
        ["Black", "Red"], ["Navy", "White"], ["Gray", "Black"], ["Green", "White"],
        ["Pink", "White"], ["Purple", "Black"], ["Yellow", "Black"], ["Orange", "White"],
        ["Brown", "Tan"], ["Maroon", "Gold"], ["Teal", "White"], ["Lime", "Black"]
    ]
    
    # Technology descriptions
    tech_features = [
        "Air cushioning technology", "Boost energy return", "React foam midsole",
        "Zoom Air units", "Fresh Foam comfort", "Gel cushioning system",
        "HOVR technology", "Charged cushioning", "Cloud technology",
        "FlyteFoam midsole", "DNA LOFT cushioning", "PWRRUN foam"
    ]
    
    # Size availability (US sizes)
    available_sizes = [size/2 for size in range(12, 32)]  # 6.0 to 15.5
    
    return {
        "brands_data": brands_data,
        "color_combinations": color_combinations,
        "tech_features": tech_features,
        "available_sizes": available_sizes
    }

def generate_sku():
    """Generate unique SKU"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

async def create_sneaker_batch(data, batch_size=1000, flash_sale_probability=0.08):
    """Create a batch of sneakers"""
    brands_data = data["brands_data"]
    color_combinations = data["color_combinations"]
    tech_features = data["tech_features"]
    available_sizes = data["available_sizes"]
    
    sneakers = []
    
    for i in range(batch_size):
        # Select brand and get its characteristics
        brand = random.choice(list(brands_data.keys()))
        brand_info = brands_data[brand]
        
        # Generate product details
        category = random.choice(brand_info["categories"])
        model = random.choice(brand_info["signature_models"])
        colors = random.choice(color_combinations)
        
        # Price generation based on brand
        min_price, max_price = brand_info["price_range"]
        base_price = round(random.uniform(min_price, max_price), 2)
        
        # Flash sale logic
        is_flash_sale = random.random() < flash_sale_probability
        flash_sale_end = None
        sale_price = None
        
        if is_flash_sale:
            # Flash sale duration between 1-72 hours
            flash_sale_end = datetime.now() + timedelta(hours=random.randint(1, 72))
            # Discount between 20-50%
            discount = random.uniform(0.2, 0.5)
            sale_price = round(base_price * (1 - discount), 2)
        
        # Generate sizes (not all sizes available for all shoes)
        available_shoe_sizes = random.sample(available_sizes, random.randint(8, len(available_sizes)))
        available_shoe_sizes.sort()
        
        # Create sneaker document
        sneaker = {
            "sku": generate_sku(),
            "name": f"{brand} {model} '{' '.join(colors)}'",
            "brand": brand,
            "price": base_price,
            "sale_price": sale_price,
            "description": f"The {model} combines {random.choice(tech_features)} with premium materials for ultimate comfort and style. Perfect for {category.lower()} activities.",
            "category": category,
            "sizes": available_shoe_sizes,
            "colors": colors,
            "image_url": f"https://picsum.photos/400/400?random={random.randint(1, 10000)}",
            "stock_quantity": random.randint(0, 150),
            "rating": round(random.uniform(3.5, 5.0), 1),
            "reviews_count": random.randint(5, 1200),
            "is_featured": random.random() < 0.15,  # 15% featured
            "is_flash_sale": is_flash_sale,
            "flash_sale_end": flash_sale_end,
            "created_at": datetime.now() - timedelta(days=random.randint(0, 365)),
            "weight": round(random.uniform(0.8, 1.5), 1),  # kg
            "materials": random.sample(["Leather", "Synthetic", "Mesh", "Canvas", "Suede", "Rubber"], random.randint(2, 4)),
            "country_of_origin": random.choice(["Vietnam", "China", "Indonesia", "Thailand", "India"]),
            "sustainability_rating": random.choice(["A", "B", "C", None, None]),  # Some shoes don't have rating
        }
        
        sneakers.append(sneaker)
    
    return sneakers

async def populate_database(target_count=20_000_000):
    """Populate database with target number of sneakers"""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.sneaker_store
    collection = db.sneakers
    
    try:
        # Check existing count
        existing_count = await collection.count_documents({})
        logger.info(f"Current sneaker count: {existing_count:,}")
        
        if existing_count >= target_count:
            logger.info(f"Database already has {existing_count:,} sneakers (target: {target_count:,})")
            return
        
        remaining = target_count - existing_count
        logger.info(f"Need to add {remaining:,} more sneakers")
        
        # Generate base data
        data = await generate_advanced_sneaker_data()
        
        batch_size = 5000  # Process in batches for memory efficiency
        batches_needed = (remaining + batch_size - 1) // batch_size
        
        for batch_num in range(batches_needed):
            current_batch_size = min(batch_size, remaining - (batch_num * batch_size))
            
            logger.info(f"Processing batch {batch_num + 1}/{batches_needed} ({current_batch_size:,} items)")
            
            # Generate batch
            sneakers = await create_sneaker_batch(data, current_batch_size)
            
            # Insert batch
            try:
                result = await collection.insert_many(sneakers, ordered=False)
                logger.info(f"Successfully inserted {len(result.inserted_ids):,} sneakers")
            except Exception as e:
                logger.error(f"Error inserting batch: {e}")
                # Continue with next batch
                continue
            
            # Progress update
            current_total = await collection.count_documents({})
            logger.info(f"Total sneakers now: {current_total:,}/{target_count:,} ({(current_total/target_count)*100:.1f}%)")
        
        final_count = await collection.count_documents({})
        logger.info(f"Population complete! Final count: {final_count:,}")
        
        # Create additional indexes for performance
        logger.info("Creating performance indexes...")
        await collection.create_index([("brand", 1), ("category", 1), ("price", 1)])
        await collection.create_index([("is_flash_sale", 1), ("flash_sale_end", 1)])
        await collection.create_index([("created_at", -1)])
        await collection.create_index([("rating", -1)])
        logger.info("Indexes created successfully!")
        
    except Exception as e:
        logger.error(f"Error during population: {e}")
    finally:
        client.close()

async def main():
    """Main function to run the population script"""
    logger.info("Starting sneaker database population...")
    
    # For demonstration, we'll populate with 50,000 sneakers
    # Change this to 20_000_000 for full population (will take several hours)
    target = 50_000
    
    await populate_database(target)
    logger.info("Population script completed!")

if __name__ == "__main__":
    asyncio.run(main())