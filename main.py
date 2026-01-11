import time
import driver_control
from config_data import config_data
from logging import getLogger
from logging_setup import setup_logging

logger = getLogger(__name__)

if __name__ == "__main__":


    logger = setup_logging("logging.csv")

    driver_control.logging_in(config_data.web_driver)

    time.sleep(5)

    config_data.web_driver.quit()












