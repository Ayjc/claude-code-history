"""Compare performance between original and optimized versions."""

import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from history import HistoryReader as OriginalReader
from history_optimized import HistoryReader as OptimizedReader


def measure_time(func, *args, **kwargs):
    """Measure execution time."""
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    return result, end - start


def test_original():
    """Test original implementation."""
    print("=" * 60)
    print("Testing: ORIGINAL Implementation")
    print("=" * 60)

    reader = OriginalReader()

    # Test 1: First load
    prompts, time1 = measure_time(reader.get_all)
    print(f"✓ First load: {time1:.3f}s ({len(prompts)} prompts)")

    # Test 2: Second load (no cache)
    reader2 = OriginalReader()
    prompts2, time2 = measure_time(reader2.get_all)
    print(f"✓ Second load: {time2:.3f}s ({len(prompts2)} prompts)")

    # Test 3: Search
    reader3 = OriginalReader()
    results, time3 = measure_time(reader3.search, "fix")
    print(f"✓ Search 'fix': {time3:.3f}s ({len(results)} results)")

    return {
        'first_load': time1,
        'second_load': time2,
        'search': time3,
        'count': len(prompts),
    }


def test_optimized():
    """Test optimized implementation."""
    print("\n" + "=" * 60)
    print("Testing: OPTIMIZED Implementation")
    print("=" * 60)

    # Clear cache first
    reader = OptimizedReader(use_cache=True, max_workers=4)
    reader.clear_cache()

    # Test 1: First load (cold cache)
    prompts, time1 = measure_time(reader.get_all)
    print(f"✓ First load (cold cache): {time1:.3f}s ({len(prompts)} prompts)")

    # Test 2: Second load (warm cache)
    reader2 = OptimizedReader(use_cache=True, max_workers=4)
    prompts2, time2 = measure_time(reader2.get_all)
    print(f"✓ Second load (warm cache): {time2:.3f}s ({len(prompts2)} prompts)")

    # Test 3: Third load (in-memory cache)
    prompts3, time3 = measure_time(reader2.get_all)
    print(f"✓ Third load (in-memory): {time3:.3f}s ({len(prompts3)} prompts)")

    # Test 4: Search (uses in-memory cache)
    results, time4 = measure_time(reader2.search, "fix")
    print(f"✓ Search 'fix': {time4:.3f}s ({len(results)} results)")

    # Test 5: New reader with warm cache
    reader3 = OptimizedReader(use_cache=True, max_workers=4)
    results2, time5 = measure_time(reader3.search, "fix")
    print(f"✓ Search 'fix' (new reader): {time5:.3f}s ({len(results2)} results)")

    # Cache stats
    stats = reader3.get_cache_stats()
    print(f"\n📊 Cache Stats:")
    print(f"  - Enabled: {stats['enabled']}")
    print(f"  - Size: {stats.get('size_mb', 0):.2f} MB")
    print(f"  - Valid entries: {stats.get('valid_entries', 0)}")

    return {
        'first_load_cold': time1,
        'second_load_warm': time2,
        'third_load_memory': time3,
        'search_memory': time4,
        'search_warm': time5,
        'count': len(prompts),
    }


def test_parallel_workers():
    """Test different worker counts."""
    print("\n" + "=" * 60)
    print("Testing: Parallel Workers")
    print("=" * 60)

    worker_counts = [1, 2, 4, 8]
    results = {}

    for workers in worker_counts:
        reader = OptimizedReader(use_cache=False, max_workers=workers)
        prompts, elapsed = measure_time(reader.get_all)
        results[workers] = elapsed
        print(f"✓ {workers} workers: {elapsed:.3f}s ({len(prompts)} prompts)")

    # Find best
    best_workers = min(results, key=results.get)
    print(f"\n🏆 Best: {best_workers} workers ({results[best_workers]:.3f}s)")

    return results


def generate_comparison_report(original, optimized):
    """Generate comparison report."""
    print("\n" + "=" * 60)
    print("PERFORMANCE COMPARISON REPORT")
    print("=" * 60)

    print(f"\n📊 Dataset: {original['count']} prompts")

    print(f"\n⚡ First Load (Cold):")
    print(f"  Original:  {original['first_load']:.3f}s")
    print(f"  Optimized: {optimized['first_load_cold']:.3f}s")
    speedup = original['first_load'] / optimized['first_load_cold']
    print(f"  Speedup:   {speedup:.2f}x")

    print(f"\n⚡ Second Load:")
    print(f"  Original (no cache):  {original['second_load']:.3f}s")
    print(f"  Optimized (warm):     {optimized['second_load_warm']:.3f}s")
    speedup = original['second_load'] / optimized['second_load_warm']
    print(f"  Speedup:              {speedup:.2f}x")

    print(f"\n⚡ In-Memory Cache:")
    print(f"  Optimized: {optimized['third_load_memory']:.3f}s")
    speedup = original['second_load'] / optimized['third_load_memory']
    print(f"  Speedup:   {speedup:.2f}x vs original")

    print(f"\n⚡ Search Performance:")
    print(f"  Original:           {original['search']:.3f}s")
    print(f"  Optimized (memory): {optimized['search_memory']:.3f}s")
    print(f"  Optimized (warm):   {optimized['search_warm']:.3f}s")
    speedup1 = original['search'] / optimized['search_memory']
    speedup2 = original['search'] / optimized['search_warm']
    print(f"  Speedup (memory):   {speedup1:.2f}x")
    print(f"  Speedup (warm):     {speedup2:.2f}x")

    # Overall improvement
    print(f"\n🎯 Key Improvements:")

    cache_speedup = original['second_load'] / optimized['second_load_warm']
    if cache_speedup > 10:
        print(f"  🟢 Disk cache: {cache_speedup:.0f}x faster")
    elif cache_speedup > 5:
        print(f"  🟡 Disk cache: {cache_speedup:.1f}x faster")
    else:
        print(f"  🟠 Disk cache: {cache_speedup:.1f}x faster")

    memory_speedup = original['search'] / optimized['search_memory']
    if memory_speedup > 100:
        print(f"  🟢 Memory cache: {memory_speedup:.0f}x faster")
    elif memory_speedup > 50:
        print(f"  🟡 Memory cache: {memory_speedup:.0f}x faster")
    else:
        print(f"  🟠 Memory cache: {memory_speedup:.1f}x faster")

    # User experience
    print(f"\n👤 User Experience:")
    if optimized['search_memory'] < 0.1:
        print(f"  🟢 Search feels instant ({optimized['search_memory']*1000:.0f}ms)")
    elif optimized['search_memory'] < 0.5:
        print(f"  🟡 Search is very fast ({optimized['search_memory']*1000:.0f}ms)")
    else:
        print(f"  🟠 Search is fast ({optimized['search_memory']:.2f}s)")

    if optimized['second_load_warm'] < 0.5:
        print(f"  🟢 Startup is instant ({optimized['second_load_warm']*1000:.0f}ms)")
    elif optimized['second_load_warm'] < 1.0:
        print(f"  🟡 Startup is fast ({optimized['second_load_warm']:.2f}s)")
    else:
        print(f"  🟠 Startup is acceptable ({optimized['second_load_warm']:.2f}s)")


def main():
    """Run comparison tests."""
    print("🚀 Performance Comparison: Original vs Optimized\n")

    # Test original
    original_results = test_original()

    # Test optimized
    optimized_results = test_optimized()

    # Test parallel workers
    worker_results = test_parallel_workers()

    # Generate report
    generate_comparison_report(original_results, optimized_results)

    print("\n✅ Comparison complete!")


if __name__ == "__main__":
    main()
