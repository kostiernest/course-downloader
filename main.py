import requests
import data_handler
from config_data import config_data
from logging import getLogger
from data_handler import make_get_request
from logging_setup import setup_logging


logger = getLogger(__name__)

if __name__ == "__main__":


    logger = setup_logging("logging.csv")


    with requests.Session() as session:

        data_handler.logging_in(session=session, url=config_data.login_url)

        make_get_request(session=session, url=config_data.main_course_page_url)










