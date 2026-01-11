from selenium import webdriver
from selenium.common import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logging import getLogger
from config_data import config_data
from bs4 import BeautifulSoup

logger = getLogger(__name__)


def make_get_request(driver: webdriver, url: str) -> None:
    """
    Makes url get request of webdriver

    Args:
        driver(webdriver): Webdriver.
        url(str): URL.
    Returns:
        Returns nothing.
    """

    try:
        driver.get(url)

    except (TimeoutException,
            WebDriverException,
            Exception) as e:
        logger.critical(f"[{type(e).__name__}] - [{e}]")
        exit(3)
    else:
        logger.info(f"Click-through to {url} successful.")


def get_page_code(driver: webdriver) -> str | None:
    """
    Getting html code of page using webdriver.
    Args:
        driver(webdriver): Webdriver.

    Returns:
        str | None: Html code of page or None.

    """
    page_html = driver.page_source

    soup  = BeautifulSoup(page_html, "html.parser")

    return soup.prettify()


def logging_in(driver: webdriver):

    try:
        #Going to the login page
        make_get_request(driver=driver, url=config_data.login_url)

        #Waiting till the login page loads
        wait = WebDriverWait(driver,10)

        #Finding fields for info
        email_filed = wait.until(EC.presence_of_element_located((By.NAME, "email")))
        password_field = driver.find_element(By.NAME, "password")

        #Filling
        email_filed.clear()
        email_filed.send_keys(config_data.email)

        password_field.clear()
        password_field.send_keys(config_data.password)

        #Pressing log in button
        login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send')]")
        login_button.click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "btn-enter")))

        logger.info("Login successful.")

    except Exception as e:
        logger.critical(f"[{type(e).__name__}] - [{e}]")
        driver.quit()
        exit(3)


def get_course_topics(driver: webdriver):

    html_code = get_page_code(driver=driver)

    soup = BeautifulSoup(html_code, "html.parser")

    div = soup.find("div", class_="col-md-12")

    if div:
        table = div.find("table", class_="stream-table")

        if table:

            links = [a.get("href") for a in table.find_all("a") if a.get("href")]
            names = [span.get_text(strip=True) for span in table.find_all("span", class_="stream-title")]

            topics = dict(zip(names, links))

            return topics
