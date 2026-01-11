import requests
import data_handler
from config_data import config_data
from logging import getLogger
from logging_setup import setup_logging


logger = getLogger(__name__)




if __name__ == "__main__":


    logger = setup_logging("logging.csv")


    with requests.Session() as session:

        #logging in

        if (data_handler.make_post_request(session=session,
                                       url=config_data.login_url,
                                       data={"username" : config_data.username, "password" : config_data.password},
                                       headers=config_data.browser_data)):
            #Getting to profile page
            if (data_handler.make_get_request(session=session,
                                      url=config_data.profile_url,
                                      headers=config_data.browser_data)):
                pass




