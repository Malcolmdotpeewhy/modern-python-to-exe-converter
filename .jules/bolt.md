# Bolt's Journal - Modern Python to EXE Converter

## 2025-05-15 - Performance Assessment

**Learning:** The application performs heavy directory traversal and image processing. The `search_icons` function is a major bottleneck because it walks the directory tree multiple times and iterates over every file found even when only a few are needed for display. Thread safety in logging is also a concern as it performs UI updates from background threads, which can lead to performance degradation or crashes.

**Action:**
1. Refactor `search_icons` to use a single-pass `os.walk`.
2. Implement lazy loading/limiting for icon search.
3. Cache icon generation results.
4. Optimize logging with thread-safe queue and batched updates.
5. Cache scrollable targets in mousewheel events.

## 2025-05-15 - Multi-threaded UI & Logging Optimization

**Learning:** Redundant UI state changes (e.g., toggling `tk.NORMAL`/`tk.DISABLED` on every log line) and unsafe `root.update()` calls from background threads cause significant performance overhead and potential instability. Batching UI updates and strictly using `root.after()` for thread-safe UI interactions are critical for performance in Tkinter apps.

**Action:**
1. Batch multiple log entries into a single UI update to reduce overhead.
2. Replace all direct UI calls from background threads with `root.after()`.
3. Use in-place image operations (`putalpha`) to reduce memory pressure during batch processing.
4. Cache external dependency checks to avoid repetitive subprocess overhead.
