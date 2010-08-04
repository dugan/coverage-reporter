
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    
Version = "0.01"

setup(name = "coverage-reporter",
      version = Version,
      description = "Coverage reporting tool",
      long_description="Allows more complicated reporting of information from figleaf and other coverage tools",
      author = "David Christian",
      author_email = "david.chrsitian@gmail.com",
      url = "http://github.org/dugan/coverage-reporter/",
      packages = [ 'coverage_reporter', 'coverage_reporter.filters', 'coverage_reporter.collectors', 'coverage_reporter.reports' ],
      license = 'BSD',
      scripts = ['scripts/coverage-reporter'],
      platforms = 'Posix; MacOS X; Windows',
      classifiers = [ 'Intended Audience :: Developers',
                      'License :: OSI Approved :: BSD License',
                      'Operating System :: OS Independent',
                      'Topic :: Development',
                      ],
      )
