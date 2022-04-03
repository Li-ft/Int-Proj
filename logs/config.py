from colorlog import ColoredFormatter
import logging



# log.debug("This is debug.")
# log.info("This is info.")
# log.warning("This is warning.")
# log.error("This is error.")
# log.critical("This is critical.")

def log_config(log_name: str, log_path:str):
    LOG_LEVEL = logging.DEBUG
    CONSOLE_LEVEL= logging.INFO

    # LOGFORMAT = "%(log_color)s%(asctime)s %(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"
    LOGFORMAT = "%(log_color)s%(levelname)s%(reset)s %(log_color)s%(message)s%(reset)s"
    logging.root.setLevel(LOG_LEVEL)
    formatter = ColoredFormatter(LOGFORMAT,
                                 log_colors={
                                     'DEBUG': 'cyan',
                                     'INFO': 'green',
                                     'WARNING': 'bg_yellow',
                                     'ERROR': 'red',
                                     'CRITICAL': 'bold_red'
                                 })
    # console
    console = logging.StreamHandler()
    console.setLevel(CONSOLE_LEVEL)
    console.setFormatter(formatter)

    # log file
    handler = logging.FileHandler(log_path, encoding='UTF-8')
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)

    log = logging.getLogger(log_name)
    log.setLevel(LOG_LEVEL)
    log.addHandler(console)
    log.addHandler(handler)
    return log