import asyncio
import random
import string
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import logging
from typing import List, Dict, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MongoDB connection
#MONGODB_URL = "mongodb://skelastic:password123@localhost:27017/sneaker_store?authSource=admin"
MONGODB_URL = "mongodb://localhost:27017/sneaker_store"

class SneakerDataGenerator:
    def __init__(self):
        # Enhanced brand data with realistic product lines
        self.brands_data = {
            "Nike": {
                "brand_code": "NIK",
                "price_range": (80, 400),
                "categories": ["Running", "Basketball", "Lifestyle", "Training", "Soccer"],
                "product_lines": {
                    "Air Max": ["90", "95", "97", "270", "Plus", "1", "Thea", "Tavas", "Command", "Sequent"],
                    "Air Force": ["1", "1 Low", "1 Mid", "1 High", "1 Shadow", "1 Utility", "1 Pixel", "1 React"],
                    "Dunk": ["Low", "High", "SB Low", "SB High", "Low Retro", "High Retro", "Low SE", "High SE"],
                    "React": ["Element", "Vision", "Infinity", "Presto", "WR ISPA", "City", "Flyknit", "Live"],
                    "Zoom": ["Pegasus", "Vomero", "Structure", "Fly", "Alphafly", "Vaporfly", "Winflo", "Terra"],
                    "Air Jordan": ["1", "3", "4", "5", "6", "11", "12", "13", "Retro", "Mid", "Low", "High"],
                    "Blazer": ["Mid", "Low", "High", "Mid 77", "Low 77", "SB", "Mid Rebel", "Platform"],
                    "Court": ["Vision", "Borough", "Legacy", "Royale", "Majestic", "Lite", "Vision Alta"],
                    "Revolution": ["5", "6", "Running", "Walking", "Flyease", "Next Nature"],
                    "Mercurial": ["Vapor", "Superfly", "Dream Speed", "Safari", "Academy", "Club"]
                }
            },
            "Adidas": {
                "brand_code": "ADS",
                "price_range": (70, 350),
                "categories": ["Running", "Basketball", "Lifestyle", "Soccer", "Training"],
                "product_lines": {
                    "Ultraboost": ["22", "23", "Light", "DNA", "Web", "Clima", "Laceless", "Slip-On", "ATR"],
                    "NMD": ["R1", "R2", "S1", "CS2", "TS1", "XR1", "CS1", "R1.V2", "360"],
                    "Yeezy": ["350", "380", "500", "700", "Foam Runner", "Slide", "Knit Runner", "450"],
                    "Stan Smith": ["Classic", "Recon", "Lux", "Primeknit", "Bold", "Forever", "Platform"],
                    "Gazelle": ["Indoor", "Bold", "Super", "OG", "ADV", "Platform", "Premium"],
                    "Superstar": ["Foundation", "Bold", "Pure", "Slip-On", "360", "Bonega", "Up"],
                    "Campus": ["80s", "00s", "ADV", "Bold", "Platform", "Suede", "Premium"],
                    "Samba": ["OG", "Classic", "RM", "ADV", "Vegan", "Leather", "Rose"],
                    "ZX": ["2K", "1K", "750", "500", "8000", "9000", "Flux", "Torsion"],
                    "Predator": ["Edge", "Freak", "Accuracy", "Mutator", "Archive", "19+", "20+"]
                }
            },
            "Jordan": {
                "brand_code": "JOR",
                "price_range": (120, 600),
                "categories": ["Basketball", "Lifestyle"],
                "product_lines": {
                    "Air Jordan": ["1 Low", "1 Mid", "1 High", "3", "4", "5", "6", "11", "12", "13", "14"],
                    "Jordan Delta": ["2", "Breathe", "React", "Mid", "SP"],
                    "Jordan Max": ["200", "Aura", "Alpha", "270", "720"],
                    "Jordan Zoom": ["92", "Separate", "Trunner", "Rize", "Zero"],
                    "Jordan Legacy": ["312", "312 Low", "Air", "Court"],
                    "Jordan Point": ["Lane", "Guard", "Forward"],
                    "Jordan Why": ["Not Zer0", "Not Zer0.1", "Not Zer0.2", "Not Zer0.3", "Not Zer0.4"],
                    "Jordan MVP": ["Limited", "Premium", "SE", "Classic"],
                    "Jordan Apex": ["React", "Utility", "Legend Blue"],
                    "Jordan Proto": ["React", "Max 720", "23"]
                }
            },
            "New Balance": {
                "brand_code": "NB",
                "price_range": (60, 300),
                "categories": ["Running", "Lifestyle", "Walking", "Training"],
                "product_lines": {
                    "990": ["v5", "v6", "v7", "Sport", "GL"],
                    "574": ["Core", "Sport", "Classic", "Rugged", "Legacy"],
                    "327": ["Primary", "Casablanca", "Sea Salt", "Team", "Classic"],
                    "2002R": ["Protection Pack", "Rain Cloud", "Phantom", "Refined Future"],
                    "Fresh Foam": ["X", "More", "Zante", "Beacon", "Arishi", "Sport", "Roav"],
                    "FuelCell": ["Rebel", "TC", "Propel", "Echo", "SuperComp"],
                    "860": ["v11", "v12", "v13"],
                    "1080": ["v11", "v12", "v13", "v14"],
                    "Minimus": ["10v1", "20v7", "Trail"],
                    "Made in": ["USA", "UK", "England"]
                }
            },
            "Puma": {
                "brand_code": "PUM",
                "price_range": (50, 250),
                "categories": ["Running", "Lifestyle", "Soccer", "Training", "Motorsport"],
                "product_lines": {
                    "Suede": ["Classic", "Platform", "Heart", "XL", "Mid", "Bow", "Creeper"],
                    "RS-X": ["Reinvention", "Core", "Puzzle", "Toys", "Tracks", "Bold"],
                    "Cali": ["Sport", "Bold", "Wedge", "Dream", "Star"],
                    "Future Rider": ["Play On", "Splash", "Neon", "Space", "Twofold"],
                    "Clyde": ["Court", "Hardwood", "All-Pro", "Disruptor", "OG"],
                    "Roma": ["Basic", "Platform", "Amor", "68", "Anniversary"],
                    "Basket": ["Classic", "Platform", "Heart", "Bold"],
                    "Thunder": ["Spectra", "Electric", "Desert", "Fashion"],
                    "Cell": ["Endura", "Venom", "Alien", "Stellar"],
                    "Ferrari": ["SF", "Drift Cat", "Kart Cat", "Future Cat"]
                }
            },
            "Converse": {
                "brand_code": "CNV",
                "price_range": (40, 150),
                "categories": ["Lifestyle", "Skateboarding"],
                "product_lines": {
                    "Chuck Taylor": ["All Star", "70", "Move", "Run Star", "Lift"],
                    "Chuck 70": ["High", "Low", "Platform", "Vintage", "Archive"],
                    "One Star": ["Pro", "Platform", "Academy", "Vintage"],
                    "Jack Purcell": ["Classic", "Pro", "Signature", "OX"],
                    "Star Player": ["76", "Vintage", "OX"],
                    "Pro Leather": ["High", "Low", "Mid", "Vintage"],
                    "Run Star": ["Hike", "Motion", "Legacy"],
                    "All Star": ["Move", "BB", "Pro", "Disrupt"],
                    "CONS": ["Checkpoint", "Louie Lopez", "Alexis Sablone"],
                    "Weapon": ["86", "OX", "Vintage"]
                }
            },
            "Vans": {
                "brand_code": "VNS",
                "price_range": (45, 180),
                "categories": ["Skateboarding", "Lifestyle", "Snow"],
                "product_lines": {
                    "Old Skool": ["Classic", "Platform", "Pro", "DX", "Stackform"],
                    "Authentic": ["Classic", "Pro", "44 DX", "Anaheim"],
                    "Era": ["Classic", "Pro", "59", "Stacked"],
                    "Slip-On": ["Classic", "Pro", "Platform", "Mule"],
                    "Sk8-Hi": ["Classic", "Pro", "Platform", "Reissue", "Tapered"],
                    "Ward": ["Classic", "Hi", "Platform"],
                    "Filmore": ["High", "Decon"],
                    "Knu Skool": ["Classic", "Platform"],
                    "Style 36": ["Decon", "SF"],
                    "Half Cab": ["Pro", "33", "92"]
                }
            },
            "Reebok": {
                "brand_code": "RBK",
                "price_range": (55, 200),
                "categories": ["Running", "Training", "Lifestyle", "CrossFit"],
                "product_lines": {
                    "Classic Leather": ["Legacy", "Archive", "Platform", "Alter"],
                    "Club C": ["85", "Legacy", "Double", "Revenge"],
                    "Pump": ["Omni Zone", "Court", "Fury", "Supreme"],
                    "Fury": ["Adapt", "Trail", "Sandal"],
                    "Question": ["Mid", "Low", "Practice"],
                    "Kamikaze": ["II", "Low"],
                    "Instapump": ["Fury", "OG", "Trail"],
                    "Nano": ["X", "X1", "X2", "X3"],
                    "Floatride": ["Energy", "Run Fast", "Forever"],
                    "ZigKinetica": ["Edge", "II", "Concept"]
                }
            },
            "ASICS": {
                "brand_code": "ASC",
                "price_range": (70, 280),
                "categories": ["Running", "Training", "Lifestyle", "Tennis"],
                "product_lines": {
                    "Gel-Lyte": ["III", "V", "MT", "Runner"],
                    "Gel-Kayano": ["28", "29", "30", "Lite"],
                    "Gel-Nimbus": ["24", "25", "26"],
                    "Tiger": ["Mexico 66", "Serrano", "Corsair"],
                    "Onitsuka": ["Mexico 66", "Serrano", "GSM"],
                    "Gel-Quantum": ["90", "180", "360"],
                    "Novablast": ["2", "3", "SPS"],
                    "MetaRise": ["Elite", "Speed"],
                    "Court": ["FF", "Control", "Speed"],
                    "Gel-Resolution": ["8", "9"]
                }
            },
            "Under Armour": {
                "brand_code": "UA",
                "price_range": (60, 250),
                "categories": ["Basketball", "Running", "Training", "Baseball"],
                "product_lines": {
                    "Curry": ["Flow", "8", "9", "10", "Spawn"],
                    "HOVR": ["Phantom", "Sonic", "Infinite", "Machina"],
                    "Charged": ["Assert", "Rogue", "Pursuit", "Bandit"],
                    "Flow": ["Velociti", "Futr X"],
                    "Project Rock": ["BSR", "Training", "Delta"],
                    "TriBase": ["Reign", "Edge", "Thrive"],
                    "SlipSpeed": ["Training", "Mega"],
                    "Anatomix": ["Spawn", "Low"],
                    "ClutchFit": ["Drive", "Force"],
                    "SpeedForm": ["Gemini", "Europa"]
                }
            },
            "Skechers": {
                "brand_code": "SKX",
                "price_range": (40, 150),
                "categories": ["Walking", "Running", "Lifestyle", "Work"],
                "product_lines": {
                    "Go Walk": ["5", "6", "Joy", "Evolution"],
                    "Air Cooled": ["Memory Foam", "Goga Mat"],
                    "D'Lites": ["Biggest Fan", "Fresh Start", "Moon View"],
                    "Energy": ["Afterburn", "Downforce"],
                    "Flex": ["Appeal", "Advantage"],
                    "Max": ["Cushioning", "Road", "Trail"],
                    "Ultra": ["Flex", "Go"],
                    "Arch Fit": ["Big Appeal", "Comfy Wave"],
                    "Work": ["Sure Track", "Soft Stride"],
                    "Sport": ["Energy", "Afterburn"]
                }
            },
            "Fila": {
                "brand_code": "FLA",
                "price_range": (45, 120),
                "categories": ["Lifestyle", "Running", "Basketball", "Tennis"],
                "product_lines": {
                    "Disruptor": ["II", "III", "Sandal", "Wedge"],
                    "Ray": ["Tracer", "Flow", "Low"],
                    "Grant Hill": ["2", "96", "Low"],
                    "Cage": ["Delirium", "Mid"],
                    "Mindblower": ["Vintage", "Low"],
                    "Original": ["Fitness", "Tennis"],
                    "Heritage": ["Court", "Tennis"],
                    "Strada": ["Low", "Mid"],
                    "Creator": ["Low", "Mid"],
                    "Renno": ["Low", "Mid"]
                }
            }
        }

        # Extended color combinations for more variety
        self.color_combinations = {
            "WB": {"name": "White/Black", "colors": ["White", "Black"]},
            "BW": {"name": "Black/White", "colors": ["Black", "White"]},
            "RW": {"name": "Red/White", "colors": ["Red", "White"]},
            "BL": {"name": "Blue/White", "colors": ["Blue", "White"]},
            "BR": {"name": "Black/Red", "colors": ["Black", "Red"]},
            "NV": {"name": "Navy/White", "colors": ["Navy", "White"]},
            "GR": {"name": "Gray/Black", "colors": ["Gray", "Black"]},
            "GW": {"name": "Green/White", "colors": ["Green", "White"]},
            "PK": {"name": "Pink/White", "colors": ["Pink", "White"]},
            "PR": {"name": "Purple/Black", "colors": ["Purple", "Black"]},
            "YL": {"name": "Yellow/Black", "colors": ["Yellow", "Black"]},
            "OW": {"name": "Orange/White", "colors": ["Orange", "White"]},
            "BT": {"name": "Brown/Tan", "colors": ["Brown", "Tan"]},
            "MG": {"name": "Maroon/Gold", "colors": ["Maroon", "Gold"]},
            "TW": {"name": "Teal/White", "colors": ["Teal", "White"]},
            "LB": {"name": "Lime/Black", "colors": ["Lime", "Black"]},
            "SB": {"name": "Sky Blue/White", "colors": ["Sky Blue", "White"]},
            "VW": {"name": "Violet/White", "colors": ["Violet", "White"]},
            "TB": {"name": "Turquoise/Blue", "colors": ["Turquoise", "Blue"]},
            "CB": {"name": "Coral/Beige", "colors": ["Coral", "Beige"]},
            "MW": {"name": "Mint/White", "colors": ["Mint", "White"]},
            "RS": {"name": "Rose/Silver", "colors": ["Rose", "Silver"]},
            "GB": {"name": "Gold/Black", "colors": ["Gold", "Black"]},
            "SW": {"name": "Silver/White", "colors": ["Silver", "White"]},
            "BB": {"name": "Black/Blue", "colors": ["Black", "Blue"]}
        }

        # Available sizes (US sizing)
        self.available_sizes = [6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0]

        # Materials and technologies
        self.materials = ["Leather", "Synthetic", "Mesh", "Canvas", "Suede", "Rubber", "Foam", "Primeknit", "Flyknit"]
        self.technologies = ["Air Max", "Boost", "React", "Zoom Air", "Fresh Foam", "Gel", "HOVR", "Charged"]

        # Warehouse locations
        self.warehouse_locations = [f"{chr(65+i)}-{j:02d}-{chr(65+k)}" for i in range(5) for j in range(1, 21) for k in range(5)]

    def generate_product_id(self, brand: str, line: str, model: str) -> str:
        """Generate unique product ID"""
        brand_code = self.brands_data[brand]["brand_code"]
        line_code = ''.join(word[:2].upper() for word in line.split())
        model_code = ''.join(word[:2].upper() for word in model.split())
        return f"{brand_code}-{line_code}-{model_code}"

    def generate_sku(self, brand: str, product_code: str, color_code: str, size: float) -> str:
        """Generate unique SKU"""
        brand_code = self.brands_data[brand]["brand_code"]
        size_str = str(size).replace('.', '')
        return f"{brand_code}-{product_code}-{color_code}-{size_str}"

    def create_product_document(self, brand: str, line: str, model: str) -> Dict:
        """Create a master product document"""
        brand_info = self.brands_data[brand]
        product_id = self.generate_product_id(brand, line, model)

        # Generate pricing
        min_price, max_price = brand_info["price_range"]
        base_price = round(random.uniform(min_price, max_price), 2)

        # Select materials and technology
        selected_materials = random.sample(self.materials, random.randint(2, 4))
        selected_tech = random.sample(self.technologies, random.randint(1, 2))

        # Select available sizes and colors for this product
        available_sizes = random.sample(self.available_sizes, random.randint(8, len(self.available_sizes)))
        available_sizes.sort()

        available_color_codes = random.sample(list(self.color_combinations.keys()), 5)  # Always 5 colors = 5 SKUs per size
        available_colors = [self.color_combinations[code]["name"] for code in available_color_codes]

        product = {
            "product_id": product_id,
            "name": f"{brand} {line} {model}",
            "brand": brand,
            "category": random.choice(brand_info["categories"]),
            "description": f"Premium {line} {model} from {brand} featuring {', '.join(selected_tech)} technology and {', '.join(selected_materials[:2])} construction.",
            "base_price": base_price,
            "images": {
                "main": f"https://picsum.photos/800/600?random={random.randint(1, 10000)}",
                "gallery": [f"https://picsum.photos/600/600?random={random.randint(1, 10000)}" for _ in range(4)]
            },
            "release_date": datetime.now() - timedelta(days=random.randint(0, 730)),
            "materials": selected_materials,
            "technology": selected_tech,
            "available_sizes": available_sizes,
            "available_colors": available_colors,
            "is_featured": random.random() < 0.15,  # 15% featured
            "rating": round(random.uniform(3.5, 5.0), 1),
            "reviews_count": random.randint(50, 2000),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        return product, available_color_codes, available_sizes

    def create_sku_documents(self, product: Dict, color_codes: List[str], sizes: List[float]) -> List[Dict]:
        """Create SKU documents for a product (5 color variations)"""
        skus = []

        # Create exactly 5 SKUs per product (one per color)
        selected_size = random.choice(sizes)  # Pick one size for simplicity

        for color_code in color_codes:
            color_info = self.color_combinations[color_code]

            # Price variations
            price = product["base_price"]
            if selected_size >= 12.0:  # Larger sizes cost more
                price += random.uniform(10, 25)

            # Flash sale logic
            is_flash_sale = random.random() < 0.08  # 8% flash sale
            sale_price = None
            flash_sale_end = None

            if is_flash_sale:
                flash_sale_end = datetime.now() + timedelta(hours=random.randint(6, 72))
                sale_price = round(price * random.uniform(0.6, 0.8), 2)

            # Stock quantities
            stock_quantity = random.randint(0, 100)
            stock_reserved = random.randint(0, min(5, stock_quantity))
            stock_available = stock_quantity - stock_reserved

            sku = {
                "sku": self.generate_sku(product["brand"], product["product_id"].split('-', 1)[1], color_code, selected_size),
                "product_id": product["product_id"],
                "size": selected_size,
                "color_code": color_code,
                "color_name": color_info["name"],
                "price": round(price, 2),
                "sale_price": sale_price,
                "stock_quantity": stock_quantity,
                "stock_reserved": stock_reserved,
                "stock_available": stock_available,
                "weight": round(random.uniform(0.8, 1.5), 1),
                "dimensions": {
                    "length": round(random.uniform(28.0, 35.0), 1),
                    "width": round(random.uniform(10.0, 14.0), 1),
                    "height": round(random.uniform(9.0, 13.0), 1)
                },
                "barcode": ''.join(random.choices(string.digits, k=12)),
                "supplier_code": f"{product['brand'][:3].upper()}-{random.randint(100, 999)}",
                "warehouse_location": random.choice(self.warehouse_locations),
                "is_flash_sale": is_flash_sale,
                "flash_sale_end": flash_sale_end,
                # Denormalized fields for performance
                "brand": product["brand"],
                "category": product["category"],
                "product_name": product["name"],
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }

            skus.append(sku)

        return skus

async def populate_hybrid_database(target_products: int = 400_000):
    """Populate database with hybrid schema: 400K products × 5 SKUs = 2M SKUs"""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.sneaker_store
    products_collection = db.products
    skus_collection = db.skus

    generator = SneakerDataGenerator()

    try:
        # Check existing counts
        existing_products = await products_collection.count_documents({})
        existing_skus = await skus_collection.count_documents({})

        logger.info(f"Current counts - Products: {existing_products:,}, SKUs: {existing_skus:,}")

        if existing_products >= target_products:
            logger.info(f"Target already reached: {existing_products:,} products")
            return

        batch_size = 1000  # Products per batch
        products_to_create = target_products - existing_products
        batches_needed = (products_to_create + batch_size - 1) // batch_size

        logger.info(f"Creating {products_to_create:,} products in {batches_needed} batches")

        for batch_num in range(batches_needed):
            current_batch_size = min(batch_size, products_to_create - (batch_num * batch_size))

            logger.info(f"Processing batch {batch_num + 1}/{batches_needed} ({current_batch_size:,} products)")

            products_batch = []
            skus_batch = []

            # Generate products and SKUs for this batch
            for _ in range(current_batch_size):
                # Select random brand and product line
                brand = random.choice(list(generator.brands_data.keys()))
                brand_info = generator.brands_data[brand]
                line = random.choice(list(brand_info["product_lines"].keys()))
                model = random.choice(brand_info["product_lines"][line])

                # Create product and its SKUs
                product, color_codes, sizes = generator.create_product_document(brand, line, model)
                skus = generator.create_sku_documents(product, color_codes, sizes)

                products_batch.append(product)
                skus_batch.extend(skus)

            # Insert products
            try:
                await products_collection.insert_many(products_batch, ordered=False)
                logger.info(f"✓ Inserted {len(products_batch):,} products")
            except Exception as e:
                logger.error(f"Error inserting products: {e}")
                continue

            # Insert SKUs
            try:
                await skus_collection.insert_many(skus_batch, ordered=False)
                logger.info(f"✓ Inserted {len(skus_batch):,} SKUs")
            except Exception as e:
                logger.error(f"Error inserting SKUs: {e}")
                continue

            # Progress update
            current_products = await products_collection.count_documents({})
            current_skus = await skus_collection.count_documents({})
            progress = (current_products / target_products) * 100

            logger.info(f"Progress: {current_products:,}/{target_products:,} products ({progress:.1f}%), {current_skus:,} SKUs")

        # Final counts and statistics
        final_products = await products_collection.count_documents({})
        final_skus = await skus_collection.count_documents({})
        featured_count = await products_collection.count_documents({"is_featured": True})
        flash_sale_count = await skus_collection.count_documents({"is_flash_sale": True})

        logger.info("=" * 60)
        logger.info("POPULATION COMPLETE!")
        logger.info(f"Products created: {final_products:,}")
        logger.info(f"SKUs created: {final_skus:,}")
        logger.info(f"Featured products: {featured_count:,}")
        logger.info(f"Flash sale SKUs: {flash_sale_count:,}")
        logger.info(f"Average SKUs per product: {final_skus/final_products:.1f}")
        logger.info("=" * 60)

        # Create additional performance indexes
        logger.info("Creating additional performance indexes...")

        # Compound indexes for common queries
        await skus_collection.create_index([("brand", 1), ("size", 1), ("stock_available", 1)])
        await skus_collection.create_index([("category", 1), ("price", 1), ("is_flash_sale", 1)])
        await skus_collection.create_index([("is_flash_sale", 1), ("flash_sale_end", 1), ("stock_available", 1)])

        logger.info("✓ Performance indexes created!")

    except Exception as e:
        logger.error(f"Error during population: {e}")
    finally:
        client.close()

async def main():
    """Main function"""
    logger.info("Starting hybrid database population...")
    logger.info("Target: 100,000 products × 5 SKUs each = 500,000 SKUs")

    await populate_hybrid_database(100_000)

    logger.info("Population script completed!")

if __name__ == "__main__":
    asyncio.run(main())