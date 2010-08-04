import os

from coverage_reporter.plugins import Plugin, Option

class SummarizeReporter(Plugin):
    name = 'summarize'

    options = [Option('summarize', 'boolean', help="Display summary of coverage information to screen")]

    def report(self, coverage_data, path_list):
        curdir = os.path.realpath(os.getcwd())

        path_totals, final_totals = coverage_data.get_totals()

        new_paths = []
        for path in path_list:
            if path.startswith(curdir):
                new_path = path[len(curdir)+1:]
                path_totals[new_path] = path_totals[path]
                new_paths.append(new_path)
            else:
                new_paths.append(path)

        paths = sorted(x for x in new_paths if path_totals[x]['lines' ])

        if paths:
            longest_path = max([ len(x) for x in paths ])
        else:
            longest_path = 0
        title = '%-*s%8s%8s%8s%8s' % (longest_path, 'Name', 'Stmts',
                                     'Exec', 'Miss', 'Cover')

        print title
        print '-' * len(title)
        for path in paths:
            print '%-*s%8s%8s%8s%8.2f' % (longest_path, path, path_totals[path]['lines'],
                                       path_totals[path]['covered'], path_totals[path]['missing'], path_totals[path]['percent'])
        print '-' * len(title)
        total_lines, total_covered, total_pct = final_totals
        total_missed = total_lines - total_covered
        print '%-*s%8s%8s%8s%8.2f' % (longest_path, 'TOTAL', total_lines,
                                     total_covered, total_missed, total_pct)
