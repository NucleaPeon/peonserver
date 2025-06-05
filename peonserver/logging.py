import time
import logging
import logging.handlers

def set_logger(logfile=None, level=logging.DEBUG) -> None:
    if logfile is None:
        logging.basicConfig(level=level,
                            filename=logfile,
                            filemode='a' if logfile else None,
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S'
        )

    else:
        handler = logging.handlers.RotatingFileHandler(logfile, maxBytes=1000000*5,
                                                       backupCount=5)  # 5 MB
        formatter = logging.Formatter(
            '%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
            '%H:%M:%S')
        formatter.converter = time.gmtime
        handler.setFormatter(formatter)
        LOG = logging.getLogger('peonserver ')
        LOG.addHandler(handler)
        LOG.setLevel(level)


LOG = logging.getLogger('peonserver ')
