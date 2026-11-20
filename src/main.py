from charts import generate_all_charts

from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# 1. PROJECT CONFIGURATION
# ============================================================

ANALYSIS_DATE = pd.Timestamp("2026-11-20")

DATA_DIR = Path("data")
OUTPUT_DIR = Path("outputs")

PRODUCTS_FILE = DATA_DIR / "products.csv"
SALES_FILE = DATA_DIR / "sales.csv"
INVENTORY_FILE = DATA_DIR / "inventory_snapshot.csv"


# ============================================================
# 2. LOAD DATA
# ============================================================

def load_data():
    """Load the three source datasets."""

    products_df = pd.read_csv(PRODUCTS_FILE)
    sales_df = pd.read_csv(SALES_FILE)
    inventory_df = pd.read_csv(INVENTORY_FILE)

    # Convert date columns into datetime format.
    sales_df["sale_date"] = pd.to_datetime(sales_df["sale_date"])
    inventory_df["snapshot_date"] = pd.to_datetime(
        inventory_df["snapshot_date"]
    )
    products_df["launch_date"] = pd.to_datetime(
        products_df["launch_date"]
    )

    return products_df, sales_df, inventory_df


# ============================================================
# 3. CALCULATE SALES METRICS
# ============================================================

def calculate_sales_metrics(sales_df, analysis_date):
    """Calculate sales activity over the analysis periods."""

    start_90 = analysis_date - pd.Timedelta(days=90)
    start_365 = analysis_date - pd.Timedelta(days=365)

    # Exclude transactions occurring after the analysis date.
    sales_to_date = sales_df[
        sales_df["sale_date"] <= analysis_date
    ].copy()

    # Calculate units sold during the last 90 days.
    sales_90 = (
        sales_to_date[
            sales_to_date["sale_date"] > start_90
        ]
        .groupby("sku")["quantity_sold"]
        .sum()
        .rename("sales_last_90_days")
    )

    # Calculate units sold during the last 365 days.
    sales_365 = (
        sales_to_date[
            sales_to_date["sale_date"] >= start_365
        ]
        .groupby("sku")["quantity_sold"]
        .sum()
        .rename("sales_last_365_days")
    )

    # Identify the most recent sale date for each product.
    last_sale = (
        sales_to_date
        .groupby("sku")["sale_date"]
        .max()
        .rename("last_sale_date")
    )

    # Combine all sales metrics into one DataFrame.
    sales_metrics = pd.concat(
        [sales_90, sales_365, last_sale],
        axis=1
    ).fillna({
        "sales_last_90_days": 0,
        "sales_last_365_days": 0
    })

    sales_metrics = sales_metrics.rename_axis(
        "sku"
    ).reset_index()

    return sales_metrics


# ============================================================
# 4. BUILD PRODUCT ANALYSIS
# ============================================================

def build_product_analysis(
    products_df,
    inventory_df,
    sales_metrics,
    analysis_date
):
    """Combine product, inventory and sales information."""

    # Join product information with the latest inventory snapshot.
    product_analysis = products_df.merge(
        inventory_df,
        on="sku",
        how="left"
    )

    # Add sales performance metrics.
    product_analysis = product_analysis.merge(
        sales_metrics,
        on="sku",
        how="left"
    )

    # Replace missing sales values with zero.
    product_analysis["sales_last_90_days"] = (
        product_analysis["sales_last_90_days"].fillna(0)
    )

    product_analysis["sales_last_365_days"] = (
        product_analysis["sales_last_365_days"].fillna(0)
    )

    # Calculate product age in days.
    product_analysis["days_since_launch"] = (
        analysis_date - product_analysis["launch_date"]
    ).dt.days

    # Calculate days since the most recent sale.
    product_analysis["days_since_last_sale"] = (
        analysis_date - product_analysis["last_sale_date"]
    ).dt.days

    # Calculate average monthly demand using the last 365 days.
    product_analysis["average_monthly_demand"] = (
        product_analysis["sales_last_365_days"] / 12
    )

    # Calculate how many months current stock can cover.
    # Products with no recorded demand receive NaN.
    product_analysis["stock_cover_months"] = np.where(
        product_analysis["average_monthly_demand"] > 0,
        product_analysis["current_stock"]
        / product_analysis["average_monthly_demand"],
        np.nan
    )

    # Calculate the financial value of current inventory.
    product_analysis["inventory_value"] = (
        product_analysis["current_stock"]
        * product_analysis["unit_cost"]
    )

    return product_analysis


# ============================================================
# 5. CLASSIFY INVENTORY
# ============================================================

