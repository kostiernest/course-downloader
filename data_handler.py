from logging import getLogger
from typing import Dict
from requests import Session, exceptions, Response

logger = getLogger(__name__)

def make_get_request(session: Session, url: str, headers: Dict | None) -> Response | None:
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


def make_post_request(session: Session, url: str, data: Dict | None,  headers: Dict | None) -> Response | None:
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
        response = session.post(url=url, data=data, headers=headers)

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


def get_page_code(session: Session, url: str) -> str | None:
    pass
    #soup                        = BeautifulSoup(response.text, "html.parser")
