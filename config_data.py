from json import load, JSONDecodeError
from logging import getLogger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

logger = getLogger(__name__)

class ConfigData:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not ConfigData._instance:
            ConfigData._instance = super().__new__(cls)

            #Reading config file
            try:
                with open(file="config.json", mode="r", encoding="utf-8") as file:
                    config_data = load(fp=file)
            except (FileNotFoundError, JSONDecodeError) as e:
                logger.critical(f"[{type(e).__name__}] - [{e}]")
                exit(3)

            #Login_data
            cls.email = config_data["User_Data"]["email"]
            cls.password = config_data["User_Data"]["password"]

            #URLs
            cls.login_url = config_data["URLs"]["login_url"]
            cls.profile_url = config_data["URLs"]["profile_url"]
            cls.main_course_page_url = config_data["URLs"]["main_course_page_url"]

            #Web driver
            cls.web_driver = webdriver.Chrome(service=Service(executable_path=config_data["Browser_Driver_Path"]))

            #Export path
            cls.export_path = config_data["export_path"]

        return ConfigData._instance

config_data = ConfigData()