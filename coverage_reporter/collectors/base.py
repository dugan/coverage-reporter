from coverage_reporter.collectors import util
from coverage_reporter import data

class BaseCollector(object):
    def collect(self, path_list, options):
        coverage_data = data.CoverageData()
        covered_lines = self.collect_covered_lines(options)
        coverage_data.update_coverage(covered_lines)
        all_lines = self.collect_all_lines(path_list, covered_lines, options)
        coverage_data.update_lines(all_lines)
        return coverage_data

    def should_cover(self, path):
        return True

    def collect_all_lines(self, path_list, covered_lines, options):
        """
        Returns dictionary of { path : [ line, line ] } that describes every possible coverable line.
        """
        line_dict = {}
        for path in util.filter_paths(path_list, covered_lines, options.exclude,
                                      filter_fn=self.should_cover):
            line_dict[path] = self.get_all_lines_from_path(path)
        return line_dict

    def get_total_lines_from_path(self, path):
        return []

    def collect_covered_lines(self, options):
        return {}
