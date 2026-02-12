"""Agent for analyzing code quality and security issues."""

import json
import logging
from typing import Any

from pydantic import BaseModel, Field

from .base import BaseAgent

logger = logging.getLogger(__name__)


class SecurityIssue(BaseModel):
    """Represents a single security or quality issue found in code."""

    line_number: int = Field(description="Line number where issue occurs")
    severity: str = Field(description="Severity: HIGH, MEDIUM, or LOW")
    issue_type: str = Field(description="Type of issue (e.g., 'SQL Injection')")
    description: str = Field(description="What the issue is", max_length=200)
    suggestion: str = Field(description="How to fix it", max_length=300)
    confidence: float = Field(description="Confidence score 0-1", ge=0.0, le=1.0)


class CodeAnalysisResult(BaseModel):
    """Result of code analysis."""

    total_issues: int = Field(description="Total number of issues found")
    critical_count: int = Field(description="Number of HIGH severity issues")
    issues: list[SecurityIssue] = Field(description="List of all issues found")
    summary: str = Field(description="Brief summary of findings")
    safe_to_merge: bool = Field(description="Whether code is safe to merge")


class CodeAnalyzerAgent(BaseAgent):
    """Agent that analyzes code for security and quality issues."""

    SYSTEM_PROMPT = """You are an expert code security reviewer. Your job is to analyze code changes for security vulnerabilities and quality issues.

Follow this step-by-step process:

Step 1: Read the code carefully and understand what it does
Step 2: Check for common security issues:
   - SQL injection vulnerabilities
   - Cross-site scripting (XSS)
   - Hardcoded secrets (API keys, passwords)
   - Insecure cryptography
   - Command injection
   - Path traversal
   - Insecure deserialization

Step 3: Check for code quality issues:
   - Missing error handling
   - Potential null/undefined errors
   - Resource leaks
   - Performance issues

Step 4: For each issue found, determine:
   - Exact line number
   - Severity (HIGH/MEDIUM/LOW)
   - Clear description
   - Specific fix suggestion
   - Your confidence level (0.0-1.0)

Step 5: Provide a summary and recommendation

Return your analysis as a JSON object matching this schema:
{
  "total_issues": <number>,
  "critical_count": <number of HIGH severity issues>,
  "issues": [
    {
      "line_number": <number>,
      "severity": "HIGH" | "MEDIUM" | "LOW",
      "issue_type": "<type>",
      "description": "<what's wrong>",
      "suggestion": "<how to fix>",
      "confidence": <0.0-1.0>
    }
  ],
  "summary": "<brief summary>",
  "safe_to_merge": <true|false>
}

IMPORTANT: Return ONLY valid JSON, no markdown formatting, no explanation text."""

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze code changes for security and quality issues.

        Args:
            input_data: Dict containing 'code' and optionally 'language'

        Returns:
            Analysis results
        """
        code = input_data.get("code", "")
        language = input_data.get("language", "python")

        logger.info(f"Analyzing {len(code)} characters of {language} code")

        # Create the analysis prompt
        user_prompt = f"""Analyze this {language} code for security and quality issues:
```{language}
{code}
```

Remember: Return ONLY the JSON object, nothing else."""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        # Call the LLM
        response = self._create_chat_completion(
            messages=messages,
            temperature=0.1,  # Low temperature for consistent analysis
            max_tokens=2000,
        )

        # Parse the JSON response
        try:
            # Clean up response (remove markdown if present)
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response.split("```json")[1]
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response.split("```")[1]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response.rsplit("```", 1)[0]
            cleaned_response = cleaned_response.strip()

            # Parse JSON
            result_dict = json.loads(cleaned_response)

            # Validate with Pydantic
            result = CodeAnalysisResult(**result_dict)

            logger.info(
                f"Analysis complete: {result.total_issues} issues found "
                f"({result.critical_count} critical)"
            )

            return result.model_dump()

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw response: {response}")

            # Return a safe default
            return {
                "total_issues": 0,
                "critical_count": 0,
                "issues": [],
                "summary": "Error: Could not analyze code (JSON parse error)",
                "safe_to_merge": False,
                "error": str(e),
            }

        except Exception as e:
            logger.error(f"Error during code analysis: {e}", exc_info=True)
            raise
