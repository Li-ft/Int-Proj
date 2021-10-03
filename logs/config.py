from colorlog import ColoredFormatter
import logging

LOG_LEVEL = logging.DEBUG

LOGFORMAT = "  %(log_color)s%(asctime)s  %(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"
logging.root.setLevel(LOG_LEVEL)
formatter = ColoredFormatter(LOGFORMAT,
                             log_colors={
                                 'DEBUG': 'cyan',
                                 'INFO': 'green',
                                 'WARNING': 'bg_yellow',
                                 'ERROR': 'red',
                                 'CRITICAL': 'bold_red'
                             })

stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
stream.setFormatter(formatter)

log = logging.getLogger('pythonConfig')
log.setLevel(LOG_LEVEL)
log.addHandler(stream)

log.debug("This is debug.")
log.info("This is info.")
log.warning("This is warning.")
log.error("This is error.")
log.critical("This is critical.")