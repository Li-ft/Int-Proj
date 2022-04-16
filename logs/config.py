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

    # CONSOLE_LOG_FORMAT = "%(log_color)s%(asctime)s %(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"
    CONSOLE_LOG_FORMAT = "%(log_color)s%(levelname)s%(reset)s %(log_color)s%(message)s%(reset)s"
    logging.root.setLevel(LOG_LEVEL)
    console_formatter = ColoredFormatter(CONSOLE_LOG_FORMAT,
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
    console.setFormatter(console_formatter)

    # log file
    handler = logging.FileHandler(log_path, encoding='UTF-8')
    handler.setLevel(logging.DEBUG)
    file_formatter=logging.Formatter("%(message)s")
    handler.setFormatter(file_formatter)

    log = logging.getLogger(log_name)
    log.setLevel(LOG_LEVEL)
    log.addHandler(console)
    log.addHandler(handler)
    return log