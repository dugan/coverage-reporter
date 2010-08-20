"""
Library used to wrap options parsing to make it easier for plugin authors to add options for their plugin that are also available via config file.

A "real" solution would create option subclasses or some such, this is more of a toy for now.
"""
import optparse
from coverage_reporter.errors import ConfigError

class Option(object):
    """
    Option wrapper for coverage_reporter plugins.

    This class allows you define an option once, in a way that is shared between config files and optparse flags.

    Option takes all parameters that the normal parser.add_option command would, except "action", "dest", and the flag name(s).
    These are all inferred from the name and option_type.

    The option_type possibilites are currently:
        int
        string
        list
        boolean

    These are passed in as the second parameter to the Option class.
    """

    def __init__(self, name, option_type, default=None, **option_kwargs):
        self.name = name
        self.option_type = option_type

        self.default = default
        self.option_kwargs = option_kwargs

    def __repr__(self):
        return 'Option(%r, %r, default=%r, **%r)' % (self.name, 
                                                     self.option_type, 
                                                     self.default, 
                                                     self.option_kwargs,
                                                    )

    def add_option(self, parser):
        if self.option_type in ('int', 'string'):
            action = 'store'
        elif self.option_type in ('boolean',):
            action = 'store_true'
        elif self.option_type in ('list',):
            action = 'append'
        else:
            raise ConfigError('Invalid option type %r' % (self.option_type,))
        parser.add_option('--' + self.name.replace('_', '-'), dest=self.name, action=action, **self.option_kwargs)

    def parse_int(self, value):
        if value is not None:
            return int(value)

    def parse_boolean(self, value):
        if value is None:
            return value
        if isinstance(value, bool):
            return True
        if value.lower() in ('true', '1'):
            return True
        elif value.lower() in ('false', '0'):
            return False
        else:
            raise ConfigError('Invalid value for option %r: %r' % (self.name, value))

    def get(self, value, cfg=None):
        """
        Returns value for this option from either cfg object or optparse option list, preferring the option list.
        """
        if value is None and cfg:
            if self.option_type == 'list':
                value = cfg.get_list(self.name, None)
            else:
                value = cfg.get(self.name, None)

        if value is None:
            value = self.default
        else:
            parse_method = getattr(self, 'parse_%s' % (self.option_type), None)
            if parse_method:
                value = parse_method(value)
        return value

class OptionList(object):
    def __init__(self, options):
        self.options = tuple(options)

    def get_parser(self, ignore_errors=False):
        if ignore_errors:
            parser_class = _ImperviousOptionParser
        else:
            parser_class = optparse.OptionParser
        parser = parser_class()
        for option in self.options:
            option.add_option(parser)
        return parser

    def parse(self, args, ignore_errors=False, cfg=None):
        option_values, args =  self.get_parser(ignore_errors).parse_args(args)
        for option in self.options:
            cur_value = getattr(option_values, option.name)
            setattr(option_values, option.name, option.get(cur_value, cfg))
        return option_values, args

    def __add__(self, other):
        return OptionList(self.options + other.options)


# AttributeError only needed for Python 2.4
# ImpervOptionParser recipe From unittest2
_OPT_ERRS = (optparse.BadOptionError, optparse.OptionValueError, AttributeError)

class _ImperviousOptionParser(optparse.OptionParser):
    """
    """
    def error(self, msg):
        pass

    def exit(self, status=0, msg=None):
        pass

    print_usage = print_version = print_help = lambda self, file=None: None

    def _process_short_opts(self, rargs, values):
        try:
            optparse.OptionParser._process_short_opts(self, rargs, values)
        except _OPT_ERRS:
            pass

    def _process_long_opt(self, rargs, values):
        try:
            optparse.OptionParser._process_long_opt(self, rargs, values)
        except _OPT_ERRS:
            pass

