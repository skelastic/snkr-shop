db.products.aggregate([
  {
    $lookup: {
      from: "skus",
      localField: "product_id",
      foreignField: "product_id",
      as: "variants"
    }
  },
  {
    $match: {
      "variants.stock_available": { $gt: 0 }
    }
  },
  {
    $addFields: {
      available_variants: {
        $filter: {
          input: "$variants",
          cond: { $gt: ["$$this.stock_available", 0] }
        }
      }
    }
  },
  {
    $addFields: {
      total_stock: { $sum: "$available_variants.stock_available" },
      min_price: { $min: "$available_variants.price" },
      variant_count: { $size: "$available_variants" }
    }
  },
  {
    $project: {
      name: 1,
      brand: 1,
      category: 1,
      total_stock: 1,
      min_price: 1,
      variant_count: 1,
      variants: "$available_variants"
    }
  }
]).pretty();