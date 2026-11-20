
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


# ============================================================
# CHART CONFIGURATION
# ============================================================

CHART_DIR = Path("charts")


def prepare_chart_directory():
    """Create the charts folder if it does not exist."""
    CHART_DIR.mkdir(parents=True, exist_ok=True)


def format_inr(value):
    """Format values using Indian number grouping."""
    return f"₹{value:,.0f}"


# ============================================================
# 1. INVENTORY STATUS DONUT CHART
# ============================================================

def plot_inventory_status(inventory_summary):
    """Visualise product distribution by inventory status."""

    prepare_chart_directory()

    data = inventory_summary[
        inventory_summary["product_count"] > 0
    ]

    labels = data["stock_status"]
    values = data["product_count"]

    fig, ax = plt.subplots(figsize=(10, 7))

    wedges, texts, autotexts = ax.pie(
        values,
        labels=None,
        autopct="%1.1f%%",
        startangle=90,
        pctdistance=0.78,
        wedgeprops={"width": 0.42, "edgecolor": "white"},
        textprops={"fontsize": 10}
    )

    for text in autotexts:
        text.set_fontsize(10)
        text.set_fontweight("bold")

    ax.legend(
        wedges,
        labels,
        title="Inventory Status",
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        fontsize=10
    )

    ax.set_title(
        "Inventory Status Distribution",
        fontsize=15,
        fontweight="bold",
        pad=20
    )

    ax.axis("equal")

    fig.tight_layout()

    fig.savefig(
        CHART_DIR / "inventory_status.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)


# ============================================================
# 2. CATEGORY-WISE CAPITAL AT RISK
# ============================================================

def plot_category_risk(category_summary):
    """Show capital at risk across product categories."""

    prepare_chart_directory()

    data = category_summary.sort_values(
        "capital_at_risk",
        ascending=True
    )

    fig, ax = plt.subplots(figsize=(12, 8))

    bars = ax.barh(
        data["category"],
        data["capital_at_risk"]
    )

    ax.set_title(
        "Capital at Risk by Product Category",
        fontsize=15,
        fontweight="bold",
        pad=18
    )

    ax.set_xlabel("Capital at Risk (₹)", labelpad=10)
    ax.set_ylabel("Product Category", labelpad=10)

    # Place currency values at the end of each bar.
    ax.bar_label(
        bars,
        labels=[
            format_inr(value)
            for value in data["capital_at_risk"]
        ],
        padding=6,
        fontsize=9
    )

    ax.xaxis.set_major_formatter(
        FuncFormatter(lambda value, position: f"₹{value:,.0f}")
    )

    ax.set_xlim(
        0,
        data["capital_at_risk"].max() * 1.25
    )

    ax.tick_params(axis="y", labelsize=9)
    ax.tick_params(axis="x", labelsize=9)

    ax.grid(
        axis="x",
        linestyle="--",
        alpha=0.3
    )

    ax.set_axisbelow(True)

    fig.tight_layout()

    fig.savefig(
        CHART_DIR / "category_risk.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)


# ============================================================
# 3. INVENTORY VALUE BY STOCK STATUS
# ============================================================

def plot_inventory_value(inventory_summary):
    """Compare inventory value across stock statuses."""

    prepare_chart_directory()

    data = inventory_summary.sort_values(
        "inventory_value",
        ascending=False
    )

    fig, ax = plt.subplots(figsize=(11, 7))

    bars = ax.bar(
        data["stock_status"],
        data["inventory_value"]
    )

    ax.set_title(
        "Inventory Value by Stock Status",
        fontsize=15,
        fontweight="bold",
        pad=18
    )

    ax.set_xlabel("Stock Status", labelpad=10)
    ax.set_ylabel("Inventory Value (₹)", labelpad=10)

    # Display the value above each bar.
    ax.bar_label(
        bars,
        labels=[
            format_inr(value)
            for value in data["inventory_value"]
        ],
        padding=5,
        fontsize=9
    )

    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda value, position: f"₹{value:,.0f}")
    )

    ax.set_ylim(
        0,
        data["inventory_value"].max() * 1.25
    )

    plt.xticks(
        rotation=20,
        ha="right",
        fontsize=9
    )

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.3
    )

    ax.set_axisbelow(True)

    fig.tight_layout()

    fig.savefig(
        CHART_DIR / "inventory_value.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)


# ============================================================
# 4. TOP 5 DEAD STOCK PRODUCTS
# ============================================================

def plot_dead_stock(dead_stock):
    """Show the five dead stock products with the highest value."""

    prepare_chart_directory()

    if dead_stock.empty:
        print("No dead stock products available for charting.")
        return

    data = dead_stock.nlargest(
        5,
        "inventory_value"
    ).sort_values(
        "inventory_value",
        ascending=True
    )

    fig, ax = plt.subplots(figsize=(12, 7))

    bars = ax.barh(
        data["product_name"],
        data["inventory_value"]
    )

    ax.set_title(
        "Top 5 Dead Stock Products by Inventory Value",
        fontsize=15,
        fontweight="bold",
        pad=18
    )

    ax.set_xlabel("Inventory Value (₹)", labelpad=10)
    ax.set_ylabel("Product", labelpad=10)

    # Place currency values at the end of each bar.
    ax.bar_label(
        bars,
        labels=[
            format_inr(value)
            for value in data["inventory_value"]
        ],
        padding=6,
        fontsize=9
    )

    ax.xaxis.set_major_formatter(
        FuncFormatter(lambda value, position: f"₹{value:,.0f}")
    )

    ax.set_xlim(
        0,
        data["inventory_value"].max() * 1.3
    )

    ax.tick_params(axis="y", labelsize=9)

    ax.grid(
        axis="x",
        linestyle="--",
        alpha=0.3
    )

    ax.set_axisbelow(True)

    fig.tight_layout()

    fig.savefig(
        CHART_DIR / "dead_stock.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)


# ============================================================
# 5. GENERATE ALL CHARTS
# ============================================================

def generate_all_charts(
    inventory_summary,
    category_summary,
    dead_stock
):
    """Generate and save all inventory analysis charts."""

    plot_inventory_status(inventory_summary)
    plot_category_risk(category_summary)
    plot_inventory_value(inventory_summary)
    plot_dead_stock(dead_stock)

    print("\nAll charts generated successfully.")
    print("Chart files saved in the charts/ folder.")
