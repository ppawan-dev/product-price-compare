import json
from pathlib import Path
from typing import Any

from app.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, USE_NEO4J_MEMORY


class ConversationMemory:
    """Local conversational memory with optional Neo4j integration."""

    def __init__(self, history_path: str | None = None) -> None:
        self.history_path = Path(history_path) if history_path else Path(__file__).resolve().parent.parent / "conversation_memory.json"
        self._history = self._load_history()

    def _load_history(self) -> list[dict[str, Any]]:
        if self.history_path.exists():
            try:
                with self.history_path.open("r", encoding="utf-8") as file:
                    data = json.load(file)
                    return data if isinstance(data, list) else []
            except json.JSONDecodeError:
                return []
        return []

    def _save_history(self) -> None:
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        with self.history_path.open("w", encoding="utf-8") as file:
            json.dump(self._history, file, indent=2)

    def add_turn(self, user_input: str, response: str) -> None:
        entry = {"user": user_input, "assistant": response}
        self._history.append(entry)
        self._save_history()

        if USE_NEO4J_MEMORY and NEO4J_URI and NEO4J_USERNAME and NEO4J_PASSWORD:
            try:
                from neo4j import GraphDatabase

                driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
                with driver.session() as session:
                    session.run(
                        "MERGE (u:User {id: 'default'}) "
                        "CREATE (m:Memory {user_input: $user_input, response: $response, created_at: timestamp()})-[:ABOUT]->(u)",
                        user_input=user_input,
                        response=response,
                    )
                driver.close()
            except Exception:
                # Fallback to local storage silently if Neo4j is unavailable.
                pass

    def get_recent_context(self, limit: int = 5) -> list[dict[str, Any]]:
        return list(reversed(self._history[-limit:]))
