from tests.testcase import CoverageReporterTestCase

class MinimumTest(CoverageReporterTestCase):

    def test_minimum(self):
        data = self.create_coverage_data({'foo.py' : {'missing' : 20},
                                          'bar.py' : {'missing' : 10 }})
        filter = self.load_plugin('minimum')
        filter.minimum_missing = 15
        assert(filter.report_path('foo.py', data))
        assert(not filter.report_path('bar.py', data))
