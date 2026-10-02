# Product Price Compare Agent

This project implements an agentic Python application for comparing product prices, stock prices, and asking follow-up questions in a chat-like interface.

## Features

- OpenAI Agents-based reasoning layer
- Product and stock comparison tools
- Contextual memory support via LangGraph and Neo4j (optional)
- Streamlit user interface
- Secrets stored in a local `.env` file

## Setup

1. Create a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your keys.
4. Run the app:
   ```bash
   streamlit run streamlit_app.py
   ```

## Example prompts

- Compare the price of a MacBook Air and Dell XPS 13.
- What is the cheapest option for a noise cancelling headset?
- Compare AAPL and MSFT against the market average.
- Which products are under $400?

## Notes

- If `OPENAI_API_KEY` is not configured, the app falls back to a local intelligence demo mode so you can still test the workflow.
- Neo4j and LangGraph are optional and only activated when the corresponding environment variables are set.
