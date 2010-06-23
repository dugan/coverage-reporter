import ConfigParser
import optparse
import os
import shlex

class CoverageReporterConfig(object):
    def __init__(self):
        self.exclude = []
        self.coverage_type = None
        self.annotate = False
        self.summarize = False
        self.patch = None
        self.patch_level = 0
        self.minimum_missing = 0
        self.annotate_dir = 'annotate'

    def get_option_parser(self):
        parser = optparse.OptionParser()
        parser.add_option('--figleaf', dest='coverage_type', action='store_const', const='figleaf')
        parser.add_option('--coverage', dest='coverage_type', action='store_const', const='coverage')
        parser.add_option('--annotate', dest='annotate', action='store_true')
        parser.add_option('--exclude', dest='exclude', action='append')
        parser.add_option('--summarize', dest='summarize', action='store_true')
        parser.add_option('--patch', dest='patch', action='store')
        parser.add_option('--patch-level', '-p', dest='patch_level', action='store')
        from coverage_reporter.reports import summarize
        from coverage_reporter.reports import annotate
        summarize.add_options(parser)
        annotate.add_options(parser)
        return parser

    def parse_options(self, args):
        parser = self.get_option_parser()
        options, args = parser.parse_args(args)
        if options.coverage_type:
            self.coverage_type = options.coverage_type
        if options.patch:
            self.patch = options.patch
        if options.patch_level is not None:
            self.patch_level = options.patch_level
        if options.summarize:
            self.summarize = options.summarize
        if options.annotate:
            self.annotate = options.annotate
        if options.annotate_dir:
            self.annotate_dir = options.annotate_dir
        if options.minimum_missing is not None:
            self.minimum_missing = options.minimum_missing
        return args

    def read(self):
        cfg = ConfigParser.RawConfigParser()
        cfg.read(['/etc/coverage_reporter', os.path.expanduser('~/.coverage_reporter'), '.coverage_reporter'])
        for key, value in cfg.items('main'):
            if key == 'exclude':
                self.exclude = shlex.split(value)
            elif key == 'coverage_type':
                self.coverage_type = value
            elif key == 'minimum_missing':
                self.minimum_missing = int(value)
            elif key == 'annotate':
                self.annotate = value
            elif key == 'summarize':
                self.summarize = value


