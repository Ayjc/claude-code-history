"""Comprehensive test suite for performance validation."""

import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from history import HistoryReader


def test_cold_start():
    """Test cold start performance."""
    print("=" * 60)
    print("Test 1: Cold Start Performance")
    print("=" * 60)

    reader = HistoryReader(use_cache=True)
    reader.clear_cache()

    start = time.perf_counter()
    prompts = reader.get_all()
    elapsed = time.perf_counter() - start

    print(f"✓ Loaded {len(prompts)} prompts in {elapsed:.3f}s")

    # Performance criteria
    if elapsed < 3.0:
        print(f"✅ PASS: Cold start < 3s")
        return True
    else:
        print(f"❌ FAIL: Cold start too slow ({elapsed:.3f}s)")
        return False


def test_warm_start():
    """Test warm start with cache."""
    print("\n" + "=" * 60)
    print("Test 2: Warm Start Performance")
    print("=" * 60)

    reader = HistoryReader(use_cache=True)

    start = time.perf_counter()
    prompts = reader.get_all()
    elapsed = time.perf_counter() - start

    print(f"✓ Loaded {len(prompts)} prompts in {elapsed:.3f}s")

    # Performance criteria
    if elapsed < 0.5:
        print(f"✅ PASS: Warm start < 0.5s")
        return True
    else:
        print(f"❌ FAIL: Warm start too slow ({elapsed:.3f}s)")
        return False


def test_memory_cache():
    """Test in-memory cache."""
    print("\n" + "=" * 60)
    print("Test 3: In-Memory Cache Performance")
    print("=" * 60)

    reader = HistoryReader(use_cache=True)
    reader.get_all()  # Prime cache

    start = time.perf_counter()
    prompts = reader.get_all()
    elapsed = time.perf_counter() - start

    print(f"✓ Loaded {len(prompts)} prompts in {elapsed:.6f}s")

    # Performance criteria
    if elapsed < 0.001:
        print(f"✅ PASS: Memory cache < 1ms")
        return True
    else:
        print(f"❌ FAIL: Memory cache too slow ({elapsed*1000:.2f}ms)")
        return False


def test_search_performance():
    """Test search performance."""
    print("\n" + "=" * 60)
    print("Test 4: Search Performance")
    print("=" * 60)

    reader = HistoryReader(use_cache=True)
    reader.get_all()  # Prime cache

    queries = ["fix", "authentication", "refactor", "test"]
    all_passed = True

    for query in queries:
        start = time.perf_counter()
        results = reader.search(query)
        elapsed = time.perf_counter() - start

        print(f"✓ Search '{query}': {len(results)} results in {elapsed:.6f}s")

        if elapsed > 0.1:
            print(f"  ❌ FAIL: Search too slow ({elapsed*1000:.2f}ms)")
            all_passed = False

    if all_passed:
        print(f"✅ PASS: All searches < 100ms")
    else:
        print(f"❌ FAIL: Some searches too slow")

    return all_passed


def test_project_filter():
    """Test project filtering performance."""
    print("\n" + "=" * 60)
    print("Test 5: Project Filter Performance")
    print("=" * 60)

    reader = HistoryReader(use_cache=True)
    reader.get_all()  # Prime cache

    projects = reader.get_all_project_names()
    if not projects:
        print("⚠️  SKIP: No projects found")
        return True

    test_project = projects[0]

    start = time.perf_counter()
    results = reader.get_by_project(test_project)
    elapsed = time.perf_counter() - start

    print(f"✓ Filter by '{test_project}': {len(results)} results in {elapsed:.6f}s")

    if elapsed < 0.1:
        print(f"✅ PASS: Project filter < 100ms")
        return True
    else:
        print(f"❌ FAIL: Project filter too slow ({elapsed*1000:.2f}ms)")
        return False


def test_cache_validity():
    """Test cache validity checking."""
    print("\n" + "=" * 60)
    print("Test 6: Cache Validity")
    print("=" * 60)

    reader1 = HistoryReader(use_cache=True)
    prompts1 = reader1.get_all()

    # Create new reader, should use cache
    reader2 = HistoryReader(use_cache=True)
    start = time.perf_counter()
    prompts2 = reader2.get_all()
    elapsed = time.perf_counter() - start

    print(f"✓ Loaded {len(prompts2)} prompts in {elapsed:.3f}s")

    # Verify data integrity
    if len(prompts1) == len(prompts2):
        print(f"✅ PASS: Cache data integrity verified")
        return True
    else:
        print(f"❌ FAIL: Cache data mismatch ({len(prompts1)} vs {len(prompts2)})")
        return False


def test_cache_stats():
    """Test cache statistics."""
    print("\n" + "=" * 60)
    print("Test 7: Cache Statistics")
    print("=" * 60)

    reader = HistoryReader(use_cache=True)
    reader.get_all()

    stats = reader.get_cache_stats()

    print(f"✓ Cache enabled: {stats['enabled']}")
    print(f"✓ Cache size: {stats.get('size_mb', 0):.2f} MB")
    print(f"✓ Valid entries: {stats.get('valid_entries', 0)}")
    print(f"✓ In-memory cached: {stats.get('in_memory_cached', False)}")

    if stats['enabled'] and stats.get('valid_entries', 0) > 0:
        print(f"✅ PASS: Cache working correctly")
        return True
    else:
        print(f"❌ FAIL: Cache not working")
        return False


def test_no_cache_mode():
    """Test performance without cache."""
    print("\n" + "=" * 60)
    print("Test 8: No-Cache Mode")
    print("=" * 60)

    reader = HistoryReader(use_cache=False)

    start = time.perf_counter()
    prompts = reader.get_all()
    elapsed = time.perf_counter() - start

    print(f"✓ Loaded {len(prompts)} prompts in {elapsed:.3f}s (no cache)")

    if elapsed < 5.0:
        print(f"✅ PASS: No-cache mode < 5s")
        return True
    else:
        print(f"❌ FAIL: No-cache mode too slow ({elapsed:.3f}s)")
        return False


def generate_validation_report(results):
    """Generate validation report."""
    print("\n" + "=" * 60)
    print("VALIDATION REPORT")
    print("=" * 60)

    total = len(results)
    passed = sum(results.values())
    failed = total - passed

    print(f"\n📊 Test Results:")
    print(f"  Total:  {total}")
    print(f"  Passed: {passed} ✅")
    print(f"  Failed: {failed} ❌")

    print(f"\n📋 Details:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")

    if failed == 0:
        print(f"\n🎉 All tests passed! Performance optimization successful.")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Review performance issues.")
        return False


def main():
    """Run all validation tests."""
    print("🧪 Performance Validation Test Suite\n")

    results = {}

    # Run all tests
    results["Cold Start"] = test_cold_start()
    results["Warm Start"] = test_warm_start()
    results["Memory Cache"] = test_memory_cache()
    results["Search"] = test_search_performance()
    results["Project Filter"] = test_project_filter()
    results["Cache Validity"] = test_cache_validity()
    results["Cache Stats"] = test_cache_stats()
    results["No-Cache Mode"] = test_no_cache_mode()

    # Generate report
    all_passed = generate_validation_report(results)

    if all_passed:
        print("\n✅ Validation complete - All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Validation complete - Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
