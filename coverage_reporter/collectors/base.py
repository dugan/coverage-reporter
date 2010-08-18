import os

from coverage_reporter import data
from coverage_reporter.plugins import Plugin

class BaseCollector(Plugin):
    """
    Base class for collector types.  Splits behavior into two sections:
        - collecting information about what lines were covered
        - collecting list of all possible lines that _could_ have been covered.

    """

    def collect(self, path_list, path_filter=None):
        coverage_data = data.CoverageData()
        covered_lines = self.collect_covered_lines()
        coverage_data.update_coverage(covered_lines)

        if not path_list:
            path_list = covered_lines.keys()

        path_list = _iter_full_paths(path_list)

        if path_filter:
            path_list = ( x for x in path_list if path_filter.filter(x) )
        path_list = ( x for x in path_list if self.should_cover(x) )

        all_lines = dict((path, self.get_all_lines_from_path(path)) for path in path_list)
        coverage_data.update_lines(all_lines)
        return coverage_data

    def should_cover(self, path):
        """
        Returns True if this coverage tool can handle covering this path.
        """
        raise NotImplementedError

    def collect_covered_lines(self):
        """
        Returns dictionary of { path : [ line, line ] } that describes every actually covered line.
        """
        raise NotImplementedError

    def get_all_lines_from_path(self, path):
        """
        Returns a list of every possible coverable line in <path>.
        """
        raise NotImplementedError




def _iter_full_paths(path_list):
    """
    Iterates over all paths that are in a directory and its subdirectory, returning 
    fully-specified paths.
    """
    for path in path_list:
        if not os.path.isdir(path):
            full_path = os.path.realpath(path)
            yield path
        else:
            for root, dirs, filenames in os.walk(path):
                for filename in filenames:
                    full_path = os.path.realpath(os.path.join(root, filename))
                    yield full_path        
