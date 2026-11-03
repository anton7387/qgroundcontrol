#pragma once

#include "QGCCorePlugin.h"

/// The VectorNav core plugin. QGroundControl instantiates it in place of the
/// stock QGCCorePlugin because the build defines CUSTOMCLASS=VectorNavPlugin
/// (custom/CMakeLists.txt; src/API/QGCCorePlugin.cc instance()).
///
/// Phase 1 (VECTORNAV-GCS-PLAN.md item 1.4): no overrides. Every virtual of
/// QGCCorePlugin keeps its stock behaviour, so the build is stock v5.1.5 under
/// the stock name with the stock test count.
class VectorNavPlugin : public QGCCorePlugin
{
    Q_OBJECT

public:
    explicit VectorNavPlugin(QObject *parent = nullptr);

    static QGCCorePlugin *instance();
};
