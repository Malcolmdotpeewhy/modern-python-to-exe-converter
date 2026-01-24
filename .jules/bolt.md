# Bolt's Journal - Modern Python to EXE Converter

## 2025-05-15 - Performance Assessment

**Learning:** The application performs heavy directory traversal and image processing. The `search_icons` function is a major bottleneck because it walks the directory tree multiple times and iterates over every file found even when only a few are needed for display. Thread safety in logging is also a concern as it performs UI updates from background threads, which can lead to performance degradation or crashes.

**Action:**
1. Refactor `search_icons` to use a single-pass `os.walk`.
2. Implement lazy loading/limiting for icon search.
3. Cache icon generation results.
4. Optimize logging with thread-safe queue and batched updates.
5. Cache scrollable targets in mousewheel events.

## 2025-05-16 - Testing Tkinter in Headless Environments

**Learning:** When unit testing Tkinter components that use f-string formatting on `StringVar` or `DoubleVar` results (e.g., `f"{var.get():.0%}"`), `MagicMock` will fail with a `TypeError` because it doesn't support the format specifier.

**Action:** Always configure mocks for Tkinter variables to return concrete numeric or string values (e.g., `mock_tk.DoubleVar.return_value.get.return_value = 0.95`) before they are accessed by UI code.
