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

    if options.minimum_missing is not None:
        minimum = int(options.minimum_missing)
    else:
        minimum = 0
    paths = sorted(path_totals, key=lambda x: path_totals[x]['missing'])
    
    paths = [ x for x in paths if path_totals[x]['lines' ]]
    skipped_paths = len([ x for x in paths if path_totals[x]['missing'] < minimum ])
    if skipped_paths:
        print "Skipping %s files due to minimum missing of %s" % (skipped_paths, minimum,)

    paths = [ x for x in paths if path_totals[x]['missing'] >= minimum ]

    if path_totals:
        longest_path = max([ len(x) for x in path_totals ])
    else:
        longest_path = 0
    title = '%-*s%8s%8s%8s' % (longest_path, 'Name', 'Stmts',
                                 'Exec', 'Cover')

    print title
    print '-' * len(title)
    for path in paths:
        print '%*s%8s%8s%8.2f' % (longest_path, path, path_totals[path]['lines'],
                                   path_totals[path]['covered'], path_totals[path]['percent'])
    print '-' * len(title)
    total_lines, total_covered, total_pct = final_totals
    print '%-*s%8s%8s%8.2f' % (longest_path, 'TOTAL', total_lines,
                                 total_covered, total_pct)
