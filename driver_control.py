import time
import requests
import data_handler
from json import loads
from os.path import basename, join
from youtube_dl import YoutubeDL, DownloadError
from io import BytesIO
from re import search, compile, DOTALL
from selenium import webdriver
from selenium.common import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from collections import namedtuple
from json import JSONDecodeError
from urllib.parse import urljoin
from requests import Session, Response
from logging import getLogger, Logger
from typing import Dict
from config_data import config_data
from bs4 import BeautifulSoup
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True


logger: Logger = getLogger(__name__)
Lesson_Data = namedtuple("Lesson_Data", ["text", "img_links", "file_links", "video_links"])


def is_connected(url: str = "https://www.google.com", timeout: int = 5) -> bool:
    """
    Checks if the device still has internet connection.
    Args:
        url(str): Url to test internet connection.
        timeout(int): Timeout

    Returns:
        bool: True if internet is still present. Otherwise, False.

    """
    try:
        requests.get(url, timeout=timeout)
        return True
    except requests.RequestException:
        logger.error("No connection to the internet")
        return False


def make_get_request(driver: webdriver, url: str) -> None:
    """
    Makes url get request of webdriver

    Args:
        driver(webdriver): Webdriver.
        url(str): URL.
    Returns:
        Returns nothing.
    """

    while True:
        if is_connected():
            try:
                driver.get(url)
                #Waiting until page completely loaded
                WebDriverWait(driver, 20).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
            except (TimeoutException,
                    WebDriverException,
                    Exception):
                logger.error(f"Click-through failed {url}, maybe not enough time to load page.")
                time.sleep(config_data.retry_interval)
                continue
            else:
                 logger.info(f"Click-through to {url} successful.")
                 break
        else:
            time.sleep(config_data.retry_interval)


def get_page_code(driver: webdriver) -> str | None:
    """
    Getting html code of page using webdriver.
    Args:
        driver(webdriver): Webdriver.

    Returns:
        str | None: Html code of page or None.

    """
    page_html = driver.page_source

    soup = BeautifulSoup(page_html, "html.parser")

    return soup.prettify()


def logging_in(driver: webdriver) -> None:
    """
    Logging in webdriver.
    Args:
        driver(webdriver): Webdriver.

    Returns:
        Returns nothing.
    """
    try:
        #Going to the login page
        make_get_request(driver=driver, url=config_data.login_url)

        #Finding fields for info
        email_filed = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")

        #Filling
        email_filed.clear()
        email_filed.send_keys(config_data.email)

        password_field.clear()
        password_field.send_keys(config_data.password)

        #Pressing log in button
        login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send')]")
        login_button.click()

        logger.info("Login successful.")

    except Exception as e:
        logger.critical(f"[{type(e).__name__}] - [{e}]")
        driver.quit()
        exit(3)


def get_course_topics(driver: webdriver) -> Dict | None:
    """
    Getting topics of course.
    Args:
        driver(webdriver): Webdriver.

    Returns:
        Dict | None: If everything is correct, returns dictionary of topics. Otherwise, None.

    """
    html_code = get_page_code(driver=driver)

    soup: BeautifulSoup = BeautifulSoup(html_code, "html.parser")

    div = soup.find("div", class_="col-md-12")

    if div:
        table = div.find("table", class_="stream-table")

        if table:

            links = [a.get("href") for a in table.find_all("a") if a.get("href")]
            names = [span.get_text(strip=True) for span in table.find_all("span", class_="stream-title")]

            topics = dict(zip(names, links))

            return topics


def get_topic_lessons(driver: webdriver) -> Dict | None:
    """
    Get lessons of the topic.
    Args:
        driver(webdriver): Webdriver.
    Returns:
        Dict | None: If everything is correct, returns dictionary of lessons. Otherwise, None.

    """
    html_code = get_page_code(driver=driver)

    soup: BeautifulSoup = BeautifulSoup(html_code, "html.parser")

    lessons = soup.find_all("li", class_="user-state-reached")

    links: list[str] = []
    lesson_names: list[str] = []
    for li in lessons:

        title_div = li.find("div", class_="link title")
        link = title_div.get("href")
        lesson_name = title_div.get_text(strip=True)
        if "completed" in lesson_name:
            lesson_name=lesson_name[:-11]

        if not ("ZOOM meeting" in lesson_name):
            links.append(link)
            lesson_names.append(lesson_name)

    return dict(zip(lesson_names, links))


def parse_topic(driver:webdriver, topic_name: str, topic_link: str):

    make_get_request(driver=driver, url=topic_link)

    lessons = get_topic_lessons(driver)

    data_handler.create_folders(location=f"{config_data.export_path}\\{topic_name}", folder_names=list(lessons.keys()))

    with open(file=config_data.video_data_path, mode="a", encoding="utf-8") as file:

        for lesson_name, lesson_link in lessons.items():
            video_links = parse_lesson(driver       = driver,
                                       topic_name   = topic_name,
                                       lesson_name  = lesson_name,
                                       lesson_link  = f"{config_data.base_url}{lesson_link}")

            for video_link in video_links:
                full_str                    = f"{config_data.export_path}\\{topic_name}\\{lesson_name}|{video_link}\n"
                file.write(full_str)

    driver.back()


