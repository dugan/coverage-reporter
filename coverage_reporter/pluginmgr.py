import imp
import itertools
import sys

from coverage_reporter.defaults import DEFAULT_OPTIONS
from coverage_reporter.errors import PluginError
from coverage_reporter.plugins import Plugin
from coverage_reporter.options import OptionList

HOOKS = ['collect', 'initialize', 'get_options', 'parse_options', 'filter', 'report_path', 'cover_path', 'report' ]


def load_plugins(plugin_dirs, plugin_names):
    plugins = []
    classes = _load_classes(plugin_dirs, plugin_names)
    for class_ in classes:
        _validate_plugin(class_)
        plugin = class_()
        plugins.append(plugin)
    return PluginList(plugins)

def initialize_plugins(plugins, args, cfg):
    """
    """
    option_list = plugins.get_options() + DEFAULT_OPTIONS
    options, path_list = option_list.parse(args)
    plugins.process_options(options, cfg)
    plugins.initialize()
    return path_list


def _validate_plugin(plugin):
    required_attributes = ['enabled', 'name']
    for attr in required_attributes:
        if not hasattr(plugin, attr):
            raise PluginError('Plugin %r is missing %r attribute' % (plugin, attr))

def _load_classes(plugin_dirs, plugin_names):
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
        plugins.append(plugins_in_module[0])
    return plugins


class PluginList(object):
    def __init__(self, plugins):
        self.plugins = plugins
        self.plugins_by_hook = {}
        for hook in HOOKS:
            self.plugins_by_hook[hook] = [ x for x in plugins if hasattr(x, hook) ]

    def get_options(self):
        return OptionList(itertools.chain(*[x.get_options() for x in self.plugins]))

    def process_options(self, options, cfg):
        for plugin in self.plugins:
            for option in plugin.get_options():
                value = option.get(getattr(options, option.name, None), cfg)
                setattr(plugin, option.name, value)

    def initialize(self):
        self._call_hook('initialize')

    def get_collectors(self):
        return self.get_by_hook('collect')

    def get_filters(self):
        return self.get_by_hook('filter')

    def get_coverage_filter(self):
        return Filter(*[ x.cover_path for x in self.get_by_hook('cover_path')])

    def get_reporter_filter(self):
        return Filter(*[ x.report_path for x in self.get_by_hook('report_path')])

    def get_reporters(self):
        return self.get_by_hook('report')

    def get_by_hook(self, hook):
        return [ x for x in self.plugins_by_hook[hook] if x.enabled() ]

    def _call_hook(self, method_name, *args, **kwargs):
        results = []
        for plugin in self.get_by_hook(method_name):
            rv = getattr(plugin, method_name)(*args, **kwargs)
            results.append(rv)
        return results

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
