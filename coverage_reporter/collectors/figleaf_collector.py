import os
import types

from coverage_reporter.collectors.base import BaseCollector
from coverage_reporter.plugins import Option


class FigleafCollector(BaseCollector):
    """
    Coverage collector for figleaf's coverage info.
    """
    name = 'figleaf'
    options = [Option('figleaf', 'boolean', 
                      help='Enables loading of coverage information from figleaf') ]

    def should_cover(self, path):
        return path.endswith('.py')
    
    def get_all_lines_from_path(self, path):
        if '<doctest' in path:
            return set()
        if not os.path.exists(path):
            return set()
        import figleaf
        try:
            return figleaf.get_lines(open(path))
        except:
            return set()

    def collect_covered_lines(self):
        import figleaf
        return figleaf.read_coverage('.figleaf')
