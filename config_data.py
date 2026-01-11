from json import load, JSONDecodeError
from logging import getLogger

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

            #Browser
            cls.browser_data = {
                'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                'AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/98.0.4758.102 Safari/537.36'),
                'Referer': config_data["URLs"]["login_url"],
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
                }

        return ConfigData._instance

config_data = ConfigData()