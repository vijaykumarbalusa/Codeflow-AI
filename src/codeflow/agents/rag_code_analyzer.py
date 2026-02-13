"""RAG-enhanced code analyzer that learns from past code patterns."""

import json
import logging
from typing import Any

from .code_analyzer import CodeAnalyzerAgent, CodeAnalysisResult
from ..database.vector_store import VectorStore

logger = logging.getLogger(__name__)


class RAGCodeAnalyzer(CodeAnalyzerAgent):
    """Code analyzer enhanced with RAG (Retrieval-Augmented Generation)."""

    def __init__(self, model: str = "llama-3.3-70b-versatile") -> None:
        """Initialize RAG analyzer with vector store."""
        super().__init__(model)
        self.vector_store = VectorStore()
        logger.info("RAGCodeAnalyzer initialized with vector database")

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze code with RAG enhancement.

        Args:
            input_data: Dict containing 'code' and optionally 'language'

        Returns:
            Enhanced analysis results
        """
        code = input_data.get("code", "")
        language = input_data.get("language", "python")

        logger.info(f"RAG analysis: {len(code)} chars of {language} code")

        # STEP 1: Search for similar code in vector database
        similar_snippets = self.vector_store.search_similar_code(
            code=code,
            limit=3,
            score_threshold=0.5,
        )

        # STEP 2: Build context from similar code
        context = self._build_context_from_history(similar_snippets)

        # STEP 3: Enhance the system prompt with context
        enhanced_system_prompt = self._create_enhanced_prompt(context)

        # STEP 4: Analyze with enhanced context
        user_prompt = f"""Analyze this {language} code for security and quality issues:
```{language}
{code}
```

Remember: Return ONLY the JSON object, nothing else."""

        messages = [
            {"role": "system", "content": enhanced_system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # Call LLM
        response = self._create_chat_completion(
            messages=messages,
            temperature=0.1,
            max_tokens=2000,
        )

        # Parse response
        try:
            cleaned_response = self._clean_response(response)
            result_dict = json.loads(cleaned_response)
            result = CodeAnalysisResult(**result_dict)

            # STEP 5: Store this code snippet for future learning
            if result.total_issues > 0:
                self._store_for_future_learning(code, result, language)

            logger.info(
                f"RAG analysis complete: {result.total_issues} issues "
                f"({result.critical_count} critical, "
                f"{len(similar_snippets)} similar patterns found)"
            )

            # Add RAG metadata to result
            result_with_rag = result.model_dump()
            result_with_rag["rag_context"] = {
                "similar_patterns_found": len(similar_snippets),
                "learning_enabled": True,
            }

            return result_with_rag

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return {
                "total_issues": 0,
                "critical_count": 0,
                "issues": [],
                "summary": "Error: Could not analyze code",
                "safe_to_merge": False,
                "error": str(e),
            }

    def _build_context_from_history(self, similar_snippets: list[dict[str, Any]]) -> str:
        """Build context string from similar code found in history."""
        if not similar_snippets:
            return "No similar code patterns found in history."

        context_parts = [
            "IMPORTANT - Similar code patterns found in past analysis:",
            "",
        ]

        for i, snippet in enumerate(similar_snippets, 1):
            similarity = snippet["score"]
            code = snippet["code"]
            metadata = snippet["metadata"]

            context_parts.append(f"Pattern {i} (Similarity: {similarity:.0%}):")
            context_parts.append(f"  Code: {code}")
            context_parts.append(f"  Issue Found: {metadata.get('issue_type', 'Unknown')}")
            context_parts.append(f"  Severity: {metadata.get('severity', 'Unknown')}")
            context_parts.append("")

        context_parts.append("→ Pay special attention to these types of issues in the new code!")

        return "\n".join(context_parts)

    def _create_enhanced_prompt(self, context: str) -> str:
        """Create system prompt enhanced with RAG context."""
        base_prompt = self.SYSTEM_PROMPT

        if context and "No similar code" not in context:
            # Add context at the beginning
            enhanced = f"""{context}

---

{base_prompt}"""
            return enhanced

        return base_prompt

    def _clean_response(self, response: str) -> str:
        """Clean LLM response to extract JSON."""
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned.split("```json")[1]
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
        return cleaned.strip()

    def _store_for_future_learning(
        self, code: str, result: CodeAnalysisResult, language: str
    ) -> None:
        """Store analyzed code for future RAG retrieval."""
        try:
            # Only store if we found issues
            if result.total_issues == 0:
                return

            # Get the most severe issue type
            issue_types = [issue.issue_type for issue in result.issues]
            severities = [issue.severity for issue in result.issues]

            # Determine primary issue
            if "HIGH" in severities:
                primary_severity = "HIGH"
                primary_issue = next(
                    issue.issue_type for issue in result.issues if issue.severity == "HIGH"
                )
            else:
                primary_severity = severities[0] if severities else "UNKNOWN"
                primary_issue = issue_types[0] if issue_types else "UNKNOWN"

            # Store in vector database
            self.vector_store.store_code_snippet(
                code=code,
                metadata={
                    "language": language,
                    "issue_type": primary_issue,
                    "severity": primary_severity,
                    "total_issues": result.total_issues,
                    "safe_to_merge": result.safe_to_merge,
                },
            )

            logger.info(f"Stored code pattern for future learning: {primary_issue}")

        except Exception as e:
            logger.error(f"Failed to store for learning: {e}")
            # Don't fail the analysis if storage fails
