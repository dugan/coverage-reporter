from coverage_reporter.collectors.base import BaseCollector
from coverage_reporter.plugins import Option

class CoveragePyCollector(BaseCollector):
    """
    Coverage collector for the coverage.py tool.
    """
    name = 'coverage'

    options = [ Option('coverage', 'boolean', 
                       help='Enables loading of coverage information from coverage.py') ]

    def should_cover(self, path):
        return path.endswith('.py')

    def get_all_lines_from_path(self, path):
        from coverage.parser import CodeParser
        parser = CodeParser(filename=path)
        statements, excluded = parser.parse_source()
        return statements

    def collect_covered_lines(self):
       from coverage.data import CoverageData
       data = CoverageData()
       data.read_file('.coverage')
       return data.lines
