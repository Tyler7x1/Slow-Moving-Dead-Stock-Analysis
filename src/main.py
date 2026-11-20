import pandas as pd
import numpy as np

import os
os.makedirs("outputs", exist_ok=True)

products_df = pd.read_csv("data/products.csv")
sales_df = pd.read_csv("data/sales.csv")
inventory_df = pd.read_csv("data/inventory_snapshot.csv")

sales_df["sale_date"] = pd.to_datetime(sales_df["sale_date"])
inventory_df["snapshot_date"] = pd.to_datetime(inventory_df["snapshot_date"])

analysis_date = inventory_df["snapshot_date"].max()

start_90 = analysis_date - pd.Timedelta(days=90)
start_365 = analysis_date - pd.Timedelta(days=365)

sale_90 = sales_df.loc[(sales_df["sale_date"] > start_90) & (sales_df["sale_date"] <= analysis_date)]
sale_90_days = sale_90.groupby("sku")["quantity_sold"].sum()
sale_365 = sales_df.loc[(sales_df["sale_date"] >= start_365) & (sales_df["sale_date"] <= analysis_date)]
sale_365_days = sale_365.groupby("sku")["quantity_sold"].sum()

average_monthly_demand = sale_365_days / 12

last_sale = sales_df.groupby("sku")["sale_date"].max().reset_index()
products_df["launch_date"] = pd.to_datetime(products_df["launch_date"])
product_analysis = products_df.merge(last_sale, on="sku", how="left")

product_analysis["days_since_launch"] = (
    analysis_date - product_analysis["launch_date"]
).dt.days

product_analysis["days_since_last_sale"] = (analysis_date - product_analysis["sale_date"]).dt.days

product_analysis = product_analysis.merge(inventory_df[["sku", "current_stock"]], on="sku", how="left")
product_analysis = product_analysis.merge(average_monthly_demand.rename("average_monthly_demand"), on="sku", how="left")
product_analysis["stock_cover"] = np.where(product_analysis["average_monthly_demand"] > 0, product_analysis["current_stock"] / product_analysis["average_monthly_demand"], np.nan)

product_analysis["inventory_value"] = product_analysis["current_stock"] * product_analysis["unit_cost"]
total_inventory_value = product_analysis["inventory_value"].sum()

top_inventory = product_analysis.sort_values(by="inventory_value", ascending=False)

conditions = [
    product_analysis["current_stock"] == 0,
    product_analysis["days_since_last_sale"] >= 180,
    product_analysis["days_since_last_sale"].isna() &
    (product_analysis["days_since_launch"] >= 180),
    product_analysis["days_since_last_sale"].isna() &
    (product_analysis["days_since_launch"] < 90),
    product_analysis["days_since_last_sale"].isna(),
    product_analysis["days_since_last_sale"].between(90, 179),
    product_analysis["stock_cover"] > 3,
    product_analysis["days_since_last_sale"].between(0, 89) &
    (product_analysis["stock_cover"] <= 3)
]

choices = [
    "Out of Stock",
    "Dead Stock",
    "Dead Stock",
    "New Product",
    "Insufficient History",
    "Slow Moving",
    "Slow Moving",
    "Fast Moving"
]

product_analysis["stock_status"] = np.select(
    conditions,
    choices,
    default="Review Required"
)

product_analysis["stock_status"].value_counts()

print(product_analysis[
    ["sku", "product_name", "days_since_last_sale",
     "days_since_launch", "current_stock",
     "stock_cover", "inventory_value", "stock_status"]
])

status_summary = product_analysis.groupby("stock_status")["inventory_value"].sum()
print(status_summary)

capital_at_risk = product_analysis.loc[
    product_analysis["stock_status"].isin(["Slow Moving", "Dead Stock"]), "inventory_value"
    ].sum()

total_inventory_value = product_analysis["inventory_value"].sum()
risk_percentage = (capital_at_risk / total_inventory_value) * 100

print(f"Total Inventory Value: ₹{total_inventory_value:,.2f}")
print(f"Capital at Risk: ₹{capital_at_risk:,.2f}")
print(f"Capital at Risk (%): {risk_percentage:.2f}%")

product_analysis["capital_at_risk"] = np.where(
    product_analysis["stock_status"].isin(
        ["Slow Moving", "Dead Stock"]
    ),
    product_analysis["inventory_value"],
    0
)

category_summary = product_analysis.groupby("category").agg(
    total_inventory_value=("inventory_value", "sum"),
    capital_at_risk=("capital_at_risk", "sum"),
    product_count=("sku", "count")
).reset_index()

category_summary["risk_percentage"] = (
    category_summary["capital_at_risk"]
    / category_summary["total_inventory_value"]
) * 100

category_summary = category_summary.sort_values(
    by="capital_at_risk",
    ascending=False
)

print(category_summary)

dead_stock = product_analysis[
    product_analysis["stock_status"] == "Dead Stock"
]

dead_stock.sort_values(by="inventory_value", ascending=False)

print(dead_stock[
    ["sku", "product_name", "category",
     "current_stock", "days_since_last_sale",
     "inventory_value"]
].head(5))

recommendations = {
    "Fast Moving": "Maintain stock and monitor demand",
    "Slow Moving": "Review pricing and consider promotions",
    "Dead Stock": "Consider clearance, bundling or liquidation",
    "New Product": "Monitor early sales performance",
    "Out of Stock": "Review replenishment requirements",
    "Insufficient History": "Collect more sales data",
    "Review Required": "Investigate product classification"
}

product_analysis["recommendation"] = (
    product_analysis["stock_status"].map(recommendations)
)

print(product_analysis[
    ["sku", "product_name", "stock_status",
     "inventory_value", "recommendation"]
])

product_analysis.to_csv(
    "outputs/product_analysis_report.csv",
    index=False
)

category_summary.to_csv(
    "outputs/category_risk_report.csv",
    index=False
)

inventory_summary = status_summary.reset_index()

inventory_summary.columns = [
    "stock_status",
    "inventory_value"
]

inventory_summary.to_csv(
    "outputs/inventory_summary_report.csv",
    index=False
)

dead_stock.to_csv(
    "outputs/dead_stock_report.csv",
    index=False
)