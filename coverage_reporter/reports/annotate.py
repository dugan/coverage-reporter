import os
import shutil

def add_options(parser):
    parser.add_option('--annotate-dir', dest='annotate_dir', action='store', default='annotate')

def annotate(coverage_data, options):
    annotate_dir = options.annotate_dir
    if os.path.exists(annotate_dir):
        for root, dirs, files in os.walk(annotate_dir, topdown=False):
            dirs = [ x for x in dirs if os.path.exists(os.path.join(root, x)) ]
            to_remove = [ x for x in files if x.endswith(',cover') ]
            to_keep = [ x for x in files if not x in to_remove ]
            for x in to_remove:
                os.remove(os.path.join(root, x))
            if not (dirs or to_keep):
                os.rmdir(root)
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
