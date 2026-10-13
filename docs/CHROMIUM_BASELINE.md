# GAVIX Browser — Chromium Baseline Specification

**Milestone:** Chromium 130  
**Branch:** `chromium/6723`  
**Target:** `chrome_public_apk`  
**Target OS:** Android  
**Architecture:** `arm64`  

---

## 1. Reproducible Baseline Metadata

- **Milestone:** M130 (Current Chromium Stable Channel)
- **Branch ID:** 6723
- **Git Remote:** `https://chromium.googlesource.com/chromium/src.git`
- **Official Tracker:** [Chromium Dash M130](https://chromiumdash.appspot.com/milestones)

---

## 2. Baseline `args.gn` Configuration

```gn
# Unmodified Chromium Android Baseline
target_os = "android"
target_cpu = "arm64"
is_debug = false
is_component_build = false
is_official_build = false
symbol_level = 0
blink_symbol_level = 0
android_channel = "stable"
enable_nacl = false
dcheck_always_on = false
treat_warnings_as_errors = false
```

---

## 3. Toolchain Bindings

- **Host Compiler:** Hermetic Clang (downloaded via `depot_tools` hooks)
- **Android NDK:** Hermetic Chromium Android NDK r26 / r27
- **Android Target SDK:** API Level 34 / 35
- **Minimum Android SDK:** API Level 26 (Android 8.0+)
- **Build System:** GN (`gn gen out/Default`) + Ninja / Siso (`autoninja -C out/Default chrome_public_apk`)

---

## 4. Security Baseline Checklist (Strictly Enforced)

- [x] Renderer Sandbox: **ENABLED**
- [x] Strict Site Isolation: **ENABLED**
- [x] TLS Certificate Validation: **ENABLED**
- [x] Android App Process Isolation: **ENABLED**
- [x] No single-process mode shortcuts
