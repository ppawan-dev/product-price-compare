from __future__ import annotations

from agents import function_tool

from app.data import PRODUCT_CATALOG, STOCK_CATALOG


@function_tool
def search_products(query: str) -> list[dict]:
    """Search product catalog by keyword and return matching items."""
    normalized = query.lower().strip()
    if not normalized:
        return PRODUCT_CATALOG

    matches = []
    for product in PRODUCT_CATALOG:
        haystack = " ".join(
            [
                product["name"],
                product["category"],
            ]
        ).lower()
        if normalized in haystack:
            matches.append(product)
    return matches


@function_tool
def compare_product_prices(product_names: list[str]) -> list[dict]:
    """Compare a list of product names and return price summary details."""
    if not product_names:
        return []

    result = []
    for product_name in product_names:
        for product in PRODUCT_CATALOG:
            if product["name"].lower() == product_name.lower():
                result.append(product)
                break
    return result


@function_tool
def get_stock_snapshot(symbols: list[str]) -> list[dict]:
    """Return sample stock market values for selected symbols."""
    if not symbols:
        return STOCK_CATALOG

    result = []
    for symbol in symbols:
        for stock in STOCK_CATALOG:
            if stock["symbol"].lower() == symbol.lower():
                result.append(stock)
                break
    return result


@function_tool
def get_product_lowest_price(category: str | None = None) -> dict | None:
    """Return the lowest priced item in a category, or all items if category is not specified."""
    candidate_list = PRODUCT_CATALOG
    if category:
        candidate_list = [item for item in PRODUCT_CATALOG if item["category"].lower() == category.lower()]
    if not candidate_list:
        return None
    cheapest = min(candidate_list, key=lambda item: item["price"])
    return cheapest
