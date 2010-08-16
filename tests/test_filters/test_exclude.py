from tests.testcase import CoverageReporterTestCase

class ExcludeTest(CoverageReporterTestCase):

    def test_exclude_filter(self):
        excludes = [ '/2\.py', 
                     '3\.p', 
                     'dir/',
                     '^.*/whole_path$',
                     '/another_file']
        # True == excluded
        paths = {'2.py' : True,
                 '3.py' : False,
                 'somedir/blah' : False,
                 'dir/blah' : True,
                 'another_file' : True,
                 'whole_path' : True,
                 'whole_path2' : False}
        filter = self.load_plugin('coverage_reporter.filters.exclude.ExcludeFilter')
        filter.exclude = excludes
        filter.initialize()
        for path, matched in paths.items():
            path = '/some/place/' + path
            if matched:
                assert not filter.cover_path(path), "%r was not excluded when we expected it" % path
            else:
                assert filter.cover_path(path), "%r was excluded when we didn't expect it" % path
