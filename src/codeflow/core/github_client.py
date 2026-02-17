"""
GitHub API Client
Handles interactions with GitHub API: fetching PRs, posting comments, etc.
"""

import httpx
from typing import List, Dict
import logging
from src.codeflow.core.auth import get_github_auth

logger = logging.getLogger(__name__)


class GitHubClient:
    """Client for GitHub API interactions"""

    def __init__(self):
        self.auth = get_github_auth()
        self.base_url = "https://api.github.com"

    async def get_pr_diff(self, repo_full_name: str, pr_number: int) -> str:
        """
        Fetch the diff for a pull request

        Args:
            repo_full_name: Full repo name like "owner/repo"
            pr_number: PR number

        Returns:
            The unified diff as a string
        """
        url = f"{self.base_url}/repos/{repo_full_name}/pulls/{pr_number}"
        headers = await self.auth.get_auth_headers()
        headers["Accept"] = "application/vnd.github.v3.diff"  # Request diff format

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()

        logger.info(
            f"Fetched PR diff repo={repo_full_name} pr_number={pr_number} diff_size={len(response.text)}"
        )

        return response.text

    async def get_pr_files(self, repo_full_name: str, pr_number: int) -> List[Dict]:
        """
        Get list of files changed in a PR

        Returns:
            List of file objects with filename, status, additions, deletions, patch
        """
        url = f"{self.base_url}/repos/{repo_full_name}/pulls/{pr_number}/files"
        headers = await self.auth.get_auth_headers()

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            files = response.json()

        logger.info(
            f"Fetched PR files repo={repo_full_name} pr_number={pr_number} file_count={len(files)}"
        )

        return files

    async def get_pr_details(self, repo_full_name: str, pr_number: int) -> Dict:
        """
        Get PR details (title, description, author, etc.)
        """
        url = f"{self.base_url}/repos/{repo_full_name}/pulls/{pr_number}"
        headers = await self.auth.get_auth_headers()

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()

        return response.json()

    async def post_pr_comment(self, repo_full_name: str, pr_number: int, comment_body: str) -> Dict:
        """
        Post a comment on a pull request

        Args:
            repo_full_name: Full repo name like "owner/repo"
            pr_number: PR number
            comment_body: Markdown-formatted comment text

        Returns:
            The created comment object
        """
        url = f"{self.base_url}/repos/{repo_full_name}/issues/{pr_number}/comments"
        headers = await self.auth.get_auth_headers()

        payload = {"body": comment_body}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            comment = response.json()

        logger.info(
            f"Posted PR comment repo={repo_full_name} pr_number={pr_number} comment_id={comment.get('id')}"
        )

        return comment

    async def update_pr_comment(
        self, repo_full_name: str, comment_id: int, comment_body: str
    ) -> Dict:
        """
        Update an existing comment
        Useful for updating analysis results
        """
        url = f"{self.base_url}/repos/{repo_full_name}/issues/comments/{comment_id}"
        headers = await self.auth.get_auth_headers()

        payload = {"body": comment_body}

        async with httpx.AsyncClient() as client:
            response = await client.patch(url, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()

        return response.json()

    def extract_code_from_diff(self, diff: str) -> Dict[str, str]:
        """
        Extract actual code changes from unified diff

        Returns:
            Dict mapping filename to changed code
        """
        files = {}
        current_file = None
        current_code = []

        for line in diff.split("\n"):
            # New file starts with "diff --git"
            if line.startswith("diff --git"):
                if current_file and current_code:
                    files[current_file] = "\n".join(current_code)
                current_code = []
                current_file = None

            # File path in format "+++ b/path/to/file.py"
            elif line.startswith("+++"):
                current_file = line[6:]  # Remove "+++ b/"

            # Only include added/modified lines (start with '+' but not '+++')
            elif line.startswith("+") and not line.startswith("+++"):
                current_code.append(line[1:])  # Remove the '+' prefix

        # Don't forget the last file
        if current_file and current_code:
            files[current_file] = "\n".join(current_code)

        return files

    async def check_rate_limit(self) -> Dict:
        """Check current rate limit status"""
        url = f"{self.base_url}/rate_limit"
        headers = await self.auth.get_auth_headers()

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

        return response.json()


# Singleton instance
_client_instance = None


def get_github_client() -> GitHubClient:
    """Get singleton GitHub client instance"""
    global _client_instance
    if _client_instance is None:
        _client_instance = GitHubClient()
    return _client_instance
