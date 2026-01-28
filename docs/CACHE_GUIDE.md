# Cache Management Guide

## Overview

Claude Code History uses a multi-layer caching system for optimal performance:

1. **Memory Cache** - In-process cache (fastest, temporary)
2. **Disk Cache** - Persistent cache in `~/.cache/claude-code-history/` (fast, permanent)

## Cache Location

```bash
~/.cache/claude-code-history/
├── history_v1.pkl      # Main cache file (6-10 MB typical)
└── index_v1.pkl        # Index file (future use)
```

## Cache Behavior

### Automatic Invalidation

The cache automatically detects when files change:
- Checks file modification time (mtime)
- Checks file size
- Only reloads modified files
- Preserves valid cache entries

### Cache Lifecycle

```
First run:
  → Read all JSONL files (2.2s)
  → Parse JSON data
  → Build cache
  → Save to disk

Second run:
  → Load cache from disk (0.03s)
  → Validate entries
  → Use cached data

Subsequent runs:
  → Load from memory (0.001ms)
  → Instant access
```

## Manual Cache Management

### View Cache Stats

```python
from src.history import HistoryReader

reader = HistoryReader()
reader.get_all()  # Load data

stats = reader.get_cache_stats()
print(f"Cache size: {stats['size_mb']:.2f} MB")
print(f"Valid entries: {stats['valid_entries']}")
print(f"In-memory cached: {stats['in_memory_cached']}")
```

### Clear Cache

```python
from src.history import HistoryReader

reader = HistoryReader()
reader.clear_cache()
print("Cache cleared!")
```

Or manually:

```bash
rm -rf ~/.cache/claude-code-history/
```

### Disable Cache

```python
# Disable caching (always read from disk)
reader = HistoryReader(use_cache=False)
prompts = reader.get_all()
```

## Performance Tips

### 1. Let Cache Warm Up

First search of the day will be slower (2.2s) as it builds the cache. Subsequent searches are instant (20ms).

### 2. Don't Clear Cache Unnecessarily

The cache auto-invalidates when files change. Manual clearing is rarely needed.

### 3. Cache Size is Normal

Cache size (6-10 MB) is much smaller than raw data (400+ MB) and provides 55x speedup.

### 4. Memory Cache is Automatic

Once data is loaded, it stays in memory for the process lifetime. No configuration needed.

## Troubleshooting

### Cache Not Working

**Symptom**: Every search takes 2+ seconds

**Solution**:
```python
from src.history import HistoryReader

reader = HistoryReader()
stats = reader.get_cache_stats()

if not stats['enabled']:
    print("Cache is disabled")
elif stats['valid_entries'] == 0:
    print("Cache is empty or invalid")
    reader.clear_cache()  # Force rebuild
```

### Cache Corruption

**Symptom**: Errors when loading cache

**Solution**:
```bash
# Clear corrupted cache
rm -rf ~/.cache/claude-code-history/

# Next run will rebuild automatically
cch --list
```

### Stale Cache

**Symptom**: New prompts not appearing

**Solution**: Cache should auto-invalidate. If not:
```python
from src.history import HistoryReader

reader = HistoryReader()
reader.clear_cache()
prompts = reader.get_all(force_reload=True)
```

### High Memory Usage

**Symptom**: Process using too much memory

**Solution**: Memory cache is proportional to data size. For 3,771 prompts, expect ~150 MB. This is normal and provides instant access.

## Advanced Configuration

### Custom Cache Location

```python
from src.cache import HistoryCache
from pathlib import Path

# Override cache directory
HistoryCache.CACHE_DIR = Path("/custom/cache/path")

reader = HistoryReader()
prompts = reader.get_all()
```

### Cache Version

Cache version is embedded in filename (`history_v1.pkl`). When cache format changes, version increments automatically, preventing compatibility issues.

## Performance Metrics

### Typical Usage (3,771 prompts)

| Metric | Value |
|--------|-------|
| Raw data size | 408 MB |
| Cache size | 6.74 MB |
| Compression ratio | 60:1 |
| Cold start | 2.2s |
| Warm start | 0.03s |
| Memory access | 0.001ms |
| Search time | 20ms |

### Cache Efficiency

- **Space**: 1.6% of raw data size
- **Speed**: 55x faster than re-parsing
- **Hit rate**: ~100% after first load

## Best Practices

1. **Let it work automatically** - Cache manages itself
2. **Don't disable unless needed** - Cache provides huge speedup
3. **Clear only when troubleshooting** - Auto-invalidation handles updates
4. **Monitor cache stats** - Use `get_cache_stats()` to verify health
5. **Keep cache directory accessible** - Ensure `~/.cache/` is writable

## FAQ

**Q: How often should I clear the cache?**
A: Never, unless troubleshooting. Cache auto-invalidates.

**Q: Will cache grow indefinitely?**
A: No. Cache size is proportional to data size. For 10,000 prompts, expect ~20 MB.

**Q: Does cache work across different projects?**
A: Yes. Cache stores all projects together for efficiency.

**Q: What happens if cache file is deleted?**
A: Next run rebuilds cache automatically. No data loss.

**Q: Can I share cache between machines?**
A: No. Cache includes absolute file paths. Each machine needs its own cache.

**Q: Does cache affect search results?**
A: No. Cache is transparent. Results are identical with or without cache.

## Monitoring

### Check Cache Health

```bash
# Run validation tests
source venv/bin/activate
python3 tests/test_performance.py
```

### Benchmark Performance

```bash
# Compare with/without cache
python3 tests/compare_performance.py
```

### Profile Cache Operations

```bash
# Detailed profiling
python3 tests/profile_analysis.py
```

## Summary

The caching system provides:
- ⚡ 55-98x performance improvement
- 🔄 Automatic invalidation
- 💾 Efficient storage (1.6% of raw size)
- 🛡️ Transparent operation
- 🔧 Zero configuration needed

Just use the tool normally - caching works automatically!
