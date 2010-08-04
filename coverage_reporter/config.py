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

from coverage_reporter.plugins import PluginManager
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


class CoverageReporterConfig(object):
    def __init__(self):
        self.plugin_manager = PluginManager()

    def load_plugins(self):
        cfg = ConfigParser.RawConfigParser()
        cfg.read(['/etc/coverage_reporter', os.path.expanduser('~/.coverage_reporter'), '.coverage_reporter'])
        section = ConfigSection(cfg, 'coverage_reporter')
        plugin_classes = section.get_list('plugins', [])
        if not plugin_classes:
            plugin_classes = DEFAULT_PLUGINS

        def get_section(name):
            return ConfigSection(cfg, 'coverage_reporter')
        self.plugin_manager.load_plugins(get_section, plugin_classes)
        self.plugins_loaded = True

    def get_option_parser(self):
        parser = optparse.OptionParser()
        self.plugin_manager.call_method('add_options', parser)
        return parser

    def parse_options(self, args):
        parser = self.get_option_parser()
        options, args = parser.parse_args(args)
        self.plugin_manager.call_method('parse_options', options)
        return args

    def initialize_plugins(self):
        self.plugin_manager.call_method('initialize')

    def get_collectors(self):
        return self.plugin_manager.get_collectors()

    def get_filters(self):
        return self.plugin_manager.get_filters()

    def get_coverage_filter(self):
        return self.plugin_manager.get_coverage_filter()

    def get_reporter_filter(self):
        return self.plugin_manager.get_reporter_filter()

    def get_reporters(self):
        return self.plugin_manager.get_reporters()

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
