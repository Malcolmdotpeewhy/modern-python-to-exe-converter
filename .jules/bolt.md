# Bolt's Journal - Modern Python to EXE Converter

## 2025-05-15 - Performance Assessment

**Learning:** The application performs heavy directory traversal and image processing. The `search_icons` function is a major bottleneck because it walks the directory tree multiple times and iterates over every file found even when only a few are needed for display. Thread safety in logging is also a concern as it performs UI updates from background threads, which can lead to performance degradation or crashes.

**Action:**
1. Refactor `search_icons` to use a single-pass `os.walk`.
2. Implement lazy loading/limiting for icon search.
3. Cache icon generation results.
4. Optimize logging with thread-safe queue and batched updates.
5. Cache scrollable targets in mousewheel events.

## 2025-05-16 - Subprocess and Data Structure Optimizations

**Learning:** Subprocess calls for checking external tool versions (like PyInstaller) are a significant source of UI lag, especially on Windows where process creation is expensive. Additionally, performing (N)$ lookups inside loops when selecting files leads to (N^2)$ scaling that becomes noticeable even with dozens of files. UI responsiveness can be further improved by batching state changes in log processing.

**Action:**
1. Always cache results of version checks and other expensive external commands.
2. Use sets for duplicate checking in file selection and similar list-management tasks.
3. Batch UI state updates and auto-scrolling in high-frequency event loops like log processing.
4. Implement shape mask caching to speed up icon generation across different sizes.
