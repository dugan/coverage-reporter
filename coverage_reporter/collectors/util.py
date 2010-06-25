import os
import re

def get_exclude_regexp(exclude_path):
    exclude_re = exclude_path

    if exclude_re.endswith('$'):
        pass
    elif not exclude_re.endswith('/'):
        exclude_re += '$'
    else:
        exclude_re += '.*$'

    if exclude_re.startswith('^'):
        pass
    elif not exclude_re.startswith('/'):
        exclude_re = '^.*/' + exclude_re
    else:
        exclude_re = '^.*' + exclude_re
    return exclude_re


def filter_paths(path_list, covered_paths, exclude_paths, filter_fn):
    exclude_res = [ get_exclude_regexp(x) for x in exclude_paths ] 
    if not path_list:
        path_list = covered_paths
        for path in path_list:
            for exclude_re in exclude_res:
                if re.match(exclude_re, path):
                    break
            else:
                yield path
    else:
        for x in filter_specified_paths(path_list, covered_paths,
                                        exclude_res, filter_fn):
            yield x

def filter_specified_paths(path_list, covered_paths, exclude_res,
                           filter_fn):
    for path in path_list:
        if os.path.isdir(path):
            for x in _walk_one_dir(path, covered_paths, exclude_res, filter_fn):
                yield x
        else:
            yield os.path.realpath(path)

def _walk_one_dir(path, covered_paths, exclude_res, filter_fn):
    for root, dirs, files in os.walk(path):
        for file in files:
            full_path = os.path.realpath(os.path.join(root, file))
            for exclude_re in exclude_res:
                if re.match(exclude_re, full_path):
                    break
            else:
                # no exclude matches
                if path in covered_paths:
                    yield path
                elif filter_fn(full_path):
                    yield full_path
