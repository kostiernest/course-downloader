from json import load, JSONDecodeError
from logging import getLogger
from typing import  Dict
from requests import Session, Response

from logging_setup import setup_logging

logger = getLogger(__name__)

def read_config(path: str)->Dict | None:
    """
    Reads config file. It supposes to be json.
    Args:
        path(str): Path ot config file.

    Returns:
        Dict | None : Confit data in dictionary or nothing something went wrong.

    """

    try:
        with open(file=path, mode="r", encoding="utf-8") as file:
            return load(fp=file)
    except (FileNotFoundError, JSONDecodeError) as e:
        logger.critical(f"[{type(e).__name__}] - [{e}]")
        exit(3)


if __name__ == "__main__":


    logger = setup_logging("logging.csv")
    config = read_config("config.json")
    login_url = config["Course-Urls"]["login-url"]
    profile_url = config["Course-Urls"]["profile-url"]
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
               "Referer" : login_url}

    session: Session = Session()

    response: Response = session.post(login_url, data=config["User-Data"], headers=headers)
    print(response.url)

    p_response: Response = session.get(profile_url, headers=headers)
    print(p_response.url)



