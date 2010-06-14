"""
Command line interface for coverage-reporter.

Example commands

coverage-reporter --figleaf --annotate --exclude '.*/migrations/.*' <path> [<path>]
coverage-reporter --coverage --patch=stdin --annotate --exc
"""
import sys
import optparse

from coverage_reporter.reports import summarize
from coverage_reporter.reports import annotate

def get_option_parser():
    parser = optparse.OptionParser()
    parser.add_option('--figleaf', dest='coverage_type', action='store_const', const='figleaf')
    parser.add_option('--coverage', dest='coverage_type', action='store_const', const='coverage')
    parser.add_option('--annotate', dest='annotate', action='store_true')
    parser.add_option('--exclude', dest='exclude', action='append')
    parser.add_option('--summarize', dest='summarize', action='store_true')
    summarize.add_options(parser)
    annotate.add_options(parser)
    return parser

                    

def main(argv):
    parser = get_option_parser()
    options, path_list = parser.parse_args(argv[1:])
    if not options.coverage_type:
        raise RuntimeError('Must specify one of --figleaf, --coverage')
    if options.coverage_type == 'figleaf':
        from coverage_reporter.collectors.figleaf_collector import FigleafCollector as Collector
    elif options.coverage_type == 'coverage':
        from coverage_reporter.collectors.coverage_collector import CoveragePyCollector as Collector
    elif options.coverage_type == 'xml':
        from coverage_reporter.collectors.xml_collector import CorbertaCollector as Collector
    collector = Collector()
    coverage_data = collector.collect(path_list, options)

    if options.annotate:
        annotate.annotate(coverage_data, options)
    if options.summarize:
        summarize.summarize(coverage_data, options)


if __name__ == '__main__':
    main(sys.argv)
