from coverage_reporter.errors import PluginError, ConfigError

__all__ = ['Plugin', 'Option']

class Plugin(object):
    """
    (Optional) Base class for plugins.  Provides some useful behaviors.

    Among the most useful is options support.  A plugin can specify a number of options
    in the options class variable.  The options should be instances of coverage_reporter.plugins.Option.
    All such options will get their value from configuration files (if present), but their value will
    be overridden by anything specified by a command-line flag.

    The option value will be stored in an attribute of the plugin of the same name as the option.

    By default, a plugin will be assumed to be enabled if the value of the first option passed in is
    set.  This can be overridden by defining the "enabled" method.

    Plugins can currently provide 5 hooks:
        * collect(path_list, path_filter) - returns a data.CoverageData object with active lines and covered lines.
        * filter(coverage_data) - removes items from a data.CoverageData object.
        * cover_path(path) - returns True if this line should be considered for coverage
        * report_path(path, coverage_data) - returns True if this line should be reported on
        * report(coverage_data, path_list) - performs some sort of operation on the final reporting data.

    Examples of all types are shown in collectors, filters, and reporters subdirs.
    """
    options = []

    def __init__(self, cfg):
        """
        Used for actions performed upon loading but before knowing whether the plugin is enabled or not. 
        """
        self.cfg = cfg

    def add_options(self, parser):
        for option in self.options:
            option.add_option(parser)

    def parse_options(self, options):
        for option in self.options:
            value = option.get_value(options, self.cfg)
            setattr(self, option.name, value)

    def enabled(self):
        if self.options:
            # we make the handy (documented) assumption that if the first option 
            # is set then this plugin is being used.
            return getattr(self, self.options[0].name, False)
        return True

    def initialize(self):
        pass


class Option(object):
    """
    Option wrapper for coverage_reporter plugins.

    This class allows you define an option once, in a way that is shared between config files and optparse flags.

    Option takes all parameters that the normal parser.add_option command would, except "action", "dest", and the flag name(s).
    These are all inferred from the name and option_type.

    The option_type possibilites are currently:
        int
        string
        list
        boolean

    These are passed in as the second parameter to the Option class.
    """

    def __init__(self, name, option_type, default=None, **option_kwargs):
        self.name = name
        self.option_type = option_type
        self.default = default
        self.option_kwargs = option_kwargs

    def add_option(self, parser):
        if self.option_type in ('int', 'string'):
            action = 'store'
        elif self.option_type in ('boolean',):
            action = 'store_true'
        elif self.option_type in ('list',):
            action = 'append'
        else:
            raise ConfigError('Invalid option type %r' % (self.option_type,))
        parser.add_option('--' + self.name.replace('_', '-'), dest=self.name, action=action, **self.option_kwargs)

    def get_value(self, options, cfg):
        """
        Returns value for this option from either cfg object or optparse option list, preferring the option list.
        """
        if self.option_type in ('string', 'int', 'boolean'):
            value = getattr(options, self.name, None)
            if value is None:
                value = cfg.get(self.name, None)
            if value is None:
                value = self.default
            if self.option_type == 'int' and value is not None:
                value = int(value)
            elif self.option_type == 'boolean' and value is not None:
                if value.lower() in ('true', '1'):
                    return True
                elif value.lower() in ('false', '0'):
                    return False
                else:
                    raise ConfigError('Invalid value for option %r: %r' % (self.name, value))
            return value
        elif self.option_type == 'list':
            value = getattr(options, self.name, None)
            if value is None:
                value = cfg.get_list(self.name, [])
            return value

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

    def call_method(self, method_name, *args, **kwargs):
        for plugin in self.plugins:
            method = getattr(plugin, method_name, None)
            if not method:
                continue
            method(*args, **kwargs)

    def load_plugins(self, cfg_factory, class_strings):
        classes = self.load_classes(class_strings)
        for class_ in classes:
            self.validate_plugin(class_)
            plugin = class_(cfg_factory(class_.name))
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

    def load_classes(self, class_strings):
        classes = []
        for class_string in class_strings:
            module_path, class_name = class_string.rsplit('.', 1)
            module = __import__(module_path, fromlist=True)
            class_ = getattr(module, class_name)
            classes.append(class_)
        return classes


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