def classify_inventory(product_analysis):
    """Assign an inventory movement status to each product."""

    conditions = [
        # No stock currently available.
        product_analysis["current_stock"] == 0,

        # No sales for at least 180 days.
        product_analysis["days_since_last_sale"] >= 180,

        # No recorded sales and product is at least 180 days old.
        (
            product_analysis["last_sale_date"].isna()
            & (product_analysis["days_since_launch"] >= 180)
        ),

        # No recorded sales and product is less than 90 days old.
        (
            product_analysis["last_sale_date"].isna()
            & (product_analysis["days_since_launch"] < 90)
        ),

        # No recorded sales and product age is between 90 and 179 days.
        product_analysis["last_sale_date"].isna(),

        # Last sale occurred between 90 and 179 days ago.
        (
            (product_analysis["days_since_last_sale"] >= 90)
            & (product_analysis["days_since_last_sale"] < 180)
        ),

        # Stock covers more than three months of average demand.
        product_analysis["stock_cover_months"] > 3,

        # Recent sales activity and stock cover of three months or less.
        (
            (product_analysis["days_since_last_sale"] < 90)
            & (product_analysis["stock_cover_months"] <= 3)
        )
    ]

    statuses = [
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
        statuses,
        default="Review Required"
    )

    return product_analysis


# ============================================================
# 6. CALCULATE FINANCIAL METRICS
# ============================================================

def calculate_financial_metrics(product_analysis):
    """Measure total inventory value and capital at risk."""

    total_inventory_value = product_analysis[
        "inventory_value"
    ].sum()

    # Capital at risk includes slow-moving and dead stock.
    risk_statuses = ["Slow Moving", "Dead Stock"]

    capital_at_risk = product_analysis.loc[
        product_analysis["stock_status"].isin(risk_statuses),
        "inventory_value"
    ].sum()

    risk_percentage = (
        capital_at_risk / total_inventory_value * 100
        if total_inventory_value > 0
        else 0
    )

    return (
        total_inventory_value,
        capital_at_risk,
        risk_percentage
    )


# ============================================================
# 7. CREATE BUSINESS REPORTS
# ============================================================

def create_inventory_summary(product_analysis):
    """Summarise inventory value by movement status."""

    inventory_summary = (
        product_analysis
        .groupby("stock_status")
        .agg(
            inventory_value=("inventory_value", "sum"),
            product_count=("sku", "count")
        )
        .reset_index()
    )

    total_value = inventory_summary["inventory_value"].sum()

    inventory_summary["inventory_share_percentage"] = (
        inventory_summary["inventory_value"]
        / total_value * 100
        if total_value > 0
        else 0
    )

    inventory_summary = inventory_summary.sort_values(
        "inventory_value",
        ascending=False
    )

    return inventory_summary


def create_category_summary(product_analysis):
    """Identify product categories with the highest inventory risk."""

    category_summary = (
        product_analysis
        .groupby("category")
        .agg(
            total_inventory_value=("inventory_value", "sum"),
            product_count=("sku", "count")
        )
        .reset_index()
    )

    # Calculate capital at risk separately for each category.
    risk_by_category = (
        product_analysis[
            product_analysis["stock_status"].isin(
                ["Slow Moving", "Dead Stock"]
            )
        ]
        .groupby("category")["inventory_value"]
        .sum()
        .rename("capital_at_risk")
    )

    category_summary = category_summary.merge(
        risk_by_category,
        on="category",
        how="left"
    )

    category_summary["capital_at_risk"] = (
        category_summary["capital_at_risk"].fillna(0)
    )

    # Calculate the percentage of each category's value at risk.
    category_summary["risk_percentage"] = np.where(
        category_summary["total_inventory_value"] > 0,
        category_summary["capital_at_risk"]
        / category_summary["total_inventory_value"] * 100,
        0
    )

    return category_summary.sort_values(
        "capital_at_risk",
        ascending=False
    )


def create_dead_stock_report(product_analysis):
    """Return dead stock products ranked by inventory value."""

    dead_stock = product_analysis[
        product_analysis["stock_status"] == "Dead Stock"
    ].copy()

    dead_stock = dead_stock.sort_values(
        "inventory_value",
        ascending=False
    )

    report_columns = [
        "sku",
        "product_name",
        "category",
        "current_stock",
        "days_since_last_sale",
        "inventory_value"
    ]

    return dead_stock[report_columns]


def create_recommendations(product_analysis):
    """Attach a business recommendation to each product."""

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

    return product_analysis


# ============================================================
# 8. FORMAT AND DISPLAY TERMINAL REPORTS
# ============================================================

def format_currency(value):
    """Format financial values using Indian Rupee notation."""

    return f"₹{value:,.2f}"


