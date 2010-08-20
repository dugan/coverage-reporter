import sys
from cStringIO import StringIO

from tests.testcase import CoverageReporterTestCase

class SummarizeTest(CoverageReporterTestCase):

    def test_summarize(self):
        data = self.create_coverage_data({'foo' : {'missing' : 10, 'total' : 80},
                                        'bar' : {'missing' : 0, 'total' : 10},
                                        'long_name_foo_another_long_name' : {'missing' : 10, 'total' : 10}})
        reporter = self.load_plugin('summarize')
        orig_stdout = sys.stdout
        captured = StringIO()
        try:
            sys.stdout = captured
            reporter.report(data, data.get_paths())
        finally:
            sys.stdout = orig_stdout
        captured.seek(0)
        output = captured.read()
        self.assertEqual(output, EXPECTED_REPORT)

EXPECTED_REPORT = """\
Name                              Stmts    Exec    Miss   Cover
---------------------------------------------------------------
bar                                  10      10       0  100.00
foo                                  80      70      10   87.50
long_name_foo_another_long_name      10       0      10    0.00
---------------------------------------------------------------
TOTAL                               100      80      20   80.00
"""
