# VectorNav overlay

This directory is the VectorNav ground station's overlay on QGroundControl, built through upstream's own
custom-build mechanism (`cmake/CustomOptions.cmake`: `QGC_CUSTOM_DIR` defaults to `custom`, and the root
`CMakeLists.txt` includes `custom/cmake/CustomOverrides.cmake` and adds this directory when it exists).
Nothing under `src/` is edited; upstream edits that cannot be expressed as an overlay live as numbered patches
under `patches/` at the repository root, each offered upstream where it is general.

The staged plan is `VECTORNAV-GCS-PLAN.md` in the vectorsg-platform repository; this file records what the
overlay does at each phase.

| Phase | State | What the overlay does |
| --- | --- | --- |
| 1 | current | Nothing. `VectorNavPlugin` subclasses `QGCCorePlugin` with no overrides, both firmware-plugin factories stay enabled, `custom.qrc` is empty, `CustomOverrides.cmake` sets no variable. The build is stock v5.1.5 under the stock name with the stock test count; the screenshot harness (`src/VectorNavScreenshots.*`, `test/`) records the stock baseline. |
| 2 | planned | Branding: names, identifiers, icons, logo, fonts, palette, the Licences page, all through `CustomOverrides.cmake`, `custom.qrc` resource overrides and `VectorNavPlugin::paletteOverride`. |

Layout, following `custom-example/`:

- `CMakeLists.txt`: the `CUSTOM_*` cache variables `src/CMakeLists.txt` consumes (sources, libraries, include
  directories, definitions, Qt components) and the `.qrc` list.
- `cmake/CustomOverrides.cmake`: build variables overriding `cmake/CustomOptions.cmake`.
- `custom.qrc`: resource overrides under `/Custom/...` (phase 2 onwards).
- `src/`: `VectorNavPlugin.{h,cc}` and the screenshot driver.
- `test/`: the harness's unit test, registered only when `QGC_BUILD_TESTING` is on.
- `tools/`: the pixel-diff and override-drift scripts.
