"""Detailed profiling analysis for Claude Code History."""

import cProfile
import pstats
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from history import HistoryReader


def profile_get_all():
    """Profile get_all() method in detail."""
    print("=" * 60)
    print("Profiling: get_all()")
    print("=" * 60)

    profiler = cProfile.Profile()
    reader = HistoryReader()

    profiler.enable()
    prompts = reader.get_all()
    profiler.disable()

    # Print stats
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(30)
    print(s.getvalue())

    return prompts


def profile_search():
    """Profile search() method."""
    print("\n" + "=" * 60)
    print("Profiling: search()")
    print("=" * 60)

    profiler = cProfile.Profile()
    reader = HistoryReader()

    profiler.enable()
    results = reader.search("fix")
    profiler.disable()

    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(30)
    print(s.getvalue())


def analyze_io_operations():
    """Analyze I/O operations."""
    print("\n" + "=" * 60)
    print("Analysis: I/O Operations")
    print("=" * 60)

    reader = HistoryReader()

    if not reader.PROJECTS_DIR.exists():
        print("✗ Projects directory not found")
        return

    total_files = 0
    total_size = 0
    total_lines = 0

    for project in reader.PROJECTS_DIR.iterdir():
        if project.is_dir():
            for session_file in project.glob("*.jsonl"):
                total_files += 1
                total_size += session_file.stat().st_size

                try:
                    with open(session_file, 'r') as f:
                        total_lines += sum(1 for _ in f)
                except:
                    pass

    print(f"✓ Total files to read: {total_files}")
    print(f"✓ Total data to read: {total_size / 1024 / 1024:.2f} MB")
    print(f"✓ Total lines to parse: {total_lines}")
    print(f"✓ Average file size: {total_size / total_files / 1024:.2f} KB")

    # Estimate I/O time
    # Typical SSD read speed: ~500 MB/s
    estimated_io_time = total_size / (500 * 1024 * 1024)
    print(f"\n💡 Estimated pure I/O time: {estimated_io_time:.3f}s")
    print(f"💡 Actual time: ~1.8s")
    print(f"💡 Overhead: ~{1.8 - estimated_io_time:.3f}s (JSON parsing, object creation)")


def main():
    """Run profiling analysis."""
    print("🔍 Claude Code History - Profiling Analysis\n")

    # Analyze I/O
    analyze_io_operations()

    # Profile get_all
    prompts = profile_get_all()

    # Profile search
    profile_search()

    print("\n✅ Profiling complete!")


if __name__ == "__main__":
    main()
