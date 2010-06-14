import os
import re

def filter_paths(path_list, covered_paths, exclude_paths, filter_fn):
    if not path_list:
        path_list = covered_paths
        for path in path_list:
            for exclude_re in exclude_paths:
                if re.match(exclude_re, path):
                    break
            else:
                yield path
    else:
        for x in filter_specified_paths(path_list, covered_paths,
                                        exclude_paths, filter_fn):
            yield x

def filter_specified_paths(path_list, covered_paths, exclude_paths,
                           filter_fn):
    for path in path_list:
        if os.path.isdir(path):
            for x in _walk_one_dir(path, covered_paths, exclude_paths, filter_fn):
                yield x
        else:
            yield os.path.realpath(path)

def _walk_one_dir(path, covered_paths, exclude_paths, filter_fn):
    for root, dirs, files in os.walk(path):
        for file in files:
            full_path = os.path.realpath(os.path.join(root, file))
            for exclude_re in exclude_paths:
                if re.match(exclude_re, full_path):
                    break
            else:
                # no exclude matches
                if path in covered_paths:
                    yield path
                elif filter_fn(full_path):
                    yield full_path
