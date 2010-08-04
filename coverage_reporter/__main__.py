"""
Framework for parsing, munging and reporting coverage information.

Build to be extendable by plugins, if anyone should so desire.

Example commands

coverage-reporter --figleaf --annotate --exclude '.*/migrations/.*' <path> [<path>]
coverage-reporter --coverage --patch=stdin --annotate <path> 

TODO - config file parsing fixups.  Have command line way of enabling/disabling plugins.
"""
import sys

from coverage_reporter import config
from coverage_reporter import errors
from coverage_reporter import data

def main(argv):

    cfg = config.CoverageReporterConfig()
    cfg.load_plugins()

    path_list = cfg.parse_options(argv[1:])
    cfg.initialize_plugins()

    collectors = cfg.get_collectors()
    reporters = cfg.get_reporters()

    if not collectors:
        raise errors.CoverageReporterError('Please specify a source for coverage information')

    if not reporters:
        raise errors.CoverageReporterError('Please specify at least one form of reporting.')

    coverage_data = data.CoverageData()
    cover_filter = cfg.get_coverage_filter()
    for collector in cfg.get_collectors():
        new_coverage_data = collector.collect(path_list, cover_filter)
        coverage_data.merge(new_coverage_data)

    for filter in cfg.get_filters():
        coverage_data = filter.filter(coverage_data)
    print "reporting data"

    reporter_filter = cfg.get_reporter_filter()

    all_paths = coverage_data.get_paths() 
    matched_paths = list(reporter_filter.filter_all(all_paths, coverage_data))

    num_skipped_paths = len(all_paths) - len(matched_paths)
    if num_skipped_paths:
        print "Not reporting on %s files due to filters" % (num_skipped_paths,)

    for reporter in cfg.get_reporters():
        reporter.report(coverage_data, matched_paths)

if __name__ == '__main__':
    main(sys.argv)
