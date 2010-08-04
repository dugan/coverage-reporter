# Based off of figleaf's CoverageData object,
# Though currently doesn't have support for figleaf sections or
# coverage.py arcs.
import os

class CoverageData(object):
    """
    In general, do not pickle this object; it's simpler and more
    straightforward to just pass the basic Python objects around
    (e.g. CoverageData.covered, a set, and CoverageData.sections, a
    dictionary of sets).
    """
    def __init__(self, lines=None, covered=None):
        if lines is None:
            lines = {}
        if covered is None:
            covered = {}
        self.covered = covered
        self.lines = lines
        self.exclude = []

    def get_covered(self, section_name=None):
        if not section_name:
            return dict(self.covered)
        else:
            d = CoverageData()
            d.update_coverage(self.covered)
            return d.get_covered()

    def get_lines(self):
        line_info = {}
        for path, lines in self.lines.iteritems():
            covered_lines = self.covered.get(path, set())
            line_info[path] = (lines, covered_lines)
        return line_info
    
    def get_lines_for_path(self, path):
        return (self.lines.get(path, set()), self.covered.get(path, set()))

    def get_paths(self):
        return self.lines.keys()

    def get_totals(self):
        report_info = {}
        total_covered = 0
        total_lines = 0
        for path, lines in self.lines.iteritems():
            covered_lines = self.covered.get(path, set())
            covered_lines &= set(lines)
            num_lines = len(lines)
            num_covered = len(covered_lines)
            if num_lines:
                percent_covered = (num_covered * 100)/float(num_lines)
            else:
                percent_covered = 0.0
            report_info[path] = { 'lines' : num_lines, 
                                  'covered' : num_covered, 
                                  'percent' : percent_covered,
                                  'missing' : num_lines - num_covered }
            total_covered += num_covered
            total_lines += num_lines
        if not total_lines:
            total_percent = 0.0
        else:
            total_percent = (total_covered * 100)/float(total_lines)
        return report_info, (total_lines, total_covered, total_percent)

    def get_missing_lines_for_path(self, path):
        num_lines = len(self.lines.get(path, []))
        covered_lines = len(self.covered.get(path, []))
        return num_lines - covered_lines

    def _update_coverage(self, coverage1, coverage2):
        for filename, lines in coverage2.items():
            filename = os.path.realpath(os.path.abspath(filename))
            if filename in coverage1:
                coverage1[filename].update(lines)
            else:
                coverage1[filename] = set(lines)

    def update_coverage(self, coverage_dict):
        self._update_coverage(self.covered, coverage_dict)

    def update_lines(self, line_dict):
        self.lines.update(line_dict)

    def merge(self, other):
        self.lines.update(other.lines)
        self.update_coverage(other.covered)

    def __and__(self, other):
        if isinstance(other, CoverageData):
            coverage_dict = other.data
        else:
            coverage_dict = other

        final_lines = {}
        for path, lines in coverage_dict.iteritems():
            final_lines[path] = set(self.lines.get(path, set())) & set(lines)
        return CoverageData(lines=final_lines, covered=self.covered.copy())
