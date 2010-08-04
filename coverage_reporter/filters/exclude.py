import re

from coverage_reporter.plugins import Plugin, Option

class ExcludeFilter(Plugin):
    """
    Exclude filter.  Filters like foo.py match files named foo.py.  Filters like bar/ match everything under directory bar.
    Full filters should specify ^ and $.
    """
    name = 'exclude'
    options = [ Option('exclude', 'list', help='Exclude paths from coverage reporting.  Can be specified more than once, takes partial regexps.') ]

    def initialize(self):
        self.exclude_res = [ get_exclude_regexp(x) for x in self.exclude ]

    def cover_path(self, path):
        for exclude_re in self.exclude_res:
            if re.match(exclude_re, path):
                return False
        return True

def get_exclude_regexp(exclude_path):
    exclude_re = exclude_path

    if exclude_re.endswith('$'):
        pass
    elif exclude_re.endswith('/'):
        # re's that end with a / are assumed to mean everything in that directory.
        exclude_re += '.*$'
    else:
        exclude_re += '$'

    if exclude_re.startswith('^'):
        pass
    elif exclude_re.startswith('/'):
        exclude_re = '^.*' + exclude_re
    else:
        exclude_re = '^.*/' + exclude_re
    return exclude_re
