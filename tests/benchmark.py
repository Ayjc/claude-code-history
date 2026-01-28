"""Performance benchmark for Claude Code History."""

import time
import tracemalloc
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from history import HistoryReader


def measure_time(func, *args, **kwargs):
    """Measure execution time of a function."""
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    return result, end - start


def measure_memory(func, *args, **kwargs):
    """Measure memory usage of a function."""
    tracemalloc.start()
    result = func(*args, **kwargs)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, current, peak


def benchmark_get_all():
    """Benchmark get_all() method."""
    print("=" * 60)
    print("Benchmark: get_all()")
    print("=" * 60)

    reader = HistoryReader()

    # Measure time
    prompts, elapsed = measure_time(reader.get_all)
    print(f"✓ Loaded {len(prompts)} prompts")
    print(f"✓ Time: {elapsed:.3f}s")

    # Measure memory
    reader2 = HistoryReader()
    prompts2, current, peak = measure_memory(reader2.get_all)
    print(f"✓ Memory (current): {current / 1024 / 1024:.2f} MB")
    print(f"✓ Memory (peak): {peak / 1024 / 1024:.2f} MB")

    return prompts, elapsed, peak


def benchmark_search(prompts):
    """Benchmark search() method."""
    print("\n" + "=" * 60)
    print("Benchmark: search()")
    print("=" * 60)

    reader = HistoryReader()

    # Test different query types
    queries = [
        ("fix", "Common word"),
        ("authentication", "Specific term"),
        ("refactor the database", "Multi-word phrase"),
        ("xyz123abc", "Non-existent"),
    ]

    for query, desc in queries:
        results, elapsed = measure_time(reader.search, query)
        print(f"✓ Query '{query}' ({desc}): {len(results)} results in {elapsed:.4f}s")


def benchmark_project_filter(prompts):
    """Benchmark project filtering."""
    print("\n" + "=" * 60)
    print("Benchmark: Project Filtering")
    print("=" * 60)

    reader = HistoryReader()

    # Get all project names
    projects = reader.get_all_project_names()
    print(f"✓ Total projects: {len(projects)}")

    if projects:
        # Test single project filter
        test_project = projects[0]
        results, elapsed = measure_time(reader.get_by_project, test_project)
        print(f"✓ Filter by '{test_project}': {len(results)} results in {elapsed:.4f}s")

        # Test multiple project filter
        if len(projects) >= 3:
            test_projects = projects[:3]
            results, elapsed = measure_time(reader.get_by_projects, test_projects)
            print(f"✓ Filter by 3 projects: {len(results)} results in {elapsed:.4f}s")


def benchmark_cold_start():
    """Benchmark cold start (first load)."""
    print("\n" + "=" * 60)
    print("Benchmark: Cold Start")
    print("=" * 60)

    # Simulate cold start
    reader = HistoryReader()
    start = time.perf_counter()
    prompts = reader.get_all()
    end = time.perf_counter()

    print(f"✓ Cold start time: {end - start:.3f}s")
    print(f"✓ Prompts loaded: {len(prompts)}")

    return end - start


def benchmark_repeated_loads():
    """Benchmark repeated loads (no caching)."""
    print("\n" + "=" * 60)
    print("Benchmark: Repeated Loads (No Cache)")
    print("=" * 60)

    times = []
    for i in range(3):
        reader = HistoryReader()
        start = time.perf_counter()
        prompts = reader.get_all()
        end = time.perf_counter()
        times.append(end - start)
        print(f"✓ Load {i+1}: {end - start:.3f}s ({len(prompts)} prompts)")

    avg_time = sum(times) / len(times)
    print(f"✓ Average: {avg_time:.3f}s")

    return avg_time


