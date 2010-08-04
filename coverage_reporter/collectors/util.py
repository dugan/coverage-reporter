import os
import re


def filter_paths(path_list, covered_paths, path_filter):
    if not path_list:
        # No paths were specified by the user, so we only report on covered files.
        path_list = covered_paths
        for path in path_list:
            if path_filter.filter(path):
                yield path
    else:
        for x in filter_specified_paths(path_list, covered_paths, path_filter):
            yield x

def filter_specified_paths(path_list, covered_paths, path_filter):
    """
    These paths were specified at the command line.  Any specifically listed file automatically gets a pass, overriding filters.  
    Any listed directories are recursed and their files are filtered as normal.
    """
    for specified_path in path_list:
        if os.path.isdir(specified_path):
            for root, dirs, filenames in os.walk(specified_path):
                for filename in filenames:
                    full_path = os.path.realpath(os.path.join(root, filename))
                    if path_filter.filter(full_path):
                        yield full_path        
        else:
            yield os.path.realpath(specified_path)
