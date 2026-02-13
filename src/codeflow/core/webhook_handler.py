"""Handle GitHub webhook events."""

import logging
from typing import Any

from ..agents.rag_code_analyzer import RAGCodeAnalyzer

logger = logging.getLogger(__name__)


class WebhookHandler:
    """Processes GitHub webhook events with RAG-enhanced analysis."""

    def __init__(self) -> None:
        """Initialize with RAG analyzer."""
        self.code_analyzer = RAGCodeAnalyzer()
        logger.info("WebhookHandler initialized with RAG analyzer")

    async def handle_pull_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Handle pull request webhook events.

        Args:
            payload: GitHub webhook payload

        Returns:
            Processing result
        """
        action = payload.get("action", "unknown")
        pr_number = payload.get("number", 0)

        logger.info(f"Processing PR #{pr_number} (action: {action})")

        # Only analyze when PR is opened or updated
        if action not in ["opened", "synchronize"]:
            return {
                "status": "skipped",
                "reason": f"Action '{action}' does not require analysis",
            }

        # Extract PR details
        pr_data = payload.get("pull_request", {})
        title = pr_data.get("title", "")
        author = pr_data.get("user", {}).get("login", "unknown")

        logger.info(f"PR #{pr_number}: '{title}' by @{author}")

        # Sample code (in Week 4 we'll fetch real PR diff from GitHub)
        sample_code = """
def process_payment(user_id, amount):
    query = f"UPDATE accounts SET balance = balance - {amount} WHERE id = {user_id}"
    db.execute(query)
    return {"status": "success"}
"""

        # Run RAG-enhanced analysis
        analysis_result = await self.code_analyzer.process(
            {
                "code": sample_code,
                "language": "python",
            }
        )

        # Format response
        return {
            "status": "analyzed",
            "pr_number": pr_number,
            "pr_title": title,
            "author": author,
            "analysis": analysis_result,
            "rag_learning": {
                "patterns_found": analysis_result.get("rag_context", {}).get(
                    "similar_patterns_found", 0
                ),
                "learning_from_history": True,
            },
        }
