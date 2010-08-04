import os
import shutil

from coverage_reporter.plugins import Plugin, Option

class AnnotateReporter(Plugin):
    name = 'annotate'

    options = [Option('annotate', 'boolean', help="Write coverage annotations to disk, as place specified by --annotate-dir"),
               Option('annotate_dir', 'string', default='annotate', help="annotation directory, default 'annotate'")]

    def remove_old_annotations(self, annotate_dir):
        if os.path.exists(annotate_dir):
            for root, dirs, files in os.walk(annotate_dir, topdown=False):
                dirs = [ x for x in dirs if os.path.exists(os.path.join(root, x)) ]
                to_remove = [ x for x in files if x.endswith(',cover') ]
                to_keep = [ x for x in files if not x in to_remove ]
                for x in to_remove:
                    os.remove(os.path.join(root, x))
                if not (dirs or to_keep):
                    os.rmdir(root)

    def report(self, coverage_data, path_list):
        annotate_dir = self.annotate_dir
        self.remove_old_annotations(annotate_dir)
        if not os.path.exists(annotate_dir):
            os.makedirs(annotate_dir)

        curdir = os.getcwd()
        coverage = coverage_data.get_lines()
        for path in path_list:
            (total_lines, covered_lines) = coverage_data.get_lines_for_path(path)
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
                self.annotate_file(source, dest, total_lines, covered_lines)
            finally:
                source.close()
                dest.close()

    def annotate_file(self, source, dest, total_lines, covered_lines):
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
