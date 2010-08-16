import sys

import unittest2

from coverage_reporter.data import CoverageData
from coverage_reporter.config import CoverageReporterConfig

class CoverageReporterTestCase(unittest2.TestCase):

    def setUp(self):
        super(CoverageReporterTestCase, self).setUp()
        self.cfg = CoverageReporterConfig(read_defaults=False)

    def run_program(self, program_name):
        if program_name in sys.modules:
            reload(sys.modules[program_name])
        else:
            __import__(program_name)
        module = sys.modules[program_name]
        return getattr(module, 'main')()

    def load_plugin(self, plugin_name):
        return self.load_plugins([plugin_name])[0]

    def load_plugins(self, plugin_list):
        return self.cfg.load_plugins(plugin_list)

    def create_coverage_data(self, path_dict):
        data = CoverageData()
        lines = {}
        covered = {}
        for path, path_info in path_dict.items():
            missing = path_info.get('missing', 10)
            total = path_info.get('total', missing + 30)
            lines[path] = range(1, total + 1)
            covered[path] = range(1, total - missing + 1)
        data.update_lines(lines)
        data.update_coverage(covered)
        return data