def display_business_reports(
    analysis_date,
    product_analysis,
    total_inventory_value,
    capital_at_risk,
    risk_percentage,
    inventory_summary,
    category_summary,
    dead_stock
):
    """Display the main business findings in the terminal."""

    print("\n" + "=" * 65)
    print("       SLOW-MOVING AND DEAD STOCK ANALYSIS SYSTEM")
    print("=" * 65)

    print(f"\nAnalysis Date       : {analysis_date:%d %b %Y}")
    print(f"Products Analysed   : {len(product_analysis)}")

    print("\n" + "-" * 65)
    print("1. INVENTORY FINANCIAL OVERVIEW")
    print("-" * 65)

    print(
        f"Total Inventory Value : "
        f"{format_currency(total_inventory_value)}"
    )
    print(
        f"Capital at Risk       : "
        f"{format_currency(capital_at_risk)}"
    )
    print(
        f"Capital at Risk (%)   : "
        f"{risk_percentage:.2f}%"
    )

    print("\n" + "-" * 65)
    print("2. INVENTORY STATUS SUMMARY")
    print("-" * 65)

    status_display = inventory_summary.copy()

    status_display["inventory_value"] = (
        status_display["inventory_value"].apply(format_currency)
    )

    status_display["inventory_share_percentage"] = (
        status_display["inventory_share_percentage"].map(
            lambda value: f"{value:.2f}%"
        )
    )

    print(status_display.to_string(index=False))

    print("\n" + "-" * 65)
    print("3. CATEGORY-WISE INVENTORY RISK")
    print("-" * 65)

    category_display = category_summary.copy()

    category_display["total_inventory_value"] = (
        category_display["total_inventory_value"].apply(
            format_currency
        )
    )

    category_display["capital_at_risk"] = (
        category_display["capital_at_risk"].apply(
            format_currency
        )
    )

    category_display["risk_percentage"] = (
        category_display["risk_percentage"].map(
            lambda value: f"{value:.2f}%"
        )
    )

    print(category_display.to_string(index=False))

    print("\n" + "-" * 65)
    print("4. TOP 5 DEAD STOCK PRODUCTS")
    print("-" * 65)

    if dead_stock.empty:
        print("No dead stock products identified.")
    else:
        dead_stock_display = dead_stock.head(5).copy()

        dead_stock_display["inventory_value"] = (
            dead_stock_display["inventory_value"].apply(
                format_currency
            )
        )

        print(dead_stock_display.to_string(index=False))

    print("\n" + "-" * 65)
    print("5. PRODUCT-LEVEL RECOMMENDATIONS")
    print("-" * 65)

    recommendation_display = product_analysis[
        [
            "sku",
            "product_name",
            "stock_status",
            "recommendation"
        ]
    ]

    print(recommendation_display.to_string(index=False))


# ============================================================
# 9. EXPORT CSV REPORTS
# ============================================================

def export_reports(
    product_analysis,
    inventory_summary,
    category_summary,
    dead_stock
):
    """Export all business reports to the outputs folder."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Export the complete product-level analysis.
    product_analysis.to_csv(
        OUTPUT_DIR / "product_analysis_report.csv",
        index=False
    )

    # Export inventory value grouped by stock status.
    inventory_summary.to_csv(
        OUTPUT_DIR / "inventory_summary_report.csv",
        index=False
    )

    # Export category-level inventory risk.
    category_summary.to_csv(
        OUTPUT_DIR / "category_risk_report.csv",
        index=False
    )

    # Export the dead stock product list.
    dead_stock.to_csv(
        OUTPUT_DIR / "dead_stock_report.csv",
        index=False
    )

    print("\n" + "-" * 65)
    print("6. REPORT EXPORT")
    print("-" * 65)

    print("The following reports were successfully exported:")

    print(f"1. {OUTPUT_DIR / 'product_analysis_report.csv'}")
    print(f"2. {OUTPUT_DIR / 'inventory_summary_report.csv'}")
    print(f"3. {OUTPUT_DIR / 'category_risk_report.csv'}")
    print(f"4. {OUTPUT_DIR / 'dead_stock_report.csv'}")


# ============================================================
# 10. MAIN PROGRAM
# ============================================================

def main():
    """Run the complete slow-moving and dead stock analysis."""

    # Load the source datasets.
    products_df, sales_df, inventory_df = load_data()

    # Calculate sales performance metrics.
    sales_metrics = calculate_sales_metrics(
        sales_df,
        ANALYSIS_DATE
    )

    # Combine product, inventory and sales information.
    product_analysis = build_product_analysis(
        products_df,
        inventory_df,
        sales_metrics,
        ANALYSIS_DATE
    )

    # Classify products according to inventory movement.
    product_analysis = classify_inventory(product_analysis)

    # Calculate total inventory value and capital at risk.
    (
        total_inventory_value,
        capital_at_risk,
        risk_percentage
    ) = calculate_financial_metrics(product_analysis)

    # Create the business reports.
    inventory_summary = create_inventory_summary(
        product_analysis
    )

    category_summary = create_category_summary(
        product_analysis
    )

    dead_stock = create_dead_stock_report(
        product_analysis
    )

    # Generate product-level business recommendations.
    product_analysis = create_recommendations(
        product_analysis
    )

    # Display the business findings.
    display_business_reports(
        ANALYSIS_DATE,
        product_analysis,
        total_inventory_value,
        capital_at_risk,
        risk_percentage,
        inventory_summary,
        category_summary,
        dead_stock
    )

    # Export the reports as CSV files.
    export_reports(
        product_analysis,
        inventory_summary,
        category_summary,
        dead_stock
    )

    # Generate visual reports.
    generate_all_charts(
        inventory_summary,
        category_summary,
        dead_stock
    )

    print("\n" + "=" * 65)
    print("ANALYSIS COMPLETED SUCCESSFULLY")
    print("=" * 65 + "\n")


# Run the program.
if __name__ == "__main__":
    main()
