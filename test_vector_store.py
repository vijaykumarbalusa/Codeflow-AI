"""Test the vector store."""

from src.codeflow.database.vector_store import VectorStore


def main():
    print("🔧 Initializing vector store...")
    store = VectorStore()

    # Store some example code snippets with known issues
    print("\n📝 Storing example code snippets...")

    # Example 1: SQL Injection
    store.store_code_snippet(
        code='query = f"SELECT * FROM users WHERE id = {user_id}"',
        metadata={
            "language": "python",
            "issue_type": "SQL Injection",
            "severity": "HIGH",
        },
        snippet_id="example_sql_injection_1",
    )

    # Example 2: Hardcoded secret
    store.store_code_snippet(
        code='api_key = "sk-abc123secret"',
        metadata={
            "language": "python",
            "issue_type": "Hardcoded Secret",
            "severity": "HIGH",
        },
        snippet_id="example_hardcoded_secret_1",
    )

    # Example 3: Similar SQL injection (slightly different)
    store.store_code_snippet(
        code='sql = f"DELETE FROM accounts WHERE account_id = {id}"',
        metadata={
            "language": "python",
            "issue_type": "SQL Injection",
            "severity": "HIGH",
        },
        snippet_id="example_sql_injection_2",
    )

    print("✅ Stored 3 example snippets")

    # Now search for similar code
    print("\n🔍 Searching for code similar to SQL injection...")
    test_code = 'db_query = f"UPDATE users SET name = {name} WHERE id = {uid}"'

    results = store.search_similar_code(test_code, limit=3, score_threshold=0.5)

    print(f"\n📊 Found {len(results)} similar snippets:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Similarity: {result['score']:.2f}")
        print(f"   Code: {result['code']}")
        print(f"   Issue: {result['metadata']['issue_type']}")


if __name__ == "__main__":
    main()
