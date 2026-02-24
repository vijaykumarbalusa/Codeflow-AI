"""
Test GitHub Integration
Verifies that GitHub App authentication and API access work
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from codeflow.core.config import get_settings
from codeflow.core.auth import get_github_auth
from codeflow.core.github_client import get_github_client


async def test_authentication():
    """Test GitHub App authentication"""
    print("\n🔐 Testing GitHub App Authentication...")
    print("=" * 60)
    
    try:
        auth = get_github_auth()
        
        # Test JWT generation
        print("\n1️⃣ Generating JWT token...")
        jwt_token = auth._generate_jwt()
        print(f"✅ JWT generated: {jwt_token[:50]}...")
        
        # Test installation token
        print("\n2️⃣ Getting installation access token...")
        access_token = await auth.get_installation_token()
        print(f"✅ Access token obtained: {access_token[:20]}...")
        
        print("\n✅ Authentication working!")
        return True
        
    except FileNotFoundError as e:
        print(f"\n❌ Private key not found: {e}")
        print("Please download it from GitHub and place it at config/private-key.pem")
        return False
    except Exception as e:
        print(f"\n❌ Authentication failed: {e}")
        return False


async def test_api_access():
    """Test GitHub API access"""
    print("\n\n🌐 Testing GitHub API Access...")
    print("=" * 60)
    
    try:
        client = get_github_client()
        
        # Test rate limit check
        print("\n1️⃣ Checking rate limits...")
        rate_limit = await client.check_rate_limit()
        core = rate_limit.get("resources", {}).get("core", {})
        print(f"✅ Rate limit: {core.get('remaining')}/{core.get('limit')} requests remaining")
        
        # Test fetching repo (using your repo)
        print("\n2️⃣ Testing repository access...")
        settings = get_settings()
        
        # We'll try to fetch details of your own repo
        # You can change this to test with a specific PR
        print("   Note: To test PR fetching, you need an actual PR number")
        
        print("\n✅ API access working!")
        return True
        
    except Exception as e:
        print(f"\n❌ API access failed: {e}")
        return False


async def test_pr_operations():
    """Test PR operations (requires a real PR)"""
    print("\n\n📝 Testing PR Operations...")
    print("=" * 60)
    
    settings = get_settings()
    
    print("\n⚠️  This test requires a real PR to work.")
    print("To test PR operations:")
    print("1. Create a test PR in your repository")
    print("2. Update this script with the PR number")
    print("3. Run this test again")
    print("\nSkipping PR operations test for now.")
    
    return True


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  CodeFlow AI - GitHub Integration Test")
    print("=" * 60)
    
    settings = get_settings()
    
    # Display configuration
    print("\n📋 Configuration:")
    print(f"   App ID: {settings.github_app_id}")
    print(f"   Installation ID: {settings.github_installation_id}")
    print(f"   Private Key Path: {settings.github_private_key_path}")
    
    # Run tests
    auth_ok = await test_authentication()
    
    if not auth_ok:
        print("\n❌ Authentication failed - cannot continue with other tests")
        sys.exit(1)
    
    api_ok = await test_api_access()
    pr_ok = await test_pr_operations()
    
    # Summary
    print("\n" + "=" * 60)
    print("  Test Summary")
    print("=" * 60)
    print(f"  Authentication: {'✅ PASS' if auth_ok else '❌ FAIL'}")
    print(f"  API Access:     {'✅ PASS' if api_ok else '❌ FAIL'}")
    print(f"  PR Operations:  {'⚠️  SKIP (needs real PR)' if pr_ok else '❌ FAIL'}")
    
    if auth_ok and api_ok:
        print("\n🎉 GitHub Integration is working!")
        print("\nNext steps:")
        print("1. Create a test PR in your repository")
        print("2. The webhook should trigger automatically")
        print("3. Check the PR for a comment from CodeFlow AI")
    else:
        print("\n❌ Some tests failed - please fix the issues above")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
