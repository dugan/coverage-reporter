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

from coverage_reporter import defaults
from coverage_reporter.errors import ConfigError

def get_config(args):
    """
    Method to get the correct configuration file for a set of command line arguments.
    Takes into account --config-file, --plugins, --
    """
    options, _ = defaults.DEFAULT_OPTIONS.parse(args, ignore_errors=True)
    read_config = not options.skip_default_config
    cfg = CoverageReporterConfig(read_config)
    for path in options.config_file:
        cfg.read(path)
    cfg.plugin_dirs.extend(options.plugin_dir)
    cfg.plugins.extend(options.plugin)
    return cfg

class CoverageReporterConfig(object):
    def __init__(self, read_defaults=True):
        self.cfg = ConfigParser.RawConfigParser()
        self.plugins = defaults.DEFAULT_PLUGINS
        self.plugin_dirs = defaults.DEFAULT_PLUGIN_DIRS
        if read_defaults:
            self.read(*defaults.DEFAULT_CONFIG_PATHS)

    def read(self, *path_list):
        for path in path_list:
            self.cfg.read(path_list)
        section = self.get_section('plugins')
        self.plugins += section.get_list('plugins', [])
        self.plugin_dirs += section.get_list('plugin_dirs', [])

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

