import os

def add_options(parser):
    parser.add_option('--minimum-missing', dest='minimum_missing')


def summarize(coverage_data, options):
    curdir = os.path.realpath(os.getcwd())

    path_totals, final_totals = coverage_data.get_totals()
    new_path_totals = {}
    for path in path_totals:
        if path.startswith(curdir):
            new_path = path[len(curdir)+1:]
            path_totals[new_path] = path_totals.pop(path)


    if path_totals:
        longest_path = max([ len(x) for x in path_totals ])
    else:
        longest_path = 0
    title = '%-*s%8s%8s%8s' % (longest_path, 'Name', 'Stmts',
                                 'Exec', 'Cover')
    print title
    print '-' * len(title)
    paths = sorted(path_totals, key=lambda x: path_totals[x][0] - path_totals[x][1] )
    for path in paths:
        num_lines, num_covered, pct_covered = path_totals[path]
        if not num_lines:
            continue
        if options.minimum_missing is not None:
            if int(options.minimum_missing) > num_lines - num_covered:
                continue
        print '%*s%8s%8s%8.2f' % (longest_path, path, num_lines,
                                   num_covered, pct_covered)
    print '-' * len(title)
    total_lines, total_covered, total_pct = final_totals
    print '%-*s%8s%8s%8.2f' % (longest_path, 'TOTAL', total_lines,
                                 total_covered, total_pct)
