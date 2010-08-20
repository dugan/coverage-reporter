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

from coverage_reporter.config import get_config
from coverage_reporter import errors
from coverage_reporter.pluginmgr import load_plugins, initialize_plugins
from coverage_reporter.data import CoverageData

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
    plugins = load_plugins(cfg.plugin_dirs, cfg.plugins)
    path_list = initialize_plugins(plugins, argv, cfg.get_section('coverage_reporter'))
    validate_active_plugins(plugins)

    data = collect(plugins.get_collectors(), path_list, plugins.get_coverage_filter())
    data = filter_coverage(data, plugins.get_filters())
    report_paths = filter_reporting_paths(data.get_paths(), data, plugins.get_reporter_filter())
    report(data, plugins.get_reporters(), report_paths)
    
if __name__ == '__main__':
    main(sys.argv)
