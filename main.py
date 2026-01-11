import data_handler
import driver_control
from config_data import config_data
from logging import getLogger
from logging_setup import setup_logging
import time

logger = getLogger(__name__)


if __name__ == "__main__":

    logger = setup_logging("logging.csv")

    #Creating directory for course
    data_handler.create_folder(config_data.export_path)

    driver_control.logging_in(driver=config_data.web_driver)

    driver_control.make_get_request(driver=config_data.web_driver, url=config_data.teach_url)

    #Getting to the main course page
    topics = driver_control.get_course_topics(driver=config_data.web_driver)
    if topics[config_data.course_name]:

        main_course_page_url = f"{config_data.base_url}{topics[config_data.course_name]}"

        driver_control.make_get_request(driver=config_data.web_driver, url=main_course_page_url)
        logger.info("Successfully got to the course's main page")
    else:
        logger.critical("Problem with getting to the course's main page occured.")
        config_data.web_driver.quit()
        exit(3)

    #Getting course topics
    topics = driver_control.get_course_topics(driver=config_data.web_driver)

    #Creating folder for each topic
    data_handler.create_folders(config_data.export_path, list(topics.keys()))

    for key, value in topics.items():
        driver_control.parse_topic(driver=config_data.web_driver, topic_data=(key, f"{config_data.base_url}{value}"))
        time.sleep(5)

    config_data.web_driver.quit()












