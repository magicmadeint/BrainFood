from brainfood.agent import BrainFoodAgent

def test_scoring_and_relevance():
    print("=== Testing score_atomic() + get_context() relevance ===\n")
    
    brain = BrainFoodAgent()

    high_quality = {
        "name": "robust_retry",
        "category": "development",
        "language": "python",
        "full_code": "def robust_retry(func, retries=5, backoff=0.5):\n    import time\n    for i in range(retries):\n        try:\n            return func()\n        except Exception as e:\n            if i == retries - 1:\n                raise\n            time.sleep(backoff * (2 ** i))\n    return None",
        "description": "Production-grade retry with exponential backoff",
        "dependencies": ["time"]
    }

    low_quality = {
        "name": "simple_retry",
        "category": "development",
        "language": "python",
        "full_code": "def simple_retry(f): return f()",
        "description": "Basic retry"
    }

    brain.ingest(high_quality, "development")
    brain.ingest(low_quality, "development")

    score_high = brain.score_atomic("development", "robust_retry")
    score_low = brain.score_atomic("development", "simple_retry")

    print(f"robust_retry score:   {score_high:.2f}")
    print(f"simple_retry score:   {score_low:.2f}")

    context_error = brain.get_context("retry error handling", max_items=3)
    context_other = brain.get_context("database connection", max_items=3)

    print(f"\nContext for 'retry error handling': {len(context_error)} results")
    print(f"Context for 'database connection':   {len(context_other)} results")

    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_scoring_and_relevance()
