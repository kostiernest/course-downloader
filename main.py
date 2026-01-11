import data_handler
from config_data import config_data
from logging import getLogger
from logging_setup import setup_logging

logger = getLogger(__name__)

if __name__ == "__main__":

    logger = setup_logging("logging.csv")

    #Creating directory for course
    data_handler.create_folder(config_data.export_path)

    #driver_control.logging_in(driver=config_data.web_driver)

    #driver_control.make_get_request(driver=config_data.web_driver, url=config_data.main_course_page_url)

    #time.sleep(5)

    config_data.web_driver.quit()












