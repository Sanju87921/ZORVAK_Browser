# GAVIX Browser — Host Environment Audit (Phase 0)

**Company:** ZORVAK Studios LLP  
**Date:** October 13, 2026  
**Audited System:** Local Development Machine  

---

## 1. Hardware Specifications

| Component | Detected Specification | Minimum Chromium Android Requirement | Status |
| :--- | :--- | :--- | :--- |
| **Operating System** | Windows 11 Home Single Language (64-bit, Build 26200) | Linux / WSL2 / macOS / Windows 10+ | Supported |
| **CPU** | 12th Gen Intel Core i5-12500H (12 Cores, 16 Threads) | 8+ Cores recommended | **Capable** |
| **System RAM** | 16.0 GB (15.7 GB visible, ~2.5 GB free at test time) | 16 GB minimum, 32 GB+ recommended | **Marginal** (requires swap/zram tuning) |
| **Disk Storage (C:)** | 277 GB Total, **8.36 GB Free** | 150 GB+ free for full checkout & build | **CRITICAL: INSUFFICIENT ON C:** |
| **Disk Storage (D:)** | 100 GB Total, **91.86 GB Free** | Secondary volume | Insufficient for 150GB+ full tree alone |
| **Disk Storage (E:)** | 97.6 GB Total, **91.11 GB Free** | Secondary volume | Insufficient for 150GB+ full tree alone |

> [!CAUTION]
> **Disk Space Bottleneck (P0):**
> A full native Chromium checkout (`src/` with git history, dependencies, Android toolchains, sysroots, and debug build output) requires **120 GB to 180 GB** of free contiguous disk space. Drive `C:` currently has only **8.36 GB** free. Before full native compilation, drive space must be consolidated or hosted on a dedicated external/cloud build runner.

---

## 2. Software Tooling Status

| Tool | Installed Version | Required Version | Status |
| :--- | :--- | :--- | :--- |
| **Git** | 2.49.0.1 (`C:\Program Files\Git\cmd\git.exe`) | Git 2.30+ | Installed |
| **Python** | Python 3.11.9 (`%LOCALAPPDATA%\Programs\Python\Python311`) | Python 3.8 - 3.11 | Installed |
| **Java JDK** | Oracle Java 24 (`javac 24.0.1`) | OpenJDK 17 (Chromium standard) | Java 24 installed (Chromium uses hermetic JDK 17) |
| **Android SDK** | `%LOCALAPPDATA%\Android\Sdk` | Android SDK 34 / 35 | Present (build-tools, platforms, NDK, cmdline-tools) |
| **WSL2** | Ubuntu 2 (Stopped) | WSL2 Ubuntu 22.04 LTS / 24.04 LTS | Installed & Supported |
| **depot_tools** | Not installed | Latest upstream depot_tools | **Missing** |
| **GN / Ninja** | Not in system PATH | Provided via `depot_tools` | Hermetic download via depot_tools |

---

## 3. Official Chromium Build Route for Android

Chromium's official Android build instructions strictly recommend a **Linux host environment** (Ubuntu 22.04 LTS or 24.04 LTS). On Windows, native compilation for Android is either done via **WSL2** or a dedicated cloud build machine.

### Strategy to Manage Disk & Build Constraints:
1. **Shallow / Sparse Checkout:** Use `--no-history --depth 1` when fetching Chromium via `gclient` to reduce tree size from ~60GB to ~25GB.
2. **Drive Target:** Target volume `D:` or `E:` or a high-speed external NVMe (or cloud builder) for checkout & build artifacts (`out/Default`).
3. **Hermetic Android Toolchain:** Use Chromium's internal `target_os = ["android"]` in `.gclient` to automatically download the exact tested NDK, Clang, and build-tools.
