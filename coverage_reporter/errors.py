class CoverageReporterError(RuntimeError):
    pass

class PluginError(CoverageReporterError):
    pass

class ConfigError(CoverageReporterError):
    pass
