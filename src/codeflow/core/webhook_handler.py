"""
GitHub Webhook Handler
Processes webhook events from GitHub and triggers analysis
"""

import hashlib
import hmac
import time
from typing import Dict
from fastapi import HTTPException
import logging
from src.codeflow.core.config import get_settings
from src.codeflow.core.github_client import get_github_client
from src.codeflow.core.comment_formatter import CommentFormatter
from src.codeflow.agents.multi_signal_analyzer import MultiSignalAnalyzer

logger = logging.getLogger(__name__)
settings = get_settings()


class WebhookHandler:
    """Handles GitHub webhook events"""

    def __init__(self):
        self.github_client = get_github_client()
        self.analyzer = MultiSignalAnalyzer()
        self.formatter = CommentFormatter()

    def verify_signature(self, payload_body: bytes, signature_header: str) -> bool:
        """
        Verify GitHub webhook signature

        Args:
            payload_body: Raw request body
            signature_header: Value of X-Hub-Signature-256 header

        Returns:
            True if signature is valid, False otherwise
        """
        if not settings.github_webhook_secret:
            # If no secret configured, skip verification (for testing)
            logger.warning("Webhook secret not configured - skipping signature verification")
            return True

        # Compute HMAC
        secret = settings.github_webhook_secret.encode()
        computed = hmac.new(secret, payload_body, hashlib.sha256)
        expected_signature = f"sha256={computed.hexdigest()}"

        # Constant-time comparison
        return hmac.compare_digest(expected_signature, signature_header)

    async def handle_pull_request(self, event_data: Dict) -> Dict:
        """
        Handle pull request webhook event

        Args:
            event_data: Webhook payload

        Returns:
            Response data
        """
        action = event_data.get("action")

        # Only analyze on open and synchronize (new commits)
        if action not in ["opened", "synchronize"]:
            logger.info(f"Ignoring PR action: {action}")
            return {"status": "ignored", "reason": f"Action '{action}' not handled"}

        pr_data = event_data.get("pull_request", {})
        pr_number = pr_data.get("number")
        repo_data = event_data.get("repository", {})
        repo_full_name = repo_data.get("full_name")

        if not pr_number or not repo_full_name:
            raise HTTPException(status_code=400, detail="Missing required PR or repository data")

        logger.info(
            f"Processing PR webhook action={action} pr_number={pr_number} repo={repo_full_name}"
        )

        try:
            # Post initial "analyzing" comment
            initial_comment = self.formatter.format_analyzing_comment(pr_number)
            comment_obj = await self.github_client.post_pr_comment(
                repo_full_name, pr_number, initial_comment
            )
            comment_id = comment_obj.get("id")

            # Fetch PR diff
            logger.info(f"Fetching PR diff pr_number={pr_number}")
            diff = await self.github_client.get_pr_diff(repo_full_name, pr_number)

            # Extract code from diff
            code_changes = self.github_client.extract_code_from_diff(diff)

            if not code_changes:
                logger.warning(f"No code changes found in PR pr_number={pr_number}")
                final_comment = (
                    "## ✅ CodeFlow AI Analysis\n\n"
                    "No code changes detected in this PR.\n\n"
                    "---\n\n"
                    "*Analyzed by [CodeFlow AI](https://github.com/vijaykumarbalusa/Codeflow-AI)* 🤖"
                )

                await self.github_client.update_pr_comment(
                    repo_full_name, comment_id, final_comment
                )

                return {"status": "success", "pr_number": pr_number, "issues_found": 0}

            # Combine all code changes
            combined_code = "\n\n".join(
                [f"# File: {filename}\n{code}" for filename, code in code_changes.items()]
            )

            logger.info(
                f"Analyzing code pr_number={pr_number} files_changed={len(code_changes)} code_length={len(combined_code)}"
            )

            # Run analysis
            start_time = time.time()

            analysis_result = await self.analyzer.process(
                {"code": combined_code, "language": "python"}
            )

            duration_ms = (time.time() - start_time) * 1000

            # Add metadata (analysis_result is already a dict)
            if "metadata" not in analysis_result:
                analysis_result["metadata"] = {}
            analysis_result["metadata"]["duration_ms"] = duration_ms
            analysis_result["metadata"]["files_analyzed"] = len(code_changes)

            # Format comment (analysis_result is already a dict)
            final_comment = self.formatter.format_analysis_comment(
                analysis_result, pr_number, repo_full_name
            )

            # Update comment with results
            await self.github_client.update_pr_comment(repo_full_name, comment_id, final_comment)

            # Get issues count
            issues_count = len(analysis_result.get("issues", []))

            logger.info(
                f"Analysis complete pr_number={pr_number} issues_found={issues_count} duration_ms={duration_ms}"
            )

            return {
                "status": "success",
                "pr_number": pr_number,
                "repo": repo_full_name,
                "issues_found": issues_count,
                "duration_ms": duration_ms,
            }

        except Exception as e:
            logger.error(f"Analysis failed pr_number={pr_number} error={str(e)}", exc_info=True)

            # Post error comment if we have a comment to update
            try:
                if "comment_id" in locals():
                    error_comment = self.formatter.format_error_comment(e, pr_number)
                    await self.github_client.update_pr_comment(
                        repo_full_name, comment_id, error_comment
                    )
            except Exception as comment_error:
                logger.error(f"Failed to post error comment error={str(comment_error)}")

            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    async def handle_pull_request_review(self, event_data: Dict) -> Dict:
        """
        Handle pull request review event
        Can be used for feedback loop in future
        """
        logger.info("Received PR review event")
        return {"status": "acknowledged"}


# Singleton instance
_handler_instance = None


def get_webhook_handler() -> WebhookHandler:
    """Get singleton webhook handler instance"""
    global _handler_instance
    if _handler_instance is None:
        _handler_instance = WebhookHandler()
    return _handler_instance
