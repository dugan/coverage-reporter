import os
import sys

from tests.testcase import *

import coverage_reporter

class CoveragePyTest(CoverageReporterTestCase):

    def tearDown(self):
        super(CoveragePyTest, self).tearDown()
        if os.path.exists('.test_coverage'):
            os.remove('.test_coverage') 

    def cover_program(self, program_name):
        import coverage
        cur_trace = sys.gettrace()
        cov = coverage.coverage(data_file='.test_coverage')
        if os.path.exists('.test_coverage'):
            os.remove('.test_coverage')
        cov.start()
        self.run_program(program_name)
        cov.stop()
        cov.save()
        if hasattr(cur_trace, '__call__'):
            sys.settrace(cur_trace)
        elif hasattr(cur_trace, 'start'):
            cur_trace.start()

    def test_coverage(self):
        if sys.version_info[:2] < (2, 6):
            # no support for gettrace
            return
        self.cover_program('tests.data.prog1')
        collector = self.load_plugin('coverage_reporter.collectors.coverage_collector.CoveragePyCollector')
        collector.coverage_file = '.test_coverage'
        data = collector.collect(['tests/data/prog1.py'])
        full_path = os.path.realpath('tests/data/prog1.py')
        self.assertEqual(data.lines.keys(), [full_path])
        self.assertEqual(data.lines[full_path], [3, 4, 5, 6, 8, 9])
        self.assertEqual(data.covered[full_path], set([3, 4, 5, 8, 9])) # note - line 6 is not covered.
