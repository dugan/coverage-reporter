"""
Configuration for the coverage-reporter tool.  

Somewhat vestigial, as it turns out the coverage-reporter tool doesn't have any options, just plugins with options.
It will likely be merged with the plugin manager.
"""
import ConfigParser
import itertools
import optparse
import os
import shlex

from coverage_reporter.errors import ConfigError


# Default set of plugins.  Need to figure out some way to add plugins without having to re-specify all of these,
# as you probably really want these.  Perhaps move to loading plugins from a set of directories, and only require
# hard-coding the submodule name?

DEFAULT_PLUGINS = ['coverage_reporter.collectors.figleaf_collector.FigleafCollector',
                   'coverage_reporter.collectors.coverage_collector.CoveragePyCollector',
                   'coverage_reporter.filters.patch.FilterByPatch',
                   'coverage_reporter.filters.exclude.ExcludeFilter',
                   'coverage_reporter.filters.minimum.MinimumMissingFilter',
                   'coverage_reporter.reports.summarize.SummarizeReporter',
                   'coverage_reporter.reports.annotate.AnnotateReporter',
                   ]


DEFAULT_PATHS = ['/etc/coverage_reporter', os.path.expanduser('~/.coverage_reporter'), '.coverage_reporter']

class CoverageReporterConfig(object):
    def __init__(self, read_defaults=True):
        self.cfg = ConfigParser.RawConfigParser()
        if read_defaults:
            self.read(*DEFAULT_PATHS)
        self.plugin_classes = DEFAULT_PLUGINS

    def read(self, *path_list):
        self.cfg.read(path_list)

    def get_section(self, name):
        return ConfigSection(self.cfg, name)

class ConfigSection(object):
    """
    Very simply wrapper around pretty poor ConfigParser interface.  Sets the current section name so it is only specified once, and then 
    provides a number of safe methods that return None when no element is available.
    """

    def __init__(self, cfg, name):
        self.cfg = cfg
        self.name = name
        if not cfg.has_section(name):
            cfg.add_section(name)

    def get(self, key, default=None):
        if self.cfg.has_option(self.name, key):
            return self.cfg.get(self.name, key)
        return default

    def set(self, key, value):
        return self.cfg.set(self.name, key, str(value))

    def set_list(self, key, value):
        return self.cfg.set(self.name, key, value)

    def get_int(self, key, default=None):
        value = self.get(key, None)
        if value is None:
            return default
        return int(value)

    def get_list(self, item, default=None):
        value = self.get(item, default)
        if value is default:
            return value
        lines = [ line.strip() for line in value.splitlines() ]
        return list(itertools.chain(*[ shlex.split(line) for line in lines if line and not line.startswith('#') ]))
