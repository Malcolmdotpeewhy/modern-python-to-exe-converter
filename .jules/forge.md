## 2024-05-23 — Process Spawning Overhead
**Learning:** Checking external tool versions via `subprocess.run` (e.g., `pyinstaller --version`) adds 5-50ms overhead per call. In GUI apps, repeating this on every button click or action makes the UI feel sluggish and wastes CPU.
**Action:** Cache the result of external tool checks in an instance variable or singleton. Invalidate the cache only when an explicit "install/update" action occurs.

## 2024-05-23 — Avoid Optimizing Cold Paths
**Learning:** Attempting to optimize object creation in a GUI setup phase (e.g., button factories) added complexity and potential state synchronization bugs (stale cache on theme change) without measurable performance benefit.
**Action:** Strict adherence to "Measure first, optimize second". Do not optimize initialization code unless profiling shows it is a major bottleneck (e.g., taking >100ms).
