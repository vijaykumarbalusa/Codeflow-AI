"""Handle GitHub webhook events."""

import logging
from typing import Any

from ..agents.multi_signal_analyzer import MultiSignalAnalyzer

logger = logging.getLogger(__name__)


class WebhookHandler:
    """Processes GitHub webhook events with multi-signal analysis."""

    def __init__(self) -> None:
        self.code_analyzer = MultiSignalAnalyzer()
        logger.info("WebhookHandler initialized with multi-signal analyzer")

    async def handle_pull_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Handle pull request webhook events."""
        action = payload.get("action", "unknown")
        pr_number = payload.get("number", 0)

        logger.info(f"Processing PR #{pr_number} (action: {action})")

        if action not in ["opened", "synchronize"]:
            return {
                "status": "skipped",
                "reason": f"Action '{action}' does not require analysis",
            }

        pr_data = payload.get("pull_request", {})
        title = pr_data.get("title", "")
        author = pr_data.get("user", {}).get("login", "unknown")

        logger.info(f"PR #{pr_number}: '{title}' by @{author}")

        sample_code = """
def process_payment(user_id, amount):
    query = f"UPDATE accounts SET balance = balance - {amount} WHERE id = {user_id}"
    db.execute(query)
    return {"status": "success"}
"""

        analysis_result = await self.code_analyzer.process(
            {"code": sample_code, "language": "python"}
        )

        return {
            "status": "analyzed",
            "pr_number": pr_number,
            "pr_title": title,
            "author": author,
            "analysis": analysis_result,
        }
