import imp
import sys

from coverage_reporter.errors import PluginError
from coverage_reporter.plugins import Plugin

class PluginManager(object):
    """
    Class that takes care of loading and managing plugins.
    """
    def __init__(self):
        self.plugins = []
        self.collectors = []
        self.coverage_filters = []
        self.filters = []
        self.reporter_filters = []
        self.reporters = []

    def add_plugin_options(self, parser):
        self._call_method('add_options', parser)

    def parse_plugin_options(self, options):
        self._call_method('parse_options', options)

    def initialize(self):
        self._call_method('initialize')

    def _call_method(self, method_name, *args, **kwargs):
        for plugin in self.plugins:
            method = getattr(plugin, method_name, None)
            if not method:
                continue
            method(*args, **kwargs)

    def load_plugins(self, cfg, plugin_dirs, plugin_names):
        classes = self.load_classes(plugin_dirs, plugin_names)
        for class_ in classes:
            self.validate_plugin(class_)
            plugin = class_(cfg)
            self.plugins.append(plugin)
            if hasattr(plugin, 'collect'):
                self.collectors.append(plugin)
            if hasattr(class_, 'filter'):
                self.filters.append(plugin)

            if hasattr(class_, 'report_path'):
                self.reporter_filters.append(plugin)
            if hasattr(class_, 'cover_path'):
                self.coverage_filters.append(plugin)
            if hasattr(class_, 'report'):
                self.reporters.append(plugin)
        return self.plugins

    def validate_plugin(self, plugin):
        required_attributes = ['enabled', 'name']
        for attr in required_attributes:
            if not hasattr(plugin, attr):
                raise PluginError('Plugin %r is missing %r attribute' % (plugin, attr))

    def get_collectors(self):
        return [ x for x in self.collectors if x.enabled() ]

    def get_filters(self):
        return [ x for x in self.filters if x.enabled() ]

    def get_coverage_filter(self):
        return Filter(*[ x.cover_path for x in self.coverage_filters if x.enabled() ])

    def get_reporter_filter(self):
        return Filter(*[ x.report_path for x in self.reporter_filters if x.enabled() ])

    def get_reporters(self):
        return [ x for x in self.reporters if x.enabled() ]

    def load_classes(self, plugin_dirs, plugin_names):
        needed_plugins = list(plugin_names)
        plugins = []
        for plugin_name in plugin_names:
            (file, pathname, description) = imp.find_module(plugin_name, list(reversed(plugin_dirs)))
            module = imp.load_module(plugin_name, file, pathname, description)
            plugins_in_module = [ x for x in module.__dict__.values() if (isinstance(x, type) 
                                                                          and issubclass(x, Plugin) 
                                                                          and sys.modules[x.__module__] is module) ]
            if not plugins_in_module:
                raise PluginError('No plugins found in module %r at %r' % (plugin_name, module.__file__))
            elif len(plugins_in_module) > 1:
                raise PluginError('Found two plugins in module %r at %r' % (plugin_name, module.__file__))
            plugins_in_module[0].name = plugin_name
            plugins.extend(plugins_in_module)
        return plugins

class Filter(object):
    """
    Tracks several functions, returning True only if all of the referenced 
    functions return True.
    """

    def __init__(self, *filter_fns):
        self.filter_fns = filter_fns

    def filter_all(self, iterable, *args, **kwargs):
        for item in iterable:
            for filter_fn in self.filter_fns:
                if not filter_fn(item, *args, **kwargs):
                    break
            else:
                # all filters passed for item.
                yield item

    def filter(self, *args, **kwargs):
        for filter in self.filter_fns:
            if not filter(*args, **kwargs):
                return False
        return True
