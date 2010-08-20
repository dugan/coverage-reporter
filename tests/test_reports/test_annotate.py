import os
import sys
import tempfile
from cStringIO import StringIO

from tests.testcase import CoverageReporterTestCase, with_tempdir

class AnnotateTest(CoverageReporterTestCase):

    @with_tempdir
    def test_annotate(self, tempdir):
        open('foo', 'w').write('a\n' * 20)
        try:
            open(tempdir + '/bar', 'w').write('b\n' * 10)
            data = self.create_coverage_data({'foo' : {'missing' : 10, 'total' : 20},
                                              tempdir + '/bar' : {'missing' : 0, 'total' : 10}})
            reporter = self.load_plugin('annotate')
            annotate_dir = tempdir + '/annotate'
            reporter.annotate_dir = annotate_dir
            reporter.report(data, data.get_paths())
        finally:
            os.remove('foo')
        foo_coverage = open(annotate_dir + '/foo,cover').read()
        bar_coverage = open(annotate_dir + '/private' + tempdir + '/bar,cover').read()
        self.assertEqual(foo_coverage, '  a\n' * 10 + '! a\n' * 10)
        self.assertEqual(bar_coverage, '  b\n' * 10)
