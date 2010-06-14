import os
import types

from base import BaseCollector


class FigleafCollector(BaseCollector):
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

    def collect_covered_lines(self, options):
        import figleaf
        return figleaf.read_coverage('.figleaf')
