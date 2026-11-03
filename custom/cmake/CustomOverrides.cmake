# ============================================================================
# VectorNav build overrides
# ============================================================================
# Included by the root CMakeLists.txt as soon as the custom/ directory is
# detected (CMakeLists.txt lines 51-56), before any target exists. Branding
# variables (QGC_APP_NAME, QGC_ORG_NAME, QGC_PACKAGE_NAME, the icons, the
# desktop entry) go here in phase 2 (VECTORNAV-GCS-PLAN.md item 2.2).
#
# Phase 1 (item 1.4): intentionally empty. The stock values of
# cmake/CustomOptions.cmake apply unchanged, both firmware-plugin factories
# stay enabled, and the app starts under the stock name.
