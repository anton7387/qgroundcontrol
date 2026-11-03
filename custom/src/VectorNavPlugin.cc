#include "VectorNavPlugin.h"

#include <QtCore/QApplicationStatic>

Q_APPLICATION_STATIC(VectorNavPlugin, _vectorNavPluginInstance);

VectorNavPlugin::VectorNavPlugin(QObject *parent)
    : QGCCorePlugin(parent)
{
}

QGCCorePlugin *VectorNavPlugin::instance()
{
    return _vectorNavPluginInstance();
}