def analyze_file_distribution():
    """Analyze file size distribution."""
    print("\n" + "=" * 60)
    print("Analysis: File Distribution")
    print("=" * 60)

    reader = HistoryReader()

    if not reader.PROJECTS_DIR.exists():
        print("✗ Projects directory not found")
        return

    file_sizes = []
    line_counts = []

    for project in reader.PROJECTS_DIR.iterdir():
        if project.is_dir():
            for session_file in project.glob("*.jsonl"):
                size = session_file.stat().st_size
                file_sizes.append(size)

                # Count lines
                try:
                    with open(session_file, 'r') as f:
                        lines = sum(1 for _ in f)
                        line_counts.append(lines)
                except:
                    pass

    if file_sizes:
        total_size = sum(file_sizes)
        avg_size = total_size / len(file_sizes)
        max_size = max(file_sizes)

        print(f"✓ Total files: {len(file_sizes)}")
        print(f"✓ Total size: {total_size / 1024 / 1024:.2f} MB")
        print(f"✓ Average file size: {avg_size / 1024:.2f} KB")
        print(f"✓ Largest file: {max_size / 1024:.2f} KB")

    if line_counts:
        total_lines = sum(line_counts)
        avg_lines = total_lines / len(line_counts)
        max_lines = max(line_counts)

        print(f"✓ Total lines: {total_lines}")
        print(f"✓ Average lines per file: {avg_lines:.1f}")
        print(f"✓ Largest file: {max_lines} lines")


def generate_report(prompts, load_time, peak_memory):
    """Generate performance report."""
    print("\n" + "=" * 60)
    print("PERFORMANCE REPORT")
    print("=" * 60)

    print(f"\n📊 Dataset:")
    print(f"  - Total prompts: {len(prompts)}")

    print(f"\n⚡ Performance:")
    print(f"  - Load time: {load_time:.3f}s")
    print(f"  - Peak memory: {peak_memory / 1024 / 1024:.2f} MB")
    print(f"  - Throughput: {len(prompts) / load_time:.0f} prompts/s")

    # Performance rating
    if load_time < 1.0:
        rating = "🟢 Excellent"
    elif load_time < 3.0:
        rating = "🟡 Good"
    elif load_time < 5.0:
        rating = "🟠 Fair"
    else:
        rating = "🔴 Needs optimization"

    print(f"\n📈 Rating: {rating}")

    # Bottleneck analysis
    print(f"\n🔍 Potential Bottlenecks:")

    if load_time > 2.0:
        print(f"  ⚠️  Slow load time ({load_time:.3f}s)")
        print(f"     → Consider: caching, indexing, or lazy loading")

    if peak_memory > 100 * 1024 * 1024:  # 100 MB
        print(f"  ⚠️  High memory usage ({peak_memory / 1024 / 1024:.2f} MB)")
        print(f"     → Consider: streaming, pagination, or data compression")

    prompts_per_mb = len(prompts) / (peak_memory / 1024 / 1024)
    if prompts_per_mb < 100:
        print(f"  ⚠️  Low memory efficiency ({prompts_per_mb:.0f} prompts/MB)")
        print(f"     → Consider: optimizing data structures")

    print(f"\n💡 Optimization Opportunities:")
    print(f"  1. Add file-based caching with mtime checking")
    print(f"  2. Implement incremental loading")
    print(f"  3. Use binary format (pickle/msgpack) for cache")
    print(f"  4. Add search index for faster queries")
    print(f"  5. Parallelize file reading")


def main():
    """Run all benchmarks."""
    print("🚀 Claude Code History - Performance Benchmark")
    print()

    # Analyze file distribution
    analyze_file_distribution()

    # Benchmark cold start
    cold_start_time = benchmark_cold_start()

    # Benchmark get_all
    prompts, load_time, peak_memory = benchmark_get_all()

    # Benchmark repeated loads
    avg_load_time = benchmark_repeated_loads()

    # Benchmark search
    benchmark_search(prompts)

    # Benchmark project filtering
    benchmark_project_filter(prompts)

    # Generate report
    generate_report(prompts, load_time, peak_memory)

    print("\n✅ Benchmark complete!")


if __name__ == "__main__":
    main()
