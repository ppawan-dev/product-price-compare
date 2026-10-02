from __future__ import annotations

import asyncio
from typing import Any

from agents import Agent, Runner

from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.data import PRODUCT_CATALOG, STOCK_CATALOG
from app.memory import ConversationMemory
from app.tools import compare_product_prices, get_product_lowest_price, get_stock_snapshot, search_products

SYSTEM_PROMPT = """You are a helpful AI shopping and market assistant.

Your responsibilities:
- Compare product prices using the provided product catalog.
- Compare stock prices when asked.
- Explain the cheapest or best value option.
- Keep answers concise but useful.
- Use the available tools when relevant.
- If no tool is needed, respond based on the available context.
"""


def _fallback_answer(question: str, memory: ConversationMemory | None = None) -> str:
    q = question.lower()
    products = []
    for token in ["macbook", "xps", "headphones", "watch", "keyboard", "tv"]:
        if token in q:
            for product in PRODUCT_CATALOG:
                if token in product["name"].lower() or token in product["category"].lower():
                    products.append(product)

    if "compare" in q or "cheapest" in q or "best" in q:
        if products:
            ordered = sorted(products, key=lambda item: item["price"])
            cheapest = ordered[0]
            return (
                f"Here is the comparison summary: the lowest-cost option is {cheapest['name']} at ${cheapest['price']:.2f}. "
                f"Other options in the same category include {', '.join(item['name'] for item in ordered[1:4])}."
            )

        if "stock" in q or "aapl" in q or "msft" in q or "nvda" in q:
            symbols = [symbol["symbol"] for symbol in STOCK_CATALOG if symbol["symbol"].lower() in q]
            if not symbols:
                symbols = [stock["symbol"] for stock in STOCK_CATALOG[:3]]
            selected = [stock for stock in STOCK_CATALOG if stock["symbol"] in symbols]
            return (
                "Market snapshot: " + "; ".join(
                    f"{stock['symbol']} ${stock['price']:.2f} ({stock['change_pct']:+.2f}%)" for stock in selected
                )
            )

        cheapest = min(PRODUCT_CATALOG, key=lambda item: item["price"])
        return f"The cheapest available item is {cheapest['name']} at ${cheapest['price']:.2f}."

    if "product" in q or "price" in q:
        matches = [p for p in PRODUCT_CATALOG if any(word in q for word in [p["name"].lower(), p["category"].lower()])]
        if matches:
            return "I found these products: " + "; ".join(f"{p['name']} (${p['price']:.2f})" for p in matches)

    return "I can compare products or stock prices. Try asking: 'Compare MacBook Air and Dell XPS 13' or 'Compare AAPL and MSFT'."


def create_agent() -> Agent:
    return Agent(
        name="PricingAssistant",
        instructions=SYSTEM_PROMPT,
        model=OPENAI_MODEL if OPENAI_API_KEY else "gpt-4o-mini",
        tools=[search_products, compare_product_prices, get_stock_snapshot, get_product_lowest_price],
    )


def run_agent(question: str, memory: ConversationMemory | None = None) -> dict[str, Any]:
    if memory is None:
        memory = ConversationMemory()

    if not OPENAI_API_KEY:
        answer = _fallback_answer(question, memory)
        memory.add_turn(question, answer)
        return {"answer": answer, "mode": "fallback", "context": memory.get_recent_context()}

    agent = create_agent()
    prompt = (
        f"Conversation context:\n{memory.get_recent_context()}\n\n"
        f"User query: {question}"
    )

    try:
        result = asyncio.run(Runner.run(agent, prompt))
        answer = result.final_output
    except Exception:
        answer = _fallback_answer(question, memory)

    memory.add_turn(question, answer)
    return {"answer": answer, "mode": "agent", "context": memory.get_recent_context()}
