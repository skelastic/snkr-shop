#!/usr/bin/env python3
"""
Database setup and migration script for PostgreSQL
This script creates the database schema and provides utilities for data migration
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text, Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey, Index, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY

# Define the models here to avoid import issues
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    brand = Column(String(100), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    base_price = Column(Float, nullable=False)
    images = Column(JSON)
    release_date = Column(DateTime, nullable=False)
    materials = Column(ARRAY(String))
    technology = Column(ARRAY(String))
    available_sizes = Column(ARRAY(Float))
    available_colors = Column(ARRAY(String))
    is_featured = Column(Boolean, default=False, index=True)
    rating = Column(Float, default=0.0)
    reviews_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    skus = relationship("SKU", back_populates="product")

    __table_args__ = (
        Index('idx_product_brand_category', 'brand', 'category'),
        Index('idx_product_featured_brand', 'is_featured', 'brand'),
        Index('idx_product_name_search', 'name'),
    )

class SKU(Base):
    __tablename__ = "skus"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.product_id'), nullable=False, index=True)
    size = Column(Float, nullable=False)
    color_code = Column(String(10), nullable=False)
    color_name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False, index=True)
    sale_price = Column(Float, nullable=True)
    stock_quantity = Column(Integer, nullable=False, default=0)
    stock_reserved = Column(Integer, nullable=False, default=0)
    stock_available = Column(Integer, nullable=False, default=0, index=True)
    weight = Column(Float)
    dimensions = Column(JSON)
    barcode = Column(String(50))
    supplier_code = Column(String(50))
    warehouse_location = Column(String(50))
    is_flash_sale = Column(Boolean, default=False, index=True)
    flash_sale_end = Column(DateTime, nullable=True)
    brand = Column(String(100), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    product_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    product = relationship("Product", back_populates="skus")

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
    items = Column(JSON)
    total_amount = Column(Float, nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=func.now())

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin@localhost:5432/sneaker_store")

def create_database_schema():
    """Create all database tables"""
    engine = create_engine(DATABASE_URL)

    print("Creating database schema...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database schema created successfully!")

    return engine

def drop_database_schema():
    """Drop all database tables (be careful!)"""
    engine = create_engine(DATABASE_URL)

    print("⚠️  WARNING: Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    print("🗑️  Database schema dropped!")

    return engine

def create_indexes():
    """Create additional indexes for performance"""
    engine = create_engine(DATABASE_URL)

    additional_indexes = [
        # Full-text search indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_name_gin ON products USING gin(to_tsvector('english', name));",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_description_gin ON products USING gin(to_tsvector('english', description));",

        # Composite indexes for common query patterns
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_skus_brand_category_price ON skus (brand, category, price);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_skus_flash_sale_active ON skus (is_flash_sale, flash_sale_end) WHERE is_flash_sale = true;",

        # Partial indexes for better performance
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_skus_available_stock ON skus (stock_available) WHERE stock_available > 0;",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_featured ON products (is_featured) WHERE is_featured = true;",

        # JSONB indexes for image queries
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_images_gin ON products USING gin(images);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_skus_dimensions_gin ON skus USING gin(dimensions);",
    ]

    print("Creating additional performance indexes...")
    with engine.connect() as conn:
        for index_sql in additional_indexes:
            try:
                print(f"Creating index: {index_sql}")
                conn.execute(text(index_sql))
                conn.commit()
            except Exception as e:
                print(f"⚠️  Error creating index: {e}")
                conn.rollback()

    print("✅ Additional indexes created!")

def migrate_from_mongodb_sample():
    """
    Sample function to migrate data from MongoDB format to PostgreSQL
    This shows how to convert the sample JSON data provided
    """
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    # Sample product data (from your product-sample.json)
    sample_product = {
        "_id": {"$oid": "689f54d09adb3f9bf709e51f"},
        "product_id": "SKX-EN-DO",
        "name": "Skechers Energy Downforce",
        "brand": "Skechers",
        "category": "Running",
        "description": "Premium Energy Downforce from Skechers featuring Gel, HOVR technology and Leather, Mesh construction.",
        "base_price": 119.04,
        "images": {
            "main": "https://picsum.photos/800/600?random=894",
            "gallery": [
                "https://picsum.photos/600/600?random=1253",
                "https://picsum.photos/600/600?random=2683",
                "https://picsum.photos/600/600?random=9012",
                "https://picsum.photos/600/600?random=1331"
            ]
        },
        "release_date": {"$date": "2024-03-26T08:40:00.605Z"},
        "materials": ["Leather", "Mesh"],
        "technology": ["Gel", "HOVR"],
        "available_sizes": [6, 6.5, 7, 8.5, 9.5, 10, 12, 12.5, 13],
        "available_colors": ["Turquoise/Blue", "Pink/White", "Navy/White", "Black/Red", "Orange/White"],
        "is_featured": False,
        "rating": 3.7,
        "reviews_count": 1263,
        "created_at": {"$date": "2025-08-15T08:40:00.605Z"},
        "updated_at": {"$date": "2025-08-15T08:40:00.605Z"}
    }

    # Sample SKU data (from your sku-sample.json)
    sample_sku = {
        "_id": {"$oid": "689f54d09adb3f9bf709e907"},
        "sku": "SKX-EN-DO-TB-130",
        "product_id": "SKX-EN-DO",
        "size": 13,
        "color_code": "TB",
        "color_name": "Turquoise/Blue",
        "price": 142.28,
        "sale_price": None,
        "stock_quantity": 13,
        "stock_reserved": 5,
        "stock_available": 8,
        "weight": 1.4,
        "dimensions": {
            "length": 28.3,
            "width": 12.3,
            "height": 10.7
        },
        "barcode": "707040792207",
        "supplier_code": "SKE-167",
        "warehouse_location": "A-18-A",
        "is_flash_sale": False,
        "flash_sale_end": None,
        "brand": "Skechers",
        "category": "Running",
        "product_name": "Skechers Energy Downforce",
        "created_at": {"$date": "2025-08-15T08:40:00.605Z"},
        "updated_at": {"$date": "2025-08-15T08:40:00.605Z"}
    }

    try:
        # Convert and insert product
        product = Product(
            product_id=sample_product["product_id"],
            name=sample_product["name"],
            brand=sample_product["brand"],
            category=sample_product["category"],
            description=sample_product["description"],
            base_price=sample_product["base_price"],
            images=sample_product["images"],
            release_date=datetime.fromisoformat(sample_product["release_date"]["$date"].replace("Z", "+00:00")),
            materials=sample_product["materials"],
            technology=sample_product["technology"],
            available_sizes=sample_product["available_sizes"],
            available_colors=sample_product["available_colors"],
            is_featured=sample_product["is_featured"],
            rating=sample_product["rating"],
            reviews_count=sample_product["reviews_count"],
            created_at=datetime.fromisoformat(sample_product["created_at"]["$date"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(sample_product["updated_at"]["$date"].replace("Z", "+00:00"))
        )

        db.add(product)
        db.flush()  # Get the ID

        # Convert and insert SKU
        sku = SKU(
            sku=sample_sku["sku"],
            product_id=sample_sku["product_id"],
            size=sample_sku["size"],
            color_code=sample_sku["color_code"],
            color_name=sample_sku["color_name"],
            price=sample_sku["price"],
            sale_price=sample_sku["sale_price"],
            stock_quantity=sample_sku["stock_quantity"],
            stock_reserved=sample_sku["stock_reserved"],
            stock_available=sample_sku["stock_available"],
            weight=sample_sku["weight"],
            dimensions=sample_sku["dimensions"],
            barcode=sample_sku["barcode"],
            supplier_code=sample_sku["supplier_code"],
            warehouse_location=sample_sku["warehouse_location"],
            is_flash_sale=sample_sku["is_flash_sale"],
            flash_sale_end=sample_sku["flash_sale_end"],
            brand=sample_sku["brand"],
            category=sample_sku["category"],
            product_name=sample_sku["product_name"],
            created_at=datetime.fromisoformat(sample_sku["created_at"]["$date"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(sample_sku["updated_at"]["$date"].replace("Z", "+00:00"))
        )

        db.add(sku)
        db.commit()

        print("✅ Sample data migrated successfully!")
        print(f"Product ID: {product.id}")
        print(f"SKU ID: {sku.id}")

    except Exception as e:
        print(f"❌ Error migrating sample data: {e}")
        db.rollback()
    finally:
        db.close()


def generate_sample_data(num_products=50, num_skus_per_product=5):
    """Generate sample data for testing with collision-proof UUID product_ids and random SKU codes."""
    from sqlalchemy.orm import Session
    import random, string, secrets, math

    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    brands = ["Nike", "Adidas", "Jordan", "Puma", "New Balance", "Converse", "Vans", "Reebok", "Skechers", "ASICS"]
    categories = ["Running", "Basketball", "Casual", "Training", "Skateboarding", "Tennis", "Soccer", "Walking"]
    colors = [
        ("BK", "Black"), ("WH", "White"), ("RD", "Red"), ("BL", "Blue"),
        ("GR", "Green"), ("GY", "Grey"), ("YL", "Yellow"), ("OR", "Orange"),
        ("PR", "Purple"), ("PK", "Pink"),
    ]
    sizes = [6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 13]

    def rand_images(n=None):
        if n is None:
            n = random.randint(1, 4)
        base = "https://cdn.example.com/images"
        return [f"{base}/{secrets.token_hex(8)}.jpg" for _ in range(n)]

    def rand_sku_code(brand: str, color_code: str, size: float) -> str:
        prefix = "".join(c for c in brand.upper() if c.isalnum())[:3]
        return f"{prefix}-{color_code}-{str(size).replace('.', '')}-{secrets.token_hex(4)}"

    db: Session = SessionLocal()
    try:
        products_created = 0
        skus_created = 0

        for _ in range(num_products):
            brand = random.choice(brands)
            category = random.choice(categories)

            product_uuid = uuid.uuid4()  # collision-proof
            base_price = round(random.uniform(80.0, 260.0), 2)

            product = Product(
                id=uuid.uuid4(),  # primary key UUID
                product_id=product_uuid,  # business UUID referenced by SKUs
                name=f"{brand} {random.choice(['Runner','Fly','Zoom','Ultra','Boost','Classic','Glide','Velocity','Aero'])} {secrets.token_hex(2).upper()}",
                brand=brand,
                category=category,
                description="Autogenerated sample product for development and testing.",
                base_price=base_price,
                images=rand_images(),
                release_date=datetime.utcnow(),
                materials=["Leather","Mesh","Synthetic","Suede"],
                technology=["Air Max","Boost","React","Zoom"],
                available_sizes=random.sample(sizes, k=min(len(sizes), random.randint(4, 8))),
                available_colors=[c for _, c in random.sample(colors, k=min(len(colors), random.randint(2, 5)))],
                rating=round(random.uniform(2.5, 5.0), 1)
            )
            db.add(product)
            products_created += 1

            # Create SKUs for this product
            chosen_sizes = random.sample(sizes, k=min(num_skus_per_product, len(sizes)))
            chosen_colors = random.sample(colors, k=min(num_skus_per_product, len(colors)))
            for size, (ccode, cname) in zip(chosen_sizes, chosen_colors):
                sku_price = round(base_price * (1.0 + random.uniform(-0.15, 0.15)), 2)
                sku = SKU(
                    id=uuid.uuid4(),
                    product_id=product_uuid,  # FK to products.product_id (UUID)
                    sku=rand_sku_code(brand, ccode, size),
                    size=float(size),
                    color_code=ccode,
                    color_name=cname,
                    price=sku_price,
                    sale_price=None,
                    stock_quantity=random.randint(0, 500),
                    stock_reserved=0,
                    stock_available=random.randint(0, 500),
                    weight=round(random.uniform(0.5, 1.5), 2),
                    dimensions={"l": 30, "w": 20, "h": 12},
                    barcode="".join(random.choices(string.digits, k=12)),
                    supplier_code=secrets.token_hex(3).upper(),
                    warehouse_location=random.choice(["A1","B3","C2","D5"]),
                    is_flash_sale=random.random() < 0.1,
                    flash_sale_end=None,
                    brand=brand,
                    category=category,
                    product_name=product.name
                )
                db.add(sku)
                skus_created += 1

        db.commit()
        print(f"Inserted {products_created} products and {skus_created} SKUs.")
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

def reset_database():
    """Reset the entire database - drop and recreate schema"""
    print("🔄 Resetting database...")
    drop_database_schema()
    create_database_schema()
    create_indexes()
    print("✅ Database reset complete!")

def setup_database():
    """Complete database setup - create schema, indexes, and sample data"""
    print("🚀 Setting up database...")
    create_database_schema()
    create_indexes()
    migrate_from_mongodb_sample()
    generate_sample_data(5000, 5)
    print("🎉 Database setup complete!")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python database_setup.py [command]")
        print("Commands:")
        print("  setup     - Complete database setup")
        print("  reset     - Drop and recreate database")
        print("  schema    - Create schema only")
        print("  indexes   - Create indexes only")
        print("  sample    - Generate sample data only")
        print("  migrate   - Migrate sample MongoDB data")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "setup":
        setup_database()
    elif command == "reset":
        reset_database()
    elif command == "schema":
        create_database_schema()
    elif command == "indexes":
        create_indexes()
    elif command == "sample":
        generate_sample_data(5000, 5)
    elif command == "migrate":
        migrate_from_mongodb_sample()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)