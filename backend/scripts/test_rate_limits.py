#!/usr/bin/env python3
"""
Rate Limit Testing Script

Tests that rate limiting is working correctly by hitting endpoints
with fast-failing requests (invalid data) that still count against limits.

Usage:
    # Start the server first, then:
    python scripts/test_rate_limits.py
    
    # Test specific tier:
    python scripts/test_rate_limits.py --tier auth
    python scripts/test_rate_limits.py --tier public
    
    # Custom base URL:
    python scripts/test_rate_limits.py --base-url http://localhost:8000

No tokens are wasted - requests fail fast but still count against rate limits.
"""

import argparse
import sys
import time
from dataclasses import dataclass
from typing import Callable

import requests

# =============================================================================
# Configuration
# =============================================================================

DEFAULT_BASE_URL = "http://localhost:8000"

# Rate limit tiers to test (from rate_limit.py)
RATE_LIMITS = {
    "auth": {
        "limit": 5,
        "window": "minute",
        "endpoint": "/api/auth/login",
        "method": "POST",
        "payload": {"email": "fake@test.com", "password": "wrongpassword"},
        "description": "Auth endpoints (login, register)",
    },
    "public": {
        "limit": 60,
        "window": "minute",
        "endpoint": "/api/cv/health",
        "method": "GET",
        "payload": None,
        "description": "Public endpoints (health check)",
        "note": "May fail if database is not connected",
    },
    "notification_test": {
        "limit": 5,
        "window": "hour",
        "endpoint": "/api/notifications/test/email",
        "method": "POST",
        "payload": {},
        "description": "Test notification endpoints",
        "requires_auth": True,
    },
    # These require auth - we'll test them if a token is provided
    "default": {
        "limit": 100,
        "window": "minute",
        "endpoint": "/api/profiles/",
        "method": "GET",
        "payload": None,
        "description": "General API endpoints",
        "requires_auth": True,
    },
    "chat": {
        "limit": 30,
        "window": "minute",
        "endpoint": "/api/chat/00000000-0000-0000-0000-000000000000",
        "method": "POST",
        "payload": {"question": "test"},
        "description": "Chat/RAG endpoints",
        "requires_auth": True,
    },
    "upload": {
        "limit": 100,
        "window": "hour",
        "endpoint": "/api/cv/upload",
        "method": "POST",
        "payload": None,  # Will send empty file
        "description": "CV upload endpoints",
        "requires_auth": True,
        "is_upload": True,
    },
}


@dataclass
class TestResult:
    """Result of a rate limit test."""
    tier: str
    passed: bool
    requests_made: int
    got_429_at: int | None
    expected_429_at: int
    error: str | None = None


# =============================================================================
# Test Functions
# =============================================================================


def get_auth_token(base_url: str, email: str, password: str) -> str | None:
    """Get a JWT token for authenticated endpoint testing."""
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json={"email": email, "password": password},
            timeout=10,
        )
        if response.status_code == 200:
            return response.json().get("access_token")
    except Exception:
        pass
    return None


def test_rate_limit(
    base_url: str,
    tier_name: str,
    tier_config: dict,
    auth_token: str | None = None,
    verbose: bool = False,
) -> TestResult:
    """
    Test a specific rate limit tier.
    
    Makes requests until we get a 429 or exceed the expected limit.
    """
    limit = tier_config["limit"]
    endpoint = tier_config["endpoint"]
    method = tier_config["method"]
    payload = tier_config["payload"]
    requires_auth = tier_config.get("requires_auth", False)
    is_upload = tier_config.get("is_upload", False)
    
    # Skip if auth required but no token
    if requires_auth and not auth_token:
        return TestResult(
            tier=tier_name,
            passed=False,
            requests_made=0,
            got_429_at=None,
            expected_429_at=limit + 1,
            error="Requires auth token (use --email and --password)",
        )
    
    url = f"{base_url}{endpoint}"
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    got_429_at = None
    requests_made = 0
    server_errors = 0
    
    # Make limit + 5 requests to ensure we hit the limit
    max_requests = limit + 5
    
    print(f"\n{'='*60}")
    print(f"Testing: {tier_name.upper()} ({tier_config['description']})")
    print(f"Endpoint: {method} {endpoint}")
    print(f"Limit: {limit}/{tier_config['window']}")
    if tier_config.get("note"):
        print(f"Note: {tier_config['note']}")
    print(f"{'='*60}")
    
    for i in range(1, max_requests + 1):
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                if is_upload:
                    # Send empty/invalid file
                    files = {"file": ("empty.txt", b"not a pdf", "text/plain")}
                    response = requests.post(url, headers=headers, files=files, timeout=10)
                else:
                    response = requests.post(url, headers=headers, json=payload, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            requests_made += 1
            status = response.status_code
            
            # Track server errors (5xx)
            if 500 <= status < 600:
                server_errors += 1
                # If all responses are server errors, endpoint is broken
                if server_errors >= 5 and server_errors == requests_made:
                    return TestResult(
                        tier=tier_name,
                        passed=False,
                        requests_made=requests_made,
                        got_429_at=None,
                        expected_429_at=limit + 1,
                        error=f"Endpoint returns {status} errors (server/config issue, not rate limit)",
                    )
            
            if verbose:
                print(f"  Request {i}: {status}")
            else:
                # Progress indicator
                if status == 429:
                    print(f"  Request {i}: 429 🛑 RATE LIMITED")
                elif i % 10 == 0 or i <= 5:
                    print(f"  Request {i}: {status}")
            
            if status == 429:
                got_429_at = i
                break
                
        except requests.exceptions.RequestException as e:
            return TestResult(
                tier=tier_name,
                passed=False,
                requests_made=requests_made,
                got_429_at=None,
                expected_429_at=limit + 1,
                error=f"Request failed: {e}",
            )
    
    # Determine if test passed
    # We expect 429 at request (limit + 1)
    expected_429_at = limit + 1
    passed = got_429_at == expected_429_at
    
    return TestResult(
        tier=tier_name,
        passed=passed,
        requests_made=requests_made,
        got_429_at=got_429_at,
        expected_429_at=expected_429_at,
    )


def print_results(results: list[TestResult]) -> None:
    """Print test results summary."""
    print("\n")
    print("=" * 70)
    print("RATE LIMIT TEST RESULTS")
    print("=" * 70)
    
    passed = 0
    failed = 0
    skipped = 0
    
    for result in results:
        if result.error:
            status = "⏭️  SKIPPED"
            skipped += 1
            detail = result.error
        elif result.passed:
            status = "✅ PASSED"
            passed += 1
            detail = f"Got 429 at request {result.got_429_at} (expected {result.expected_429_at})"
        else:
            status = "❌ FAILED"
            failed += 1
            if result.got_429_at:
                detail = f"Got 429 at request {result.got_429_at}, expected {result.expected_429_at}"
            else:
                detail = f"Never got 429 after {result.requests_made} requests (expected at {result.expected_429_at})"
        
        print(f"\n{result.tier.upper():20} {status}")
        print(f"  {detail}")
    
    print("\n" + "-" * 70)
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
    print("-" * 70)
    
    if failed > 0:
        print("\n⚠️  Some rate limit tests failed!")
        sys.exit(1)
    elif passed == 0:
        print("\n⚠️  No tests ran successfully. Is the server running?")
        sys.exit(1)
    else:
        print("\n✅ All rate limit tests passed!")


# =============================================================================
# Main
# =============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Test rate limiting on the CV Analysis Agent API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test all public tiers (no auth needed):
  python scripts/test_rate_limits.py
  
  # Test specific tier:
  python scripts/test_rate_limits.py --tier auth
  python scripts/test_rate_limits.py --tier public
  
  # Test authenticated tiers (need valid credentials):
  python scripts/test_rate_limits.py --email user@example.com --password mypass
  
  # Verbose output:
  python scripts/test_rate_limits.py --verbose
        """,
    )
    
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"Base URL of the API (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--tier",
        choices=list(RATE_LIMITS.keys()) + ["all", "public-only"],
        default="public-only",
        help="Which rate limit tier to test (default: public-only)",
    )
    parser.add_argument(
        "--email",
        help="Email for authentication (to test authenticated endpoints)",
    )
    parser.add_argument(
        "--password",
        help="Password for authentication (to test authenticated endpoints)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show all request statuses",
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("CV ANALYSIS AGENT - RATE LIMIT TESTER")
    print("=" * 70)
    print(f"Base URL: {args.base_url}")
    
    # Check if server is running
    try:
        response = requests.get(f"{args.base_url}/api/cv/health", timeout=5)
        print(f"Server status: ✅ Running (health check returned {response.status_code})")
    except requests.exceptions.RequestException:
        print("Server status: ❌ Not reachable")
        print(f"\nMake sure the server is running at {args.base_url}")
        print("Start it with: uvicorn app.main:app --reload")
        sys.exit(1)
    
    # Get auth token if credentials provided
    auth_token = None
    if args.email and args.password:
        print(f"\nAuthenticating as {args.email}...")
        auth_token = get_auth_token(args.base_url, args.email, args.password)
        if auth_token:
            print("Authentication: ✅ Success")
        else:
            print("Authentication: ❌ Failed (will skip authenticated tests)")
    
    # Determine which tiers to test
    if args.tier == "all":
        tiers_to_test = list(RATE_LIMITS.keys())
    elif args.tier == "public-only":
        tiers_to_test = [k for k, v in RATE_LIMITS.items() if not v.get("requires_auth", False)]
    else:
        tiers_to_test = [args.tier]
    
    print(f"\nTiers to test: {', '.join(tiers_to_test)}")
    
    # Run tests
    results = []
    for tier_name in tiers_to_test:
        tier_config = RATE_LIMITS[tier_name]
        
        # Wait a bit between tier tests to not mix rate limits
        if results:
            print("\n⏳ Waiting 2 seconds before next tier...")
            time.sleep(2)
        
        result = test_rate_limit(
            args.base_url,
            tier_name,
            tier_config,
            auth_token,
            args.verbose,
        )
        results.append(result)
    
    # Print summary
    print_results(results)


if __name__ == "__main__":
    main()
