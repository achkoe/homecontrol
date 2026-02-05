import logging

VERSION = "0.0.1"

CONFIGURATION_NAME = "configuration.json"
LOGGING_NAME = "valve.log.json"

logging.basicConfig(format="%(levelname)s:%(funcName)s:%(lineno)d:%(message)s: ", level=logging.INFO)
LOGGER = logging.getLogger(__name__)
