# ============================================================================
# VectorNav overlay for QGroundControl (the official custom-build mechanism)
# ============================================================================
# Everything VectorNav lives under this directory; nothing under src/ is edited.
# Phase 1 (VECTORNAV-GCS-PLAN.md item 1.4): a no-op overlay. VectorNavPlugin
# subclasses QGCCorePlugin and overrides nothing, the stock firmware-plugin
# factories stay enabled, custom.qrc is empty. The build must behave as stock
# v5.1.5: same app name, same test count, same pixels.
# Reference: custom-example/CMakeLists.txt (copied, then reduced).

message(STATUS "QGC: Adding VectorNav overlay")

# ----------------------------------------------------------------------------
# Resources and QML import paths (the override mechanism, filled in phase 2)
# ----------------------------------------------------------------------------
list(APPEND CUSTOM_RESOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/custom.qrc
)
set(QGC_RESOURCES ${QGC_RESOURCES} ${CUSTOM_RESOURCES} CACHE STRING "Paths to .qrc Resources" FORCE)

# ----------------------------------------------------------------------------
# Plugin sources: the QGCCorePlugin subclass the core instantiates
# (src/API/QGCCorePlugin.cc: CUSTOMCLASS::instance() under QGC_CUSTOM_BUILD)
# ----------------------------------------------------------------------------
set(CUSTOM_SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/src/VectorNavPlugin.cc
    ${CMAKE_CURRENT_SOURCE_DIR}/src/VectorNavPlugin.h
    CACHE INTERNAL "" FORCE
)

set(CUSTOM_LIBRARIES
    ""
    CACHE INTERNAL "" FORCE
)

set(CUSTOM_INCLUDE_DIRECTORIES
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    CACHE INTERNAL "" FORCE
)

set(CUSTOM_DEFINITIONS
    QGC_CUSTOM_BUILD
    CUSTOMHEADER="VectorNavPlugin.h"
    CUSTOMCLASS=VectorNavPlugin
    CACHE INTERNAL "" FORCE
)

set(CUSTOM_QT_COMPONENTS
    Core
    CACHE INTERNAL "" FORCE
)
