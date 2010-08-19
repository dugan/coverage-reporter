"""
Framework for parsing, munging and reporting coverage information.

Build to be extendable by plugins, if anyone should so desire.

Example commands

coverage-reporter --figleaf --annotate --exclude '.*/migrations/.*' <path> [<path>]
coverage-reporter --coverage --patch=stdin --annotate <path> 

TODO - config file parsing fixups.  Have command line way of enabling/disabling plugins.
"""
import optparse
import sys

from coverage_reporter import config
from coverage_reporter import errors
from coverage_reporter.pluginmgr import PluginManager
from coverage_reporter.data import CoverageData

# AttributeError only needed for Python 2.4
_OPT_ERRS = (optparse.BadOptionError, optparse.OptionValueError, AttributeError)

class _ImperviousOptionParser(optparse.OptionParser):
    """
    # recipe From unittest2
    """
    def error(self, msg):
        pass
    def exit(self, status=0, msg=None):
        pass

    print_usage = print_version = print_help = lambda self, file=None: None

    def _process_short_opts(self, rargs, values):
        try:
            optparse.OptionParser._process_short_opts(self, rargs, values)
        except _OPT_ERRS:
            pass

    def _process_long_opt(self, rargs, values):
        try:
            optparse.OptionParser._process_long_opt(self, rargs, values)
        except _OPT_ERRS:
            pass

def get_config(args):
    parser = _ImperviousOptionParser()
    add_config_options(parser)
    options, _ = parser.parse_args(args[:1])
    read_config = not options.skip_default_config
    cfg = config.CoverageReporterConfig(read_config)
    for path in options.config_files:
        cfg.read(path)
    cfg.plugin_dirs.extend(options.plugin_dirs)
    cfg.plugins.extend(options.plugins)
    return cfg

def setup_plugins(plugins, args):
    parser = optparse.OptionParser()
    add_config_options(parser)
    plugins.add_plugin_options(parser)
    options, path_list = parser.parse_args(args[1:])
    path_list = plugins.parse_plugin_options(options)
    plugins.initialize()
    return path_list

def add_config_options(parser):
    parser.add_option('--skip-default-config', dest='skip_default_config', action='store_true')
    parser.add_option('--config-file', dest='config_files', action='append', default=[])
    parser.add_option('--plugin-dir', dest='plugin_dirs', action='append', default=[])
    parser.add_option('--plugin', dest='plugins', action='append', default=[])
    parser.add_option('--disable-plugin', dest='disabled_plugins', action='append', default=[])

def collect(collectors, path_list, cover_filter):
    data = CoverageData()
    for collector in collectors:
        new_data = collector.collect(path_list, cover_filter)
        data.merge(new_data)
    return data

def filter_collection_paths(path_list, filter=None):
    path_list = iter_full_paths(path_list)
    if filter is not None:
        path_list = (x for x in path_list if filter.filter(x))
    return path_list

def filter_coverage(data, filters):
    for filter in filters:
        data = filter.filter(data)
    return data

def filter_reporting_paths(paths, data, reporter_filter):
    matched_paths = list(reporter_filter.filter_all(paths, data))
    num_skipped_paths = len(paths) - len(matched_paths)
    if num_skipped_paths:
        print "Not reporting on %s files due to filters" % (num_skipped_paths,)
    return matched_paths

def report(data, reporters, paths):
    for reporter in reporters:
        reporter.report(data, paths)

def validate_active_plugins(plugins):
    if not plugins.get_reporters():
        raise errors.CoverageReporterError('Please specify at least one form of reporting.')
    if not plugins.get_collectors():
        raise errors.CoverageReporterError('Please specify a source for coverage information')

def main(argv):
    cfg = get_config(argv)
    plugins = PluginManager()
    plugins.load_plugins(cfg.get_section('coverage_reporter'), cfg.plugin_dirs,
                         cfg.plugins)
    path_list = setup_plugins(plugins, argv)
    plugins.initialize()
    validate_active_plugins(plugins)

    data = collect(plugins.get_collectors(), path_list, plugins.get_coverage_filter())
    data = filter_coverage(data, plugins.get_filters())
    report_paths = filter_reporting_paths(data.get_paths(), data, plugins.get_reporter_filter())
    report(data, plugins.get_reporters(), report_paths)
    
if __name__ == '__main__':
    main(sys.argv)
