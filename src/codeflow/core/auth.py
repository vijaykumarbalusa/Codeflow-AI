"""
GitHub App Authentication Module
Handles JWT token generation and GitHub installation authentication
"""

import time
from pathlib import Path
import jwt
import httpx
from typing import Optional
from src.codeflow.core.config import get_settings

settings = get_settings()


class GitHubAuth:
    """Handles GitHub App authentication"""

    def __init__(self):
        self.app_id = settings.github_app_id
        self.private_key_path = settings.github_private_key_path
        self.installation_id = settings.github_installation_id
        self._installation_token: Optional[str] = None
        self._token_expires_at: float = 0

    def _load_private_key(self) -> str:
        """Load private key from env var (cloud) or file (local)"""
        # Prefer env var (for cloud deployments like Render)
        if settings.github_private_key:
            key = settings.github_private_key.replace("\\n", "\n")
            return key
        # Fall back to file path (for local development)
        key_path = Path(self.private_key_path)
        if not key_path.exists():
            raise FileNotFoundError(
                f"Private key not found at {self.private_key_path}. "
                f"Set GITHUB_PRIVATE_KEY env var or place the key file there."
            )
        return key_path.read_text()

    def _generate_jwt(self) -> str:
        """Generate JWT token for GitHub App authentication"""
        private_key = self._load_private_key()

        # JWT payload
        now = int(time.time())
        payload = {
            "iat": now,  # Issued at time
            "exp": now + 600,  # Expires in 10 minutes
            "iss": self.app_id,  # Issuer (your app ID)
        }

        # Encode JWT
        token = jwt.encode(payload, private_key, algorithm="RS256")
        return token

    async def get_installation_token(self) -> str:
        """
        Get installation access token for API requests
        Tokens are cached and reused until they expire
        """
        # Return cached token if still valid
        if self._installation_token and time.time() < self._token_expires_at:
            return self._installation_token

        # Generate new JWT
        jwt_token = self._generate_jwt()

        # Exchange JWT for installation token
        url = f"https://api.github.com/app/installations/{self.installation_id}/access_tokens"
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers)
            response.raise_for_status()
            data = response.json()

        # Cache the token
        self._installation_token = data["token"]
        # Tokens expire in 1 hour, we'll refresh 5 mins early
        self._token_expires_at = time.time() + 3300  # 55 minutes

        return self._installation_token

    async def get_auth_headers(self) -> dict:
        """Get authenticated headers for GitHub API requests"""
        token = await self.get_installation_token()
        return {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}


# Singleton instance
_auth_instance = None


def get_github_auth() -> GitHubAuth:
    """Get singleton GitHub auth instance"""
    global _auth_instance
    if _auth_instance is None:
        _auth_instance = GitHubAuth()
    return _auth_instance
