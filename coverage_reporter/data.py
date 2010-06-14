import os

class CoverageData(object):
    """
    In general, do not pickle this object; it's simpler and more
    straightforward to just pass the basic Python objects around
    (e.g. CoverageData.covered, a set, and CoverageData.sections, a
    dictionary of sets).
    """
    def __init__(self):
        self.covered = {}
        self.sections = {}
        self.lines = {}

    def get_covered(self, section_name=None):
        if not section_name:
            return dict(self.covered)
        else:
            d = CoverageData()
            d.update_coverage(self.covered)
            d.update_coverage(self.sections.get(section_name, {}))
            return d.get_covered()

    def get_section_lines(self):
        line_info = {}
        for path, lines in self.lines.iteritems():
            section_info = {}
            covered_lines = self.covered.get(path, [])
            line_info[path] = (lines, covered_lines, section_info)
            for section_name, section in self.sections.items():
                if path in section:
                    section_info[section_name] = section[path]
        return line_info

    def get_lines(self):
        line_info = {}
        for path, lines in self.lines.iteritems():
            covered_lines = self.covered.get(path, [])
            line_info[path] = (lines, covered_lines)
        return line_info

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
            report_info[path] = (num_lines, num_covered, percent_covered)
            total_covered += num_covered
            total_lines += num_lines
        if not total_lines:
            total_percent = 0.0
        else:
            total_percent = (total_covered * 100)/float(total_lines)
        return report_info, (total_lines, total_covered, total_percent)

    def _update_coverage(self, coverage1, coverage2):
        for filename, lines in coverage2.items():
            filename = os.path.realpath(os.path.abspath(filename))
            if filename in coverage1:
                coverage1[filename].update(lines)
            else:
                coverage1[filename] = set(lines)

    def update_coverage(self, coverage_dict, section_name=None):
        if not section_name:
            self._update_coverage(self.covered, coverage_dict)
        else:
            section_dict = self.sections.get(section_name, {})
            self._update_coverage(section_dict, coverage_dict)
            self.sections[section_name] = section_dict

    def update_sections(self, section_dict):
        for section_name, coverage_dict in section_dict.items():
            self.update_coverage(coverage_dict, section_name)

    def update_lines(self, line_dict):
        self.lines.update(line_dict)

    def merge(self, other):
        self.lines.update(other.lines)
        self.update_coverage(other.covered)
        self.update_sections(other.sections)

    def add_lines(self, path, lines):
        self.lines[path] = lines

    def filter_lines(self, line_dict):
        final_lines = {}
        for path, lines in line_dict.iteritems():
            final_lines[path] = self.lines.get(path, set()) & set(lines)
        self.lines = final_lines

    def add_coverage(self, path, lines, section_name=None):
        if not section_name:
            self.covered[path] = lines
        else:
            self.sections.get(section_name, {})[path] = line
