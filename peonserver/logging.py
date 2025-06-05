import time
import logging
import logging.handlers

LOG = logging.getLogger('peonserver ')  # init to a default value first

def set_logger(logfile=None, level=logging.DEBUG, name="peonserver") -> None:
    if logfile is None:
        # level does not set correctly when done this way, so set it after too.
        logging.basicConfig(level=level,
                            filename=logfile,
                            filemode='a' if logfile else None,
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S'
        )
        LOG = logging.getLogger(f'{name} ')

    else:
        handler = logging.handlers.RotatingFileHandler(
            logfile, maxBytes=1000000*5, backupCount=5)  # 5 MB
        formatter = logging.Formatter(
            '%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
            '%H:%M:%S')
        formatter.converter = time.gmtime
        handler.setFormatter(formatter)
        LOG = logging.getLogger(f'{name} ')
        LOG.addHandler(handler)

    LOG.setLevel(level)


