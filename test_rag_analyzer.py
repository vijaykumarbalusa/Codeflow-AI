"""Test RAG-enhanced analyzer with learning."""

import asyncio
from src.codeflow.agents.rag_code_analyzer import RAGCodeAnalyzer


async def main():
    print("🧠 Testing RAG Code Analyzer\n")
    print("=" * 60)

    agent = RAGCodeAnalyzer()

    # TEST 1: Analyze first code (no history yet)
    print("\n📝 TEST 1: First Analysis (No History)")
    print("-" * 60)

    code1 = """
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)
"""

    result1 = await agent.process({"code": code1, "language": "python"})

    print(f"Issues found: {result1['total_issues']}")
    print(f"Similar patterns: {result1['rag_context']['similar_patterns_found']}")
    print(f"Main issue: {result1['issues'][0]['issue_type'] if result1['issues'] else 'None'}")

    # TEST 2: Analyze similar code (should find pattern!)
    print("\n\n📝 TEST 2: Second Analysis (With History)")
    print("-" * 60)

    code2 = """
def delete_account(account_id):
    sql = f"DELETE FROM accounts WHERE id = {account_id}"
    return db.execute(sql)
"""

    result2 = await agent.process({"code": code2, "language": "python"})

    print(f"Issues found: {result2['total_issues']}")
    print(f"Similar patterns: {result2['rag_context']['similar_patterns_found']}")
    print(f"Main issue: {result2['issues'][0]['issue_type'] if result2['issues'] else 'None'}")

    if result2["rag_context"]["similar_patterns_found"] > 0:
        print("\n✅ SUCCESS! AI remembered similar SQL injection pattern!")
    else:
        print("\n⚠️  No similar patterns found yet (might need lower threshold)")

    # TEST 3: Completely different code type
    print("\n\n📝 TEST 3: Different Issue Type")
    print("-" * 60)

    code3 = """
def login(username, password):
    api_key = "sk-secret-key-12345"
    response = requests.post(url, headers={"Authorization": api_key})
    return response
"""

    result3 = await agent.process({"code": code3, "language": "python"})

    print(f"Issues found: {result3['total_issues']}")
    print(f"Similar patterns: {result3['rag_context']['similar_patterns_found']}")
    print(f"Main issue: {result3['issues'][0]['issue_type'] if result3['issues'] else 'None'}")

    print("\n" + "=" * 60)
    print("🎉 RAG Testing Complete!")


if __name__ == "__main__":
    asyncio.run(main())
