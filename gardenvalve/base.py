import logging
from dotenv import dotenv_values

VERSION = "0.0.1"

CONFIGURATION_NAME = "configuration.json"
LOGGING_NAME = "valve.log.json"

loglevel = int(dotenv_values(".env").get("LOGLEVEL", logging.CRITICAL))
logging.basicConfig(format="%(levelname)s:%(funcName)s:%(lineno)d:%(message)s: ", level=loglevel)
LOGGER = logging.getLogger(__name__)
