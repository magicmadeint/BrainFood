from brainfood.agent import BrainFoodAgent

def main():
    print("=== BrainFood v0.1 Basic Test ===\n")
    
    brain = BrainFoodAgent()

    component = {
        "name": "retry_with_backoff",
        "category": "development",
        "language": "python",
        "full_code": "def retry_with_backoff(func, max_retries=3):\n    for attempt in range(max_retries):\n        try:\n            return func()\n        except Exception as e:\n            if attempt == max_retries - 1:\n                raise\n            print(f\"Attempt {attempt + 1} failed: {e}. Retrying...\")\n    return None",
        "dependencies": []
    }

    success = brain.ingest(component, category="development")
    print(f"Ingest successful: {success}")

    retrieved = brain.get_atomic("development", "retry_with_backoff")
    print("\nRetrieved component:")
    print(retrieved.get("name") if retrieved else "Not found")

    context = brain.get_context("error handling and retries")
    print(f"\nContext items found: {len(context)}")

    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()