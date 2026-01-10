from json import load, JSONDecodeError
from logging import getLogger
from typing import  Dict
import requests


logger                          = getLogger(__name__)

def read_config(path: str)->Dict | None:

    try:
        with open(file=path, mode="r", encoding="utf-8") as file:
            return load(fp=file)
    except (FileNotFoundError, JSONDecodeError) as e:
        logger.critical(f"[{e.__name__}] - [{e}]")
        exit(3)




if __name__ == "__main__":


    config                      = read_config("config.json")
    login_url                   =  config["Course-Urls"]["login-url"]
    profile_url                 =  config["Course-Urls"]["profile-url"]
    headers                     = {
                                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
                                    "Referer" : login_url
                                  }


    session                     = requests.Session()

    response                    = session.post(login_url, data=config["User-Data"], headers=headers)
    print(response.url)

    p_response                  = session.get(profile_url, headers=headers)
    print(p_response.url)



