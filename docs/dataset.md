# Slow-Moving and Dead Stock Analysis — Practice Dataset

All records in this package are **synthetic** and created for learning and portfolio development. They do not represent a real company.

## Files

- `products.csv` — product master data (one row per SKU)
- `sales.csv` — sales transactions over the 365-day analysis window
- `inventory_snapshot.csv` — one current stock snapshot per SKU

## Dataset profile

- Products: 20
- Sales transactions: 1104
- Inventory rows: 20
- Distinct categories: 11
- Distinct suppliers: 5
- Analysis / snapshot date: 2026-11-20
- Sales window start: 2025-11-20
- Currency: INR (Indian rupees)

## Join keys

Use `sku` to join the three files. Each SKU appears once in `products.csv` and `inventory_snapshot.csv`, and may appear many times in `sales.csv`.

## Column guide

### products.csv

| Column | Meaning |
|---|---|
| `sku` | Unique product stock-keeping unit |
| `product_name` | Product description |
| `category` | Product category |
| `supplier` | Supplier name |
| `launch_date` | Date the product was introduced |
| `unit_cost` | Purchase cost per unit, in INR |
| `reorder_level` | Stock threshold used to trigger replenishment review |
| `lead_time_days` | Typical supplier lead time in days |

### sales.csv

| Column | Meaning |
|---|---|
| `sale_id` | Unique sales transaction identifier |
| `sale_date` | Transaction date |
| `sku` | Product sold |
| `quantity_sold` | Number of units sold in the transaction |
| `unit_selling_price` | Selling price per unit, in INR |

### inventory_snapshot.csv

| Column | Meaning |
|---|---|
| `snapshot_date` | Date the stock position was recorded |
| `sku` | Product stock-keeping unit |
| `current_stock` | Units currently held in inventory |

## Analysis guidance

The data intentionally contains a mix of sales patterns so you can practise identifying fast-moving, slow-moving, dead, newly launched, and out-of-stock products. Treat any classification thresholds as project assumptions rather than universal inventory standards.

A sensible first analysis date is **2026-11-20**. For example, calculate units sold in the 90 days before that date and in the full 365-day window, then combine those figures with the latest sale date and current stock.

Suggested joins:

```python
product_inventory = inventory_df.merge(products_df, on="sku", how="left")
product_sales = sales_df.merge(products_df[["sku", "unit_cost"]], on="sku", how="left")
```