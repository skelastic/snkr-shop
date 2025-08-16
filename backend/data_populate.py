# Data population endpoint (run once to populate database)
@app.post("/populate-data")
async def populate_sneakers():
    existing_products = await products_collection.count_documents({})
    existing_skus = await skus_collection.count_documents({})

    if existing_products >= 100:  # Demo check - reduce for testing
        return {"message": f"Database already has {existing_products:,} products and {existing_skus:,} SKUs"}

    # For demo, create 10 products with 5 SKUs each = 50 SKUs
    generator = SneakerDataGenerator()

    products_batch = []
    skus_batch = []

    for i in range(10):  # 10 products for demo
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

    # Insert data
    await products_collection.insert_many(products_batch)
    await skus_collection.insert_many(skus_batch)

    return {
        "message": f"Successfully populated {len(products_batch)} products and {len(skus_batch)} SKUs",
        "products_created": len(products_batch),
        "skus_created": len(skus_batch)
    }

# Helper class for data generation (simplified version for the API)
class SneakerDataGenerator:
    def __init__(self):
        self.brands_data = {
            "Nike": {
                "brand_code": "NIK",
                "price_range": (80, 350),
                "categories": ["Running", "Basketball", "Lifestyle", "Training"],
                "product_lines": {
                    "Air Max": ["90", "95", "97", "270"],
                    "Air Force": ["1", "1 Low"],
                    "Dunk": ["Low", "High"]
                }
            },
            "Adidas": {
                "brand_code": "ADS",
                "price_range": (70, 300),
                "categories": ["Running", "Basketball", "Lifestyle"],
                "product_lines": {
                    "Ultraboost": ["22", "23"],
                    "Stan Smith": ["Classic", "Recon"]
                }
            }
        }

        self.color_combinations = {
            "WB": {"name": "White/Black", "colors": ["White", "Black"]},
            "BW": {"name": "Black/White", "colors": ["Black", "White"]},
            "RW": {"name": "Red/White", "colors": ["Red", "White"]},
            "BL": {"name": "Blue/White", "colors": ["Blue", "White"]},
            "BR": {"name": "Black/Red", "colors": ["Black", "Red"]}
        }

        self.available_sizes = [8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0]
        self.materials = ["Leather", "Synthetic", "Mesh", "Canvas", "Suede"]
        self.technologies = ["Air Max", "Boost", "React", "Zoom Air"]

    def create_product_document(self, brand: str, line: str, model: str):
        """Create a master product document"""
        brand_info = self.brands_data[brand]
        product_id = f"{brand_info['brand_code']}-{line.replace(' ', '')[:3].upper()}-{model.replace(' ', '')[:3].upper()}"

        min_price, max_price = brand_info["price_range"]
        base_price = round(random.uniform(min_price, max_price), 2)

        selected_materials = random.sample(self.materials, random.randint(2, 3))
        selected_tech = random.sample(self.technologies, random.randint(1, 2))

        available_sizes = random.sample(self.available_sizes, random.randint(5, len(self.available_sizes)))
        available_sizes.sort()

        available_color_codes = list(self.color_combinations.keys())  # All 5 colors
        available_colors = [self.color_combinations[code]["name"] for code in available_color_codes]

        product = {
            "product_id": product_id,
            "name": f"{brand} {line} {model}",
            "brand": brand,
            "category": random.choice(brand_info["categories"]),
            "description": f"Premium {line} {model} from {brand} featuring {', '.join(selected_tech)} technology.",
            "base_price": base_price,
            "images": {
                "main": f"https://picsum.photos/800/600?random={random.randint(1, 10000)}",
                "gallery": [f"https://picsum.photos/600/600?random={random.randint(1, 10000)}" for _ in range(4)]
            },
            "release_date": datetime.now() - timedelta(days=random.randint(0, 365)),
            "materials": selected_materials,
            "technology": selected_tech,
            "available_sizes": available_sizes,
            "available_colors": available_colors,
            "is_featured": random.random() < 0.2,
            "rating": round(random.uniform(3.5, 5.0), 1),
            "reviews_count": random.randint(50, 500),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        return product, available_color_codes, available_sizes

    def create_sku_documents(self, product, color_codes, sizes):
        """Create 5 SKU documents for a product (one per color)"""
        skus = []
        selected_size = random.choice(sizes)

        for color_code in color_codes:
            color_info = self.color_combinations[color_code]

            price = product["base_price"]
            if selected_size >= 11.0:
                price += random.uniform(5, 15)

            is_flash_sale = random.random() < 0.1
            sale_price = None
            flash_sale_end = None

            if is_flash_sale:
                flash_sale_end = datetime.now() + timedelta(hours=random.randint(6, 48))
                sale_price = round(price * random.uniform(0.7, 0.85), 2)

            stock_quantity = random.randint(0, 50)
            stock_reserved = random.randint(0, min(3, stock_quantity))
            stock_available = stock_quantity - stock_reserved

            sku = {
                "sku": f"{product['brand'][:3].upper()}-{product['product_id'].split('-', 1)[1]}-{color_code}-{str(selected_size).replace('.', '')}",
                "product_id": product["product_id"],
                "size": selected_size,
                "color_code": color_code,
                "color_name": color_info["name"],
                "price": round(price, 2),
                "sale_price": sale_price,
                "stock_quantity": stock_quantity,
                "stock_reserved": stock_reserved,
                "stock_available": stock_available,
                "weight": round(random.uniform(0.8, 1.2), 1),
                "dimensions": {
                    "length": round(random.uniform(28.0, 32.0), 1),
                    "width": round(random.uniform(10.0, 12.0), 1),
                    "height": round(random.uniform(9.0, 11.0), 1)
                },
                "barcode": ''.join(random.choices(string.digits, k=12)),
                "supplier_code": f"{product['brand'][:3].upper()}-{random.randint(100, 999)}",
                "warehouse_location": f"A-{random.randint(1, 20):02d}-{chr(65 + random.randint(0, 4))}",
                "is_flash_sale": is_flash_sale,
                "flash_sale_end": flash_sale_end,
                "brand": product["brand"],
                "category": product["category"],
                "product_name": product["name"],
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }

            skus.append(sku)

        return skus
