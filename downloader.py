from logging import Logger
from logging_setup import setup_logging
logger: Logger = setup_logging("logging.csv")
import os.path
from multiprocessing import Pool, freeze_support
import data_handler
import driver_control
from config_data import config_data
import time

if __name__ == "__main__":

    # Initializing web
    web_driver = driver_control.init_webdriver()

    freeze_support()

    if config_data.download_files:
        #Creating directory for course
        data_handler.create_folder(config_data.export_path)

        # If already exists delete previous one
        if os.path.exists(config_data.video_data_path):
            os.remove(config_data.video_data_path)

        # Logging in
        driver_control.logging_in(driver=web_driver, button_text=config_data.login_button_text)

        # Getting to the course page
        driver_control.make_get_request(driver=web_driver, url=config_data.teach_url)

        logger.info("Successfully got to the course's main page")

        #Getting course topics
        topics = driver_control.get_course_topics(driver=web_driver)

        #Creating folder for each topic
        data_handler.create_folders(config_data.export_path, list(topics.keys()))

        for key, value in topics.items():
            driver_control.parse_topic(driver=web_driver, topic_name=key, topic_link=f"{config_data.base_url}{value}")
            time.sleep(5)

        web_driver.quit()

    if config_data.download_videos:

        video_data = data_handler.read_video_data(config_data.video_data_path)

        with Pool(config_data.process_number) as pool:
            pool.map(driver_control.download_video, video_data)

    web_driver.quit()










