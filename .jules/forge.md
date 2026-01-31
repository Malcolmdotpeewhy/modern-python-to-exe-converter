
## 2025-05-17 - Performance Bottlenecks in Monolithic GUI

**Learning:** In a monolithic Tkinter application like this, the single thread is easily choked by heavy image processing and recursive directory walks. Using `os.scandir` instead of `os.walk` and implementing progressive image resizing provided the most significant perceived performance gains for the Icon Manager.

**Action:** Prioritize `os.scandir` for any future directory traversal tasks and ensure all image processing steps utilize intermediate results where possible.
