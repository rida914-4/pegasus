__author__ = "Ridah Naseem"
__credits__ = [""]
__version__ = "1.0.1"
__maintainer__ = "Ridah Naseem"
__email__ = "ridah.naseem@pegasussystems.com"
__status__ = "Development"

import logging
import datetime

# # Get an instance of a logger
logger = logging.getLogger(__name__)


def exception_handler(func):
    def called_function(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            logger.debug("{} {error}".format(func.__name__, error=e))
            logger.error(e)
    return called_function


def time_now_pkt():
    """ get pkt local time
    """
    time_delta = datetime.timedelta(hours=5)
    pkt_obj = datetime.timezone(time_delta, name="PKT")
    return datetime.datetime.now(pkt_obj)

