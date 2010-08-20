import os

from coverage_reporter.options import Option, OptionList

DEFAULT_PLUGIN_DIRS = [ os.path.dirname(__file__) + '/collectors/',
                        os.path.dirname(__file__) + '/filters/',
                        os.path.dirname(__file__) + '/reports/',
                       ]

DEFAULT_PLUGINS = [ 'figleaf_collector',
                    'coverage_collector',
                    'patch',
                    'exclude',
                    'minimum',
                    'summarize',
                    'annotate',
                   ]


DEFAULT_CONFIG_PATHS = ['/etc/coverage_reporter', os.path.expanduser('~/.coverage_reporter'), '.coverage_reporter']


DEFAULT_OPTIONS = OptionList([ Option('skip_default_config', 'boolean'),
                               Option('config_file', 'list', default=[]),
                               Option('plugin_dir', 'list', default=[]),
                               Option('plugin', 'list', default=[]),
                               Option('disable_plugin', 'list', default=[]) ])


