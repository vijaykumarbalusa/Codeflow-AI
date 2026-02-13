"""Test multi-signal analyzer."""

import asyncio
from src.codeflow.agents.multi_signal_analyzer import MultiSignalAnalyzer


async def main():
    agent = MultiSignalAnalyzer()

    code = """
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    password = "hardcoded123"
    return db.execute(query)
"""

    result = await agent.process({"code": code, "language": "python"})

    print(f"Total issues: {result['total_issues']}")
    print(f"AI issues: {result['multi_signal']['ai_issues']}")
    print(f"Static issues: {result['multi_signal']['static_issues']}")
    print(f"Confidence boosted: {result['multi_signal']['confidence_boosted']}")

    for issue in result["issues"]:
        verified = "✓" if issue.get("verified_by") else ""
        print(
            f"\n{issue['severity']} - {issue['issue_type']} {verified}"
            f"\n  Line: {issue['line_number']}"
            f"\n  Confidence: {issue['confidence']:.0%}"
        )


asyncio.run(main())
