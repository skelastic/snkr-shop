#!/usr/bin/env python3
"""
Seed PostgreSQL with 10,000 sneakers, each having 1–5 variants.

Usage:
  pip install psycopg2-binary
  python seed_pg_sneakers.py \
    --host localhost --port 5432 --db sneaker_store --user admin --password admin \
    --count 10000 --batch-size 1000 --drop
"""

import argparse
import random
import string
from datetime import datetime, timezone

import psycopg2
from psycopg2.extras import execute_values, Json

BRANDS = ["Nike", "Adidas", "New Balance", "Puma", "Asics", "Reebok", "Saucony", "Converse", "Vans"]
CATEGORIES = ["Lifestyle", "Running", "Basketball", "Skate", "Trail", "Training"]
COLORS = [
    ("BK", "Black"), ("WH", "White"), ("RD", "Red"), ("BL", "Blue"), ("GR", "Green"),
    ("GY", "Grey"), ("TN", "Tan"), ("YW", "Yellow"), ("OR", "Orange"), ("PR", "Purple")
]
SIZES_US = [6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 13]

def make_product_name(brand: str) -> str:
    line = random.choice(["Aero", "Vector", "Pulse", "Zoom", "Nova", "Glide", "Shift", "Racer", "Core", "Edge"])
    suffix = random.choice(["Pro", "Lite", "X", "Max", "Prime", "Elite"])
    return f"{brand} {line} {suffix}"

def make_variant(pid: str):
    color_code, color_name = random.choice(COLORS)
    size = random.choice(SIZES_US)
    base_price = random.choice([8999, 9999, 10999, 11999, 12999, 14999])
    delta = random.choice([-1000, -500, 0, 0, 500, 1000])
    price_cents = max(4999, base_price + delta)
    stock = random.randint(0, 250)
    sku = f"{pid}-{color_code}-{str(size).replace('.', '')}"
    upc = "".join(random.choices(string.digits, k=12))
    images = [
        f"https://example.cdn/sneakers/{pid}/{color_code}/main.jpg",
        f"https://example.cdn/sneakers/{pid}/{color_code}/side.jpg",
    ]
    return {
        "sku": sku,
        "color_code": color_code,
        "color_name": color_name,
        "size_us": float(size),
        "price_cents": int(price_cents),
        "in_stock": int(stock),
        "upc": upc,
        "images": images,
    }

def ensure_schema(cur, drop=False):
    if drop:
        cur.execute("DROP TABLE IF EXISTS variants;")
        cur.execute("DROP TABLE IF EXISTS sneakers;")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sneakers (
        id               BIGSERIAL PRIMARY KEY,
        product_id       TEXT NOT NULL UNIQUE,
        name             TEXT NOT NULL,
        brand            TEXT NOT NULL,
        category         TEXT NOT NULL,
        description      TEXT,
        created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        min_price_cents  INTEGER,
        max_price_cents  INTEGER,
        total_stock      INTEGER,
        variant_count    INTEGER
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS variants (
        id           BIGSERIAL PRIMARY KEY,
        sneaker_id   BIGINT NOT NULL REFERENCES sneakers(id) ON DELETE CASCADE,
        sku          TEXT NOT NULL UNIQUE,
        color_code   TEXT NOT NULL,
        color_name   TEXT NOT NULL,
        size_us      NUMERIC(4,1) NOT NULL,
        price_cents  INTEGER NOT NULL,
        in_stock     INTEGER NOT NULL,
        upc          TEXT NOT NULL,
        images       JSONB NOT NULL DEFAULT '[]'
    );
    """)

    # Helpful indexes
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sneakers_brand_category ON sneakers(brand, category);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_variants_sneaker_id ON variants(sneaker_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_variants_color_size ON variants(color_code, size_us);")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=5432)
    parser.add_argument("--db", default="sneaker_store")
    parser.add_argument("--user", default="admin")
    parser.add_argument("--password", default="admin")
    parser.add_argument("--count", type=int, default=10000)
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument("--drop", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)

    conn = psycopg2.connect(
        host=args.host, port=args.port, dbname=args.db, user=args.user, password=args.password
    )
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            ensure_schema(cur, drop=args.drop)
            conn.commit()

        total_inserted = 0
        i = 1
        while i <= args.count:
            batch_end = min(i + args.batch_size - 1, args.count)

            # Build in-memory batch of sneakers and their variants
            sneakers = []
            variants_pending = []  # list of lists, aligned with sneakers list
            for n in range(i, batch_end + 1):
                brand = random.choice(BRANDS)
                category = random.choice(CATEGORIES)
                product_id = f"SNK-{n:06d}"
                name = make_product_name(brand)

                # create variants first (so we can compute denormalized fields)
                k = random.randint(1, 5)
                seen = set()
                vlist = []
                attempts = 0
                while len(vlist) < k and attempts < 20:
                    v = make_variant(product_id)
                    key = (v["color_code"], v["size_us"])
                    if key not in seen:
                        vlist.append(v)
                        seen.add(key)
                    attempts += 1

                min_price = min(v["price_cents"] for v in vlist)
                max_price = max(v["price_cents"] for v in vlist)
                total_stock = sum(v["in_stock"] for v in vlist)
                created_at = datetime.now(timezone.utc)

                sneakers.append((
                    product_id, name, brand, category,
                    f"{name} is a {category.lower()} sneaker designed for comfort and performance.",
                    created_at, min_price, max_price, total_stock, len(vlist)
                ))
                variants_pending.append(vlist)

            # Insert sneakers with RETURNING ids (order preserved)
            with conn.cursor() as cur:
                insert_sql = """
                    INSERT INTO sneakers
                        (product_id, name, brand, category, description, created_at,
                         min_price_cents, max_price_cents, total_stock, variant_count)
                    VALUES %s
                    RETURNING id, product_id;
                """
                execute_values(cur, insert_sql, sneakers)
                returned = cur.fetchall()  # list of (id, product_id) in the same order as inserted
                # Build all variant rows with correct sneaker_id
                all_variants_rows = []
                for idx, (sneaker_id, pid) in enumerate(returned):
                    for v in variants_pending[idx]:
                        all_variants_rows.append((
                            sneaker_id,
                            v["sku"], v["color_code"], v["color_name"], v["size_us"],
                            v["price_cents"], v["in_stock"], v["upc"], Json(v["images"])
                        ))

                # Bulk insert variants
                if all_variants_rows:
                    execute_values(cur, """
                        INSERT INTO variants
                            (sneaker_id, sku, color_code, color_name, size_us, price_cents, in_stock, upc, images)
                        VALUES %s
                        ON CONFLICT (sku) DO NOTHING
                    """, all_variants_rows)

            conn.commit()
            total_inserted += len(sneakers)
            print(f"Inserted {total_inserted}/{args.count} sneakers (and ~{sum(len(v) for v in variants_pending)} variants) ...")
            i = batch_end + 1

        print("Done.")
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()
