import os

def add_options(parser):
    parser.add_option('--annotate-dir', dest='annotate_dir', action='store', default='annotate')

def annotate(coverage_data, options):
    annotate_dir = options.annotate_dir
    if not os.path.exists(annotate_dir):
        os.makedirs(annotate_dir)
    curdir = os.getcwd()
    for path, lines in coverage_data.get_lines().iteritems():
        (total_lines, covered_lines) = lines
        if options.minimum_missing is not None:
            if int(options.minimum_missing) > (len(total_lines) - len(lines)):
                continue
        if path.startswith(curdir):
            annotate_path = annotate_dir + path[len(curdir):]
        else:
            annotate_path = annotate_dir + path
        annotate_path += ',cover'
        source = open(path, 'r')
        dir = os.path.dirname(annotate_path)
        if not os.path.exists(dir):
            os.makedirs(dir)
        dest = open(annotate_path, 'w')
        try:
            annotate_file(source, dest, total_lines, covered_lines)
        finally:
            source.close()
            dest.close()

def annotate_file(source, dest, total_lines, covered_lines):
    for idx, line in enumerate(source):
        lineno = idx + 1
        if lineno not in total_lines:
            if line.strip():
                mark = '  '
            else:
                mark = '  '
        elif lineno not in covered_lines:
            mark = '! '
        else:
            mark = '  '
        dest.write(mark)
        dest.write(line)
