# Slow-Moving and Dead Stock Analysis System

## 1. Project Overview

The **Slow-Moving and Dead Stock Analysis System** is a Python-based inventory analytics project developed for an electronics distribution business.

The system analyses product sales and current inventory to identify fast-moving, slow-moving and dead-stock products. It also calculates inventory value, quantifies capital tied up in slow-moving and dead stock, and generates business reports with suggested inventory management actions.

The main objective is to help businesses identify inventory risks and make better purchasing, pricing and stock management decisions.

## 2. Business Problem

Unsold and slow-moving inventory ties up business capital that could otherwise be used for other operational activities.

Without regular inventory analysis, a business may continue purchasing products that already have weak demand, while older stock remains unsold.

This project addresses the following business question:

**How can Python-based analysis identify slow-moving and dead stock, quantify the capital tied up in inventory, and support inventory management decisions?**

## 3. Technologies Used

- Python
- Pandas
- NumPy
- CSV files

## 4. Project Structure

```text
Slow-Moving-Dead-Stock-Analysis/
│
├── data/
│   ├── products.csv
│   ├── sales.csv
│   └── inventory_snapshot.csv
│
├── src/
│   └── main.py
│
├── outputs/
│   ├── product_analysis_report.csv
│   ├── category_risk_report.csv
│   ├── inventory_summary_report.csv
│   └── dead_stock_report.csv
│
└── README.md
```

## 5. Analysis Performed

### Product-level inventory analysis

The system calculates:

- Days since the last recorded sale
- Days since product launch
- Total quantity sold during the last 90 days
- Total quantity sold during the last 365 days
- Average monthly demand
- Stock cover in months
- Current inventory value

### Inventory classification

Products are classified using the following business rules:

| Classification | Rule |
|---|---|
| Out of Stock | Current stock is zero |
| Dead Stock | Last sale was at least 180 days ago, or the product has never sold and has been listed for at least 180 days |
| New Product | No recorded sales and product age is under 90 days |
| Insufficient History | No recorded sales and product age is between 90 and 179 days |
| Slow Moving | Last sale was 90–179 days ago, or stock cover exceeds 3 months |
| Fast Moving | Last sale was within 89 days and stock cover is 3 months or less |
| Review Required | Does not match the preceding rules |

These thresholds are project-defined assumptions and can be adjusted to suit a business's inventory policies.

### Financial analysis

The system calculates:

**Inventory Value**

`Current Stock × Unit Cost`

**Average Monthly Demand**

`Quantity Sold During the Last 365 Days ÷ 12`

**Stock Cover**

`Current Stock ÷ Average Monthly Demand`

**Capital at Risk**

`Value of Slow-Moving Inventory + Value of Dead Stock`

**Capital at Risk Percentage**

`(Capital at Risk ÷ Total Inventory Value) × 100`

## 6. Key Business Findings

The analysis produced the following results:

| Metric | Result |
|---|---:|
| Total inventory value | ₹1,14,39,250 |
| Capital at risk | ₹81,09,400 |
| Capital at risk percentage | 70.89% |
| Fast-moving products | 5 |
| Slow-moving products | 4 |
| Dead-stock products | 7 |
| New products | 2 |
| Out-of-stock products | 2 |

### Category-level findings

- Computers have the highest absolute capital at risk, at ₹34,32,000.
- Office Equipment has ₹16,38,600 of inventory value at risk, representing 100% of its category inventory value.
- Photography Equipment also has 100% of its inventory value at risk.
- Mobile Devices and Mobile Accessories have no inventory value classified as slow-moving or dead stock in this snapshot.

### Product-level findings

- The Entry DSLR Camera has the highest dead-stock inventory value at ₹7,65,000.
- The Office Projector has ₹3,99,000 in dead-stock value.
- The Gaming Laptop has ₹34,32,000 in slow-moving inventory value and deserves management attention despite not being classified as dead stock.

## 7. Business Recommendations

The system generates suggested actions based on inventory classification:

| Stock Status | Suggested Action |
|---|---|
| Fast Moving | Maintain stock and monitor demand |
| Slow Moving | Review pricing and consider promotions |
| Dead Stock | Consider clearance, bundling or liquidation |
| New Product | Monitor early sales performance |
| Out of Stock | Review replenishment requirements |
| Insufficient History | Collect more sales data |
| Review Required | Investigate product classification |

These recommendations are intended as decision-support guidance. Actual purchasing, discounting and liquidation decisions should also consider business constraints and market conditions.

## 8. Output Reports

The system generates four CSV reports:

1. **product_analysis_report.csv** — Product-level metrics, inventory classification and recommendations.
2. **category_risk_report.csv** — Inventory value and capital at risk by product category.
3. **inventory_summary_report.csv** — Total inventory value grouped by stock status.
4. **dead_stock_report.csv** — Dead-stock products sorted by inventory value.

## 9. Limitations and Assumptions

- The project uses a synthetic dataset for demonstration.
- Classification thresholds are illustrative business assumptions, not universal inventory management standards.
- Capital at risk represents the inventory value of slow-moving and dead-stock products. It does not mean that the entire amount will necessarily be lost.
- Some synthetic records contain sales dates earlier than their recorded product launch dates. This inconsistency may affect the interpretation of individual products' sales history.
- The analysis uses a single inventory snapshot and does not currently model inventory changes over time.
- Stock cover is based on average monthly demand over the previous 365 days and may not reflect seasonality.

## 10. Conclusion

The project demonstrates how Python, Pandas and NumPy can be used to convert raw inventory and sales data into useful business insights.

The analysis identified that 70.89% of the inventory value was tied up in slow-moving or dead stock in the sample dataset. It also highlighted the categories and products contributing most to this exposure and generated suggested actions to support inventory management.

The system provides a foundation for more advanced inventory analytics, such as demand forecasting, reorder planning and historical inventory trend analysis.