import os
import sys

from tests.testcase import *

import coverage_reporter
from coverage_reporter.plugins import Filter


class FigLeafTest(CoverageReporterTestCase):

    def tearDown(self):
        super(FigLeafTest, self).tearDown()
        if os.path.exists('.figleaf_test'):
            os.remove('.figleaf_test') 

    def cover_program(self, program_name):
        import figleaf
        cur_trace = sys.gettrace()
        sys.settrace(None)
        if os.path.exists('.figleaf_test'):
            os.remove('.figleaf_test')
        figleaf.start()
        self.run_program(program_name)
        figleaf.stop()
        figleaf.write_coverage('.figleaf_test', append=False)
        if hasattr(cur_trace, '__call__'):
            sys.settrace(cur_trace)
        elif hasattr(cur_trace, 'start'):
            cur_trace.start()

    def test_figleaf(self):
        self.cover_program('tests.data.prog1')
        collector = self.load_plugin('coverage_reporter.collectors.figleaf_collector.FigleafCollector')
        collector.figleaf_file = '.figleaf_test'
        data = collector.collect(['tests/data/prog1.py'])
        full_path = os.path.realpath('tests/data/prog1.py')
        self.assertEqual(data.lines.keys(), [full_path])
        self.assertEqual(data.lines[full_path], set([3,4,5,6,8,9]))
        self.assertEqual(data.covered[full_path], set([3,4,5,8,9])) # note - line 6 is not covered.