def parse_lesson(driver: webdriver, topic_name, lesson_name: str, lesson_link: str):

    make_get_request(driver=driver, url=lesson_link)

    html = get_page_code(driver)

    all_data = get_data_links(driver, html)

    #Writing data
    try:

        #Saving text
        if len(all_data.text) > 0:
            with open(file=f"{config_data.export_path}\\{topic_name}\\{data_handler.get_rid_of_forbidden_symbols(lesson_name)}\\Text.txt", mode="w",
                      encoding="utf-8") as file:
                file.write(all_data.text)
                logger.info(f"Text saved:{lesson_name}")

        session: Session = Session()

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
        }

        for cookie in driver.get_cookies():
            session.cookies.set(cookie["name"], cookie["value"])

        #Saving images
        for link in all_data.img_links:
            file_name: str = basename(link)
            file_path: str = f"{config_data.export_path}\\{topic_name}\\{data_handler.get_rid_of_forbidden_symbols(lesson_name)}"
            url = urljoin("https:", link)
            response: Response = session.get(url=url, headers=headers)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))

            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")

            save_path = join(file_path, f"{file_name}.png")
            img.save(save_path, 'PNG')
            logger.info(f"Image saved:{url}")

        #Saving files
        for link in all_data.file_links:
            file_name = basename(link)
            file_path = f"{config_data.export_path}\\{topic_name}\\{data_handler.get_rid_of_forbidden_symbols(lesson_name)}"
            response: Response = session.get(url=link, headers=headers)
            response.raise_for_status()
            with open(f"{file_path}\\{file_name}", "wb") as f:
                f.write(response.content)

            logger.info(f"File saved:{link}")

        session.close()

    except Exception as e:
        logger.critical(f"[{type(e).__name__}] - [{e}]")
        exit(3)

    return all_data.video_links


def get_data_links(driver: webdriver, html : str) -> namedtuple:
    """
    Gets links to data from page.
    Args:
        driver(webdriver): Webdriver.
        html(str): Html of page.

    Returns:
        namedtuple: Container with different types of links. namedtuple("Lesson_Data", ["text", "img_links", "file_links", "video_links"])

    """

    soup: BeautifulSoup = BeautifulSoup(html, "html.parser")
    blocks = soup.find_all("div", attrs={"data-code": True,
                                               "data-block-id": True})

    all_text: str = ""
    image_links: list[str] = []
    file_links: list[str] = []
    player_links: list[str]= []

    for block in blocks:
        #Player links
        for tag in block.find_all("iframe"):
            link_p = tag.get("src")
            if link_p:
                player_links.append(link_p)
        #Files
        for tag in block.find_all("a"):
            href = tag.get("href")
            if href:
                if href.lower().endswith(".pdf") or href.lower().endswith(".xlsx"):
                    file_links.append(href)
        #Images
        for tag in block.find_all("img"):
            src = tag.get("src")
            if src:
                class_data = tag.get("class")
                if class_data and "lt-image-common" in class_data:
                    image_links.append(src)

        #Text
        for tag in block.find_all("p"):
            for p in tag:
                text = p.get_text(strip=True)
                if text:
                    all_text +=f"{text}\n"


    #Getting video links
    video_links: list[str] = []
    for player_link in player_links:
        video_links.append(get_video_playlist_url(driver=driver, player_url=player_link))

    return Lesson_Data(text=all_text, img_links=image_links, file_links=file_links,video_links=video_links)


def get_video_playlist_url(driver: webdriver, player_url: str) -> str:
    """
    Gets url to download video from player.
    Args:
        driver(webdriver): Webdriver.
        player_url(str): Url of the video player.

    Returns:
        str: Url to download video.

    """
    make_get_request(driver=driver, url=player_url)

    html = get_page_code(driver=driver)

    soup: BeautifulSoup = BeautifulSoup(html, "html.parser")

    try:
        tag = soup.find("script", text=compile(r"window\.configs\s*=\s*\{"))

        if not tag:
            raise Exception("Failed to get masterPlaylistUrl.")

        script = tag.string
        match = search(r"window\.configs\s*=\s*(\{.*?\})(?:\s*;|\s*$)", script, DOTALL)

        if not match:
            raise Exception("Failed to get JSON.")

        json_str = match.group(1).rstrip(";")

        master_url = loads(json_str).get("masterPlaylistUrl")


    except (Exception, JSONDecodeError) as e:
        logger.critical(f"[{type(e).__name__}] - [{e}]")
        exit(3)

    driver.back()

    logger.info(f"Link to download video acquired: {master_url}")

    return master_url


def download_video(video_data: tuple[str,str]) -> None:

    """
    Download video using youtube-dl.
    Args:
        video_data(tuple[str,str]:  location_to_store_video, link to download video

    Returns:
        Returns nothing.

    """
    path, url = video_data

    ydl_set = {"format" : "best",
                "hls_prefer_native": True,
                "hls_use_mpegts": True,
                "verbose": True,
                "outtmpl": f"{path}/%(title)s.%(ext)s",
                "ffmpeg_location": "ffmpeg\\bin\\ffmpeg.exe"}

    for attempt in range(0,5):
        try:
            with YoutubeDL(ydl_set) as ydl:
                ydl.download([url])
            break

        except DownloadError:
            logger.critical(f"Failed to download a video. Try number: {attempt}")

    config_data.web_driver.quit()
