import pandas as pd
import numpy as np

products_df = pd.read_csv("data/raw/products.csv")
sales_df = pd.read_csv("data/raw/sales.csv")
inventory_df = pd.read_csv("data/raw/inventory_snapshot.csv")

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
product_analysis = products_df.merge(last_sale, on="sku", how="left")
product_analysis["days_since_last_sale"] = (analysis_date - product_analysis["sale_date"]).dt.days

product_analysis = product_analysis.merge(inventory_df[["sku", "current_stock"]], on="sku", how="left")
product_analysis = product_analysis.merge(average_monthly_demand.rename("average_monthly_demand"), on="sku", how="left")
product_analysis["stock_cover"] = np.where( product_analysis["average_monthly_demand"] > 0, product_analysis["current_stock"] / product_analysis["average_monthly_demand"], np.nan)