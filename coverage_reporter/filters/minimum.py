from coverage_reporter.plugins import Plugin, Option

class MinimumMissingFilter(Plugin):
    """
    Simple filter that allows you to only display files that are missing large amounts of coverage.
    """
    name = 'missing'
    options = [ Option('minimum_missing', 'int', help='Specifies minimum number of missing coverage lines needed to report on file') ]

    def report_path(self, path, coverage_data):
        if self.minimum_missing is None:
            return True
        return coverage_data.get_missing_lines_for_path(path) >= self.minimum_missing
