from coverage_reporter.collectors import util
from coverage_reporter import data
from coverage_reporter.plugins import Plugin

class BaseCollector(Plugin):
    """
    Base class for collector types.  Splits behavior into two sections:
        - collecting information about what lines were covered
        - collecting list of all possible lines that _could_ have been covered.

    """

    def collect(self, path_list, path_filter):
        coverage_data = data.CoverageData()
        covered_lines = self.collect_covered_lines()
        coverage_data.update_coverage(covered_lines)
        all_lines = self.collect_all_lines(path_list, covered_lines, path_filter)
        coverage_data.update_lines(all_lines)
        return coverage_data

    def should_cover(self, path):
        """
        Returns True if this coverage tool can handle covering this path.
        """
        return False

    def collect_covered_lines(self):
        """
        Returns dictionary of { path : [ line, line ] } that describes every actually covered line.
        """
        return {}

    def collect_all_lines(self, path_list, covered_lines, path_filter):
        """
        Returns dictionary of { path : [ line, line ] } that describes every possible coverable line.
        """
        line_dict = {}
        paths = list(util.filter_paths(path_list, covered_lines, path_filter))
        for path in util.filter_paths(path_list, covered_lines, path_filter):
            if self.should_cover(path):
                line_dict[path] = self.get_all_lines_from_path(path)
        return line_dict

    def get_total_lines_from_path(self, path):
        """
        Returns a list of every possible coverable line in <path>.
        """
        return []
