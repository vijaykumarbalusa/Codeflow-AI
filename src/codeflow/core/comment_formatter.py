"""
GitHub PR Comment Formatter
Creates beautifully formatted markdown comments for PR analysis results
"""

from typing import Dict, Any


class CommentFormatter:
    """Formats analysis results into GitHub markdown comments"""

    @staticmethod
    def format_analysis_comment(
        analysis_result: Dict[str, Any], pr_number: int, repo_name: str
    ) -> str:
        """
        Format analysis result into a comprehensive PR comment

        Args:
            analysis_result: Analysis result from multi-signal analyzer
            pr_number: PR number
            repo_name: Repository name

        Returns:
            Formatted markdown comment
        """
        issues = analysis_result.get("issues", [])
        metadata = analysis_result.get("metadata", {})

        # Determine overall risk level
        severity_counts = {"high": 0, "medium": 0, "low": 0}
        for issue in issues:
            severity = issue.get("severity", "low").lower()
            if severity in severity_counts:
                severity_counts[severity] += 1

        risk_level = CommentFormatter._calculate_risk_level(severity_counts)
        risk_emoji = CommentFormatter._get_risk_emoji(risk_level)

        # Build comment
        lines = []

        # Header
        lines.append("## 🔍 CodeFlow AI Analysis")
        lines.append("")
        lines.append(f"**Overall Risk:** {risk_emoji} {risk_level}")
        lines.append("")

        # Summary
        if issues:
            lines.append(f"**Issues Found:** {len(issues)}")
            lines.append(f"- 🔴 High: {severity_counts['high']}")
            lines.append(f"- 🟡 Medium: {severity_counts['medium']}")
            lines.append(f"- 🟢 Low: {severity_counts['low']}")
        else:
            lines.append("✅ **No issues found!** Code looks good.")

        lines.append("")
        lines.append("---")
        lines.append("")

        # Issues details
        if issues:
            lines.append("### Issues Found")
            lines.append("")

            for idx, issue in enumerate(issues, 1):
                lines.append(CommentFormatter._format_issue(issue, idx))
                lines.append("")

        # Metadata
        lines.append("---")
        lines.append("")
        lines.append("### Analysis Details")
        lines.append("")
        lines.append(f"- **Analysis Time:** {metadata.get('duration_ms', 0)/1000:.2f}s")
        lines.append("- **Model Used:** Llama 3.3 70B")
        lines.append(f"- **Files Analyzed:** {metadata.get('files_analyzed', 1)}")

        lines.append("")
        lines.append("---")
        lines.append("")

        # Footer
        lines.append(f"*Analyzed by [CodeFlow AI](https://github.com/{repo_name})* 🤖")
        lines.append("")
        lines.append("💡 *Was this helpful? React with 👍 or 👎*")

        return "\n".join(lines)

    @staticmethod
    def _format_issue(issue: Dict[str, Any], index: int) -> str:
        """Format a single issue as a collapsible details block"""
        # Extract issue details - MATCHING ACTUAL ANALYZER OUTPUT
        severity = issue.get("severity", "medium").lower()
        confidence = issue.get("confidence", 0.8)
        description = issue.get("description", "Potential security or code quality issue detected")
        reasoning = issue.get("reasoning", "")

        # Get line number (analyzer uses line_number, not location)
        line_number = issue.get("line_number", issue.get("line", "?"))

        # Try to get file from location dict, or default
        location_info = issue.get("location", {})
        if isinstance(location_info, dict):
            file_path = location_info.get("file", "test_vulnerable.py")
        else:
            file_path = "test_vulnerable.py"  # Default to our test file

        # Get code snippet
        code_snippet = issue.get("code_snippet", issue.get("code", ""))

        # Get fix suggestion (analyzer uses 'suggestion' not 'fix_suggestion')
        fix_suggestion = issue.get("fix_suggestion", issue.get("suggestion", ""))
        if not fix_suggestion or fix_suggestion.startswith("Review:"):
            # Generate better fix if we only have generic suggestion
            fix_suggestion = CommentFormatter._generate_fix_suggestion(description, code_snippet)

        severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢", "critical": "🔴"}.get(
            severity, "⚪"
        )

        # Format issue type as title - use description to infer type
        title = CommentFormatter._format_issue_title(description)

        lines = []
        lines.append("<details>")
        lines.append(
            f"<summary>{severity_emoji} <strong>{title}</strong> (Confidence: {confidence:.0%})</summary>"
        )
        lines.append("")
        lines.append("<br>")
        lines.append("")

        # Location
        lines.append(f"**📍 Location:** `{file_path}:{line_number}`")
        lines.append("")

        # Description
        lines.append(f"**⚠️ Issue:** {description}")
        lines.append("")

        # Reasoning (if available)
        if reasoning:
            lines.append(f"**🔍 Why this matters:** {reasoning}")
            lines.append("")

        # Code snippet
        if code_snippet:
            lines.append("**📝 Problematic Code:**")
            lines.append("```python")
            lines.append(code_snippet.strip())
            lines.append("```")
            lines.append("")

        # Fix suggestion
        if fix_suggestion:
            lines.append("**💡 Suggested Fix:**")
            lines.append("")
            lines.append(fix_suggestion)
            lines.append("")

        lines.append("</details>")

        return "\n".join(lines)

    @staticmethod
    def _format_issue_title(description: str) -> str:
        """Convert description to readable title"""
        # Handle descriptions that contain the issue type
        desc_lower = description.lower()

        # Check if description already has the issue name
        if "sql injection" in desc_lower or "sql_injection" in desc_lower:
            return "SQL Injection Vulnerability"
        if "hardcoded" in desc_lower and (
            "secret" in desc_lower or "api" in desc_lower or "key" in desc_lower
        ):
            return "Hardcoded Secret Detected"
        if "hardcoded" in desc_lower and "password" in desc_lower:
            return "Hardcoded Password"
        if "xss" in desc_lower or "cross-site" in desc_lower:
            return "Cross-Site Scripting (XSS)"
        if "path traversal" in desc_lower:
            return "Path Traversal Vulnerability"
        if "command injection" in desc_lower:
            return "Command Injection Risk"
        if "weak" in desc_lower and "crypto" in desc_lower:
            return "Weak Cryptography"
        if "error handling" in desc_lower or "missing error" in desc_lower:
            return "Missing Error Handling"

        # Default: use first part of description
        if len(description) > 50:
            return description[:47] + "..."

        return description

    @staticmethod
    def _generate_fix_suggestion(description: str, code_snippet: str) -> str:
        """Generate fix suggestions based on description"""
        desc_lower = description.lower()

        if "sql" in desc_lower and "injection" in desc_lower:
            return """Use **parameterized queries** instead of string concatenation:
````````python
# ❌ Vulnerable - DO NOT USE
query = f"SELECT * FROM users WHERE id = {user_id}"

# ✅ Safe - Use parameterized queries
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))

# Or with named parameters
query = "SELECT * FROM users WHERE id = :user_id"
cursor.execute(query, {"user_id": user_id})
````````

**Why this works:** Parameterized queries separate code from data, preventing injection attacks."""

        elif (
            "hardcoded" in desc_lower
            or "secret" in desc_lower
            or "password" in desc_lower
            or "api" in desc_lower
        ):
            return """**Never hardcode secrets in source code.** Use environment variables:
````````python
# ❌ Vulnerable - DO NOT USE
API_KEY = "sk-1234567890abcdef"
PASSWORD = "admin123"

# ✅ Safe - Use environment variables
import os
API_KEY = os.getenv("API_KEY")
PASSWORD = os.getenv("DATABASE_PASSWORD")

# Or use a secrets manager
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.environ["API_KEY"]
````````

**Additional steps:**
1. Add secrets to `.env` file (don't commit this!)
2. Add `.env` to `.gitignore`
3. Document required env vars in `.env.example`
4. Rotate any exposed secrets immediately"""

        elif "xss" in desc_lower or "cross" in desc_lower:
            return """Sanitize and escape user input before displaying:
````````python
# ❌ Vulnerable
return f"<div>{user_input}</div>"

# ✅ Safe - Escape HTML
from markupsafe import escape
return f"<div>{escape(user_input)}</div>"

# Or use a templating engine (Jinja2, Django templates)
# They auto-escape by default
```````"""

        elif "command" in desc_lower and "injection" in desc_lower:
            return """Avoid shell=True and validate input:
``````python
# ❌ Vulnerable
os.system(f"git clone {repo_url}")

# ✅ Safe - Use subprocess with list
import subprocess
subprocess.run(["git", "clone", repo_url], check=True)

# Better: Validate input first
if not repo_url.startswith("https://github.com/"):
    raise ValueError("Invalid repository URL")
`````"""

        elif "error" in desc_lower and "handling" in desc_lower:
            return """Add proper error handling:
````python
# ❌ Missing error handling
data = requests.get(url).json()

# ✅ With error handling
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
except requests.Timeout:
    logger.error("Request timed out")
    raise
except requests.HTTPError as e:
    logger.error(f"HTTP error: {e}")
    raise
except ValueError:
    logger.error("Invalid JSON response")
    raise
```"""

        else:
            return """Review this code section and apply security best practices:

- **Input validation:** Verify and sanitize all user input
- **Output encoding:** Escape data before displaying
- **Principle of least privilege:** Use minimal permissions
- **Defense in depth:** Multiple layers of security"""

    @staticmethod
    def _calculate_risk_level(severity_counts: dict) -> str:
        """Calculate overall risk level from severity counts"""
        if severity_counts["high"] >= 3:
            return "Critical"
        elif severity_counts["high"] >= 2:
            return "High"
        elif severity_counts["high"] >= 1:
            return "High"
        elif severity_counts["medium"] >= 3:
            return "High"
        elif severity_counts["medium"] >= 1:
            return "Medium"
        elif severity_counts["low"] > 0:
            return "Low"
        else:
            return "None"

    @staticmethod
    def _get_risk_emoji(risk_level: str) -> str:
        """Get emoji for risk level"""
        return {"Critical": "🔴🔴", "High": "🔴", "Medium": "🟡", "Low": "🟢", "None": "✅"}.get(
            risk_level, "⚪"
        )

    @staticmethod
    def format_error_comment(error: Exception, pr_number: int) -> str:
        """Format an error message as a comment"""
        lines = []
        lines.append("## ⚠️ CodeFlow AI - Analysis Failed")
        lines.append("")
        lines.append("Sorry, I encountered an error while analyzing this PR.")
        lines.append("")
        lines.append(f"**Error:** `{str(error)}`")
        lines.append("")
        lines.append("Please check the logs or contact the maintainer.")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(
            "*Analyzed by [CodeFlow AI](https://github.com/vijaykumarbalusa/Codeflow-AI)* 🤖"
        )

        return "\n".join(lines)

    @staticmethod
    def format_analyzing_comment(pr_number: int) -> str:
        """Initial comment posted while analysis is running"""
        return (
            "## 🔄 CodeFlow AI - Analysis in Progress\n\n"
            "I'm analyzing this PR now. This will take a few seconds...\n\n"
            "---\n\n"
            "*Analyzed by [CodeFlow AI](https://github.com/vijaykumarbalusa/Codeflow-AI)* 🤖"
        )
