// MongoDB initialization script
db = db.getSiblingDB('sneaker_store');

// Create collections
db.createCollection('sneakers');
db.createCollection('users');
db.createCollection('orders');

// Create indexes for better performance
db.sneakers.createIndex({ "brand": 1, "category": 1 });
db.sneakers.createIndex({ "price": 1 });
db.sneakers.createIndex({ "is_featured": 1 });
db.sneakers.createIndex({ "is_flash_sale": 1 });
db.sneakers.createIndex({ "name": "text", "description": "text" });
db.sneakers.createIndex({ "sku": 1 }, { unique: true });

db.users.createIndex({ "email": 1 }, { unique: true });
db.orders.createIndex({ "user_id": 1 });
db.orders.createIndex({ "created_at": 1 });

print('Database initialized successfully!');