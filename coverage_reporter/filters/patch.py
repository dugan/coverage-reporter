import os
import sys

from coverage_reporter.plugins import Plugin, Option

class FilterByPatch(Plugin):
    name = 'patch'
    options = [ Option('patch', 'string', help='Filter coverage reports by patch at PATCH.  Can be file or stdin'),
                Option('patch_level', 'int', help='Patch level, as usually specified to patch command'), ]

    def filter(self, coverage_data):
        return filter_by_patch(coverage_data, self.patch, self.patch_level)

def filter_by_patch(coverage_data, patch_path, patch_level):
    if not os.path.exists(patch_path) and patch_path.lower() == 'stdin':
        patch_file = sys.stdin
    else:
        patch_file = open(patch_path)
    lines = _get_lines_from_patch(patch_file, patch_level)
    coverage_data &= lines
    return coverage_data

def _find_patch_file(path, level):
    path = os.path.sep.join(path.split(os.path.sep)[level:])
    if not os.path.exists(path):
        sys.stderr.write("Could not find file %r with patch level %s - maybe wrong patch level?  Specify -p\n" % (path, level))
        return None
    return os.path.realpath(path)

def _get_lines_from_patch(patch_file, patch_level):
    file_dict = {}
    new_file = None
    for line in patch_file:
        # strip 1 \n from the end.
        line = line[:-1]
        if line.startswith('+++'):
            # place marker - name of file
            # +++ <filename>
            new_file = line.split(None, 1)[1]
            new_file = line.split('\t', 1)[0]
            new_file = _find_patch_file(new_file, patch_level)
            if new_file:
                file_dict.setdefault(new_file, [])
        elif not new_file:
            continue
        elif line.startswith('---'):
            # --- <old filename>
            # place marker - name of old file
            continue
        elif line.startswith('@@'):
            # @@ -old_lineno,old_end +new_lineno,new_end @@ <extra info>
            # place marker - we want to start counting lines at new_lineno
            line = line[line.find('+')+1:]
            line = line[:line.find(',')]
            cur_line = int(line)
        elif line.startswith('+'):
            # added line
            file_dict[new_file].append(cur_line)
            cur_line += 1
        elif line.startswith('-'):
            # we can't cover removed lines.
            continue
        else:
            # unchanged line
            cur_line += 1
    return file_dict
