import optparse
import sys

from coverage_reporter.errors import PluginError, ConfigError
from coverage_reporter.options import Option

__all__ = ['Plugin', 'Option']

class Plugin(object):
    """
    Required base class for plugins.  Provides some useful behaviors.

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

    def get_options(self):
        return self.options

    def enabled(self):
        if self.options:
            # we make the handy (documented) assumption that if the first option 
            # is set then this plugin is being used.
            return getattr(self, self.options[0].name, False)
        return True
