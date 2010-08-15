from unittest2.events import Plugin, addOption
from unittest2.util import getSource

import os
import sys

try:
    import coverage
except ImportError, e:
    coverage = None
    coverageImportError = e


help_text1 = 'Enable coverage reporting'

class CoveragePlugin(Plugin):
    
    configSection = 'coverage'
    commandLineSwitch = ('C', 'coverage', help_text1)
    
    def __init__(self):
        self.configFile = self.config.get('config', '').strip() or True
        self.branch = self.config.as_bool('branch', default=None)
        self.timid = self.config.as_bool('timid', default=False)
        self.cover_pylib = self.config.as_bool('cover-pylib', default=False)
        self.excludeLines = self.config.as_list('exclude-lines', default=[])
        self.ignoreErrors = self.config.as_bool('ignore-errors', default=False)
    
    def register(self):
        if coverage is None:
            raise coverageImportError
        Plugin.register(self)
    
    def pluginsLoaded(self, event):
        args = dict(
            config_file=self.configFile,
            cover_pylib=self.cover_pylib,
            branch=self.branch,
            timid=self.timid,
        )
        self.cov = coverage.coverage(**args)
        self.cov.erase()

        self.cov.exclude('#pragma:? *[nN][oO] [cC][oO][vV][eE][rR]')
        for line in self.excludeLines:
            self.cov.exclude(line)
            
        self.cov.start()

    def stopTestRun(self, event):
        self.cov.stop()
        self.cov.save()
