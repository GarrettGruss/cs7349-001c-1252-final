# cs7349_001c_1252_final.config.logging_config.py
# Garrett Gruss 4/27/2025

import logging
import coloredlogs

# Format for all log messages
LOG_FORMAT = "%(asctime)s %(name)s:%(lineno)d %(levelname)s: %(message)s"

# Color mappings for individual fields
FIELD_STYLES = {
    'asctime': {'color': 'green'},
    'name':    {'color': 'blue'},
    'lineno':  {'color': 'blue'}
}

# Color mappings for each log level
LEVEL_STYLES = {
    'debug':    {'color': 'cyan'},
    'info':     {'color': 'green'},
    'warning':  {'color': 'yellow'},
    'error':    {'color': 'red'},
    'critical': {'color': 'magenta'}
}

# Plain file handler (no colors)
FILE_HANDLER = logging.FileHandler('app.log')
FILE_HANDLER.setLevel('DEBUG')
FILE_HANDLER.setFormatter(logging.Formatter(LOG_FORMAT))


def setup_logging():
    # Install colored console logging on root
    coloredlogs.install(
        level='DEBUG',
        fmt=LOG_FORMAT,
        field_styles=FIELD_STYLES,
        level_styles=LEVEL_STYLES,
        logger=logging.getLogger()
    )
    # Add file handler for persistent logs
    root = logging.getLogger()
    root.addHandler(FILE_HANDLER)
