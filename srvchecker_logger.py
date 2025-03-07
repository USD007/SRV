"""
Author : mmi6kor
This will create a basic function for logging mechanism
"""
import logging
from errorcodes import dbgmsg

# TODO - shutdown logger

MESSAGE = 70
LOGGER_ERROR_LEVELS = {
    0: 50,
    1: 40,
    2: 30,
    3: 20,
    4: 10
}


class MyLogger(logging.getLoggerClass()):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)
        logging.addLevelName(MESSAGE, "MESSAGE")

    def message(self, msg, *args, **kwargs):
        if self.isEnabledFor(MESSAGE):
            self._log(MESSAGE, msg, args, **kwargs)


class MyFormatter(logging.Formatter):

    FORMATS = {
        logging.CRITICAL: "%(asctime)s: {level:<7} - %(msg)s".format(level='ERROR'),  # FATAL logging changed to ERROR for users
        logging.WARNING: "%(asctime)s: {level:<7} - %(msg)s".format(level='WARNING'),
        logging.DEBUG: "%(asctime)s: {level:<7} -  %(filename)s - %(module)s: %(lineno)d: %(msg)s".format(level='DEBUG'),
        logging.ERROR: "%(asctime)s: {level:<7} - %(msg)s".format(level='ERROR'),
        logging.INFO: "%(asctime)s: {level:<7} - %(msg)s".format(level='INFO')
    }

    def __init__(self, fmt="%(asctime)s: %(levelname)s: %(msg)s", datefmt='%d-%b-%y %H:%M:%S'):
        logging.Formatter.__init__(self, fmt, datefmt, style='%')

    def format(self, record):
        format_orig = self._style._fmt

        # Replace the original format with one customized by logging level
        self._style._fmt = MyFormatter.FORMATS.get(record.levelno)
        result = logging.Formatter.format(self, record)
        self._style._fmt = format_orig

        return result


class LoggerDisp:

    def __init__(self, output_path):
        self.output_path = output_path
        filename = 'srvchecker.log'
        import os.path
        self.logger = logging.getLogger('MyLogger')
        self.logger.setLevel(logging.DEBUG)
        # create formatter and add it to the handlers
        self.fmt = MyFormatter()
        self.file_handler = logging.FileHandler(os.path.join(self.output_path, filename), 'w')
        self.file_handler.setLevel(logging.DEBUG)
        self.file_handler.setFormatter(self.fmt)
        self.logger.addHandler(self.file_handler)

    def logmessage(self, error, ft=None, exc_info=False):
        outmessage = dbgmsg[error]
        errlevel = outmessage[0]
        logger_err_level = LOGGER_ERROR_LEVELS[errlevel]
        errcode = outmessage[1]
        if ft is not None:
            full_errormessage = errcode + ', ' + (outmessage[2] % ft)
        else:
            full_errormessage = errcode + ', ' + outmessage[2]
        self.logger.log(logger_err_level, full_errormessage, exc_info=exc_info)
