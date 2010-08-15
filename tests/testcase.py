import sys

import unittest2

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
