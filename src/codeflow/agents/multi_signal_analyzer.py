"""Multi-signal code analyzer combining AI + static analysis."""

import json
import logging
import subprocess  # nosec B404
import tempfile
from pathlib import Path
from typing import Any

from .rag_code_analyzer import RAGCodeAnalyzer

logger = logging.getLogger(__name__)


class MultiSignalAnalyzer(RAGCodeAnalyzer):
    """Analyzer combining AI, RAG, and static analysis."""

    def __init__(self, model: str = "llama-3.3-70b-versatile") -> None:
        super().__init__(model)
        self._check_semgrep()
        logger.info("MultiSignalAnalyzer initialized")

    def _check_semgrep(self) -> None:
        """Check if semgrep is available."""
        try:
            subprocess.run(  # nosec B603 B607
                ["semgrep", "--version"],
                capture_output=True,
                check=True,
                timeout=5,
            )
            self.semgrep_available = True
        except Exception:
            self.semgrep_available = False
            logger.warning("Semgrep not available, using AI-only mode")

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze with multiple signals."""
        code = input_data.get("code", "")
        language = input_data.get("language", "python")

        ai_result = await super().process(input_data)

        static_issues = []
        if self.semgrep_available:
            static_issues = self._run_semgrep(code, language)

        combined_result = self._combine_signals(ai_result, static_issues)

        logger.info(
            f"Multi-signal: {combined_result['total_issues']} issues "
            f"(AI: {ai_result['total_issues']}, Static: {len(static_issues)})"
        )

        return combined_result

    def _run_semgrep(self, code: str, language: str) -> list[dict[str, Any]]:
        """Run semgrep static analysis."""
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=f".{language}", delete=False) as f:
                f.write(code)
                temp_path = f.name

            result = subprocess.run(  # nosec B603 B607
                ["semgrep", "--config=auto", "--json", temp_path],
                capture_output=True,
                timeout=10,
            )

            Path(temp_path).unlink()

            if result.returncode in [0, 1]:
                data = json.loads(result.stdout)
                return data.get("results", [])

            return []

        except Exception as e:
            logger.error(f"Semgrep error: {e}")
            return []

    def _combine_signals(
        self, ai_result: dict[str, Any], static_issues: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Combine AI and static analysis results."""
        combined = ai_result.copy()

        for issue in static_issues:
            issue_dict = {
                "line_number": issue.get("start", {}).get("line", 0),
                "severity": self._map_severity(issue.get("extra", {}).get("severity", "WARNING")),
                "issue_type": issue.get("check_id", "Unknown").split(".")[-1],
                "description": issue.get("extra", {}).get("message", "Static analysis issue"),
                "suggestion": f"Review: {issue.get('check_id', 'Issue')}",
                "confidence": 0.9,
                "source": "semgrep",
            }

            is_duplicate = any(
                ai_issue["line_number"] == issue_dict["line_number"]
                and ai_issue["issue_type"].lower() in issue_dict["issue_type"].lower()
                for ai_issue in combined.get("issues", [])
            )

            if not is_duplicate:
                combined["issues"].append(issue_dict)
            else:
                for ai_issue in combined["issues"]:
                    if (
                        ai_issue["line_number"] == issue_dict["line_number"]
                        and ai_issue["issue_type"].lower() in issue_dict["issue_type"].lower()
                    ):
                        ai_issue["confidence"] = min(ai_issue["confidence"] + 0.15, 1.0)
                        ai_issue["verified_by"] = "semgrep"

        combined["total_issues"] = len(combined["issues"])
        combined["critical_count"] = sum(1 for i in combined["issues"] if i["severity"] == "HIGH")

        combined["multi_signal"] = {
            "ai_issues": ai_result["total_issues"],
            "static_issues": len(static_issues),
            "combined_issues": combined["total_issues"],
            "confidence_boosted": sum(
                1 for i in combined["issues"] if i.get("verified_by") == "semgrep"
            ),
        }

        return combined

    def _map_severity(self, semgrep_severity: str) -> str:
        """Map semgrep severity to our system."""
        mapping = {"ERROR": "HIGH", "WARNING": "MEDIUM", "INFO": "LOW"}
        return mapping.get(semgrep_severity.upper(), "MEDIUM")
