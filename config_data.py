from json import load, JSONDecodeError
from logging import getLogger, Logger

logger: Logger = getLogger(__name__)

class ConfigData:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not ConfigData._instance:
            ConfigData._instance = super().__new__(cls)

            #Reading config file
            try:
                with open(file="config.json", mode="r", encoding="utf-8") as file:
                    c_data = load(fp=file)
            except (FileNotFoundError, JSONDecodeError) as e:
                logger.critical(f"[{type(e).__name__}] - [{e}]")
                exit(3)

            #Usage Mode
            cls.download_files = c_data["Usage_Mode"]["download_files"]
            cls.download_videos = ["Usage_Mode"]["download_videos"]
            #Course Data
            cls.course_name = c_data["course_name"]
            #Login_data
            cls.email = c_data["User_Data"]["email"]
            cls.password = c_data["User_Data"]["password"]

            #URLs
            cls.base_url = c_data["URLs"]["base_url"]
            cls.login_url = c_data["URLs"]["login_url"]
            cls.profile_url = c_data["URLs"]["profile_url"]
            cls.teach_url = c_data["URLs"]["teach_url"]

            #Video Downloading
            cls.video_download_attempts = c_data["video_download_attempts"]

            #Entry button text
            cls.login_button_text = c_data["login_button_text"]

            #Export path
            cls.video_data_path = c_data["video_data_path"]
            cls.export_path = c_data["export_path"]

            cls.retry_interval = c_data["retry_interval"]
            cls.process_number = c_data["process_number"]

        return ConfigData._instance

config_data = ConfigData()
