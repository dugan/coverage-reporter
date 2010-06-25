"""
Command line interface for coverage-reporter.

Example commands

coverage-reporter --figleaf --annotate --exclude '.*/migrations/.*' <path> [<path>]
coverage-reporter --coverage --patch=stdin --annotate --exc
"""
import sys

from coverage_reporter import config
from coverage_reporter.reports import summarize
from coverage_reporter.reports import annotate
from coverage_reporter import filter



def main(argv):
    cfg = config.CoverageReporterConfig()
    cfg.read()
    path_list = cfg.parse_options(argv[1:])
    if not cfg.coverage_type:
        raise RuntimeError('Must specify one of --figleaf, --coverage')
    if not cfg.exclude:
        cfg.exclude = []

    if cfg.coverage_type == 'figleaf':
        from coverage_reporter.collectors.figleaf_collector import FigleafCollector as Collector
    elif cfg.coverage_type == 'coverage':
        from coverage_reporter.collectors.coverage_collector import CoveragePyCollector as Collector
    elif cfg.coverage_type == 'xml':
        from coverage_reporter.collectors.xml_collector import CorbertaCollector as Collector
    collector = Collector()
    coverage_data = collector.collect(path_list, cfg)

    if cfg.patch:
        coverage_data = filter.filter_by_patch(coverage_data, cfg.patch, int(cfg.patch_level))

    if cfg.annotate:
        annotate.annotate(coverage_data, cfg)
    if cfg.summarize:
        summarize.summarize(coverage_data, cfg)


if __name__ == '__main__':
    main(sys.argv)
