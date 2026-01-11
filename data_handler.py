import re
from logging import getLogger
from typing import Dict
from requests import  Session, exceptions, Response
from config_data import config_data
from bs4 import BeautifulSoup

logger = getLogger(__name__)


def make_get_request(session: Session, url: str, headers: Dict | None = config_data.browser_data) -> Response | None:
    """
    Makes url get request of session.
    If status code of the response is somewhat not in 200...300. Then it only means that something not acceptable has happened.

    Args:
        session(Session): Object of session.
        url(str): URL.
        headers(Dict | Node): Headers of request.

    Returns:
        Response | None: If status code of response is in 200...300, returns object of response. Else, None.

    """
    try:
        response = session.get(url=url, headers=headers)

        if  not response.ok:
            raise exceptions.RequestException(f"Response: {response.url} with status code:{response.status_code}")

    except (exceptions.RequestException,
            exceptions.ConnectionError,
            exceptions.URLRequired,
            exceptions.InvalidURL) as e:
        logger.critical(f"[{type(e).__name__}] - [{e}]")
        exit(3)
    else:
        return response


def make_post_request(session: Session, url: str, data: Dict | None,  headers: Dict | None = config_data.browser_data) -> Response | None:
    """
    Makes url post request of session.
    If status code of the response is somewhat not in 200...300. Then it only means that something not acceptable has happened.

    Args:
        session(Session): Object of session.
        data(Dict): Data of post request.
        url(str): URL.
        headers(Dict | Node): Headers of request.

    Returns:
        Response | None: If status code of response is in 200...300, returns object of response. Else, None.

    """
    try:
        response = session.post(url=url, data=data, headers=headers, allow_redirects=True)

        if  not response.ok:
            raise exceptions.RequestException(f"Response: {response.url} with status code:{response.status_code}")

    except (exceptions.RequestException,
            exceptions.ConnectionError,
            exceptions.URLRequired,
            exceptions.InvalidURL) as e:
        logger.critical(f"[{type(e).__name__}] - [{e}]")
        exit(3)
    else:
        return response



def get_page_code(session: Session, url: str, headers: Dict | None = config_data.browser_data) -> str | None:
    response                    = make_get_request(session=session, url=url, headers=headers)

    soup                        = BeautifulSoup(response.text, "html.parser")

    page_html                   = soup.prettify()

    return page_html


def logging_in(session: Session, url:str):

    response = get_page_code(session=session, url=url)

    try:
        #Finding csrf
        csrf_find_res = re.search(r'window\.csrfToken\s*=\s*"([^"]+)"', response)
        csrf = csrf_find_res.group(1) if csrf_find_res else None

        if not csrf:
            raise ValueError("Csrf token not found.")
    except ValueError as e:
        logger.critical(f"[{type(e).__name__}] - [{e}]")
        exit(3)

    login_data = {"email"    : config_data.email,
                  "password" : config_data.password,
                  "csrfToken": csrf,
                  "requestSimpleSign": "3856797c14014e4d41d922d8f1171852",
                  "controllerId": "system",
                  "actionId": "login"}

    response = make_post_request(session=session, url=url, data=login_data)

    print(response.status_code)

    print(response.text)







