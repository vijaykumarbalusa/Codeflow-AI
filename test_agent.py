"""Quick test of the CodeAnalyzerAgent."""

import asyncio
import json
from src.codeflow.agents.code_analyzer import CodeAnalyzerAgent


async def main():
    # Create the agent
    agent = CodeAnalyzerAgent()

    # Test code with obvious security issues
    test_code = """
def login(username, password):
    # SQL Injection vulnerability
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    user = db.execute(query)

    # Hardcoded API key
    api_key = "sk-fake-api-key-for-example-only"

    # No error handling
    return user.id
"""

    print("🔍 Analyzing code...")
    print(f"Code:\n{test_code}\n")

    # Run analysis
    result = await agent.process({"code": test_code, "language": "python"})

    # Print results
    print("📊 Analysis Results:")
    print(json.dumps(result, indent=2))

    print(f"\n✅ Total issues found: {result['total_issues']}")
    print(f"🚨 Critical issues: {result['critical_count']}")
    print(f"🔒 Safe to merge: {result['safe_to_merge']}")


if __name__ == "__main__":
    asyncio.run(main())
