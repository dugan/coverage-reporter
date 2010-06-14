from base import BaseCollector

class CoveragePyCollector(BaseCollector):
    def should_cover(self, path):
        return path.endswith('.py')

    def get_all_lines_from_path(self, path):
        from coverage.parser import CodeParser
        parser = CodeParser(filename=path)
        statements, excluded = parser.parse_source()
        return statements

    def collect_covered_lines(self, cfg):
       from coverage.data import CoverageData
       data = CoverageData()
       data.read_file('.coverage')
       return data.lines

