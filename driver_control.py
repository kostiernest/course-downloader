import json
import multiprocessing
import re
from collections import namedtuple
from json import JSONDecodeError
import youtube_dl
from selenium import webdriver
from selenium.common import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logging import getLogger
from typing import Dict, List
from youtube_dl import DownloadError
import data_handler
from config_data import config_data
from bs4 import BeautifulSoup


logger = getLogger(__name__)
Data_Links = namedtuple("Data_Links", ["img_links", "file_links", "video_links"])


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

    soup = BeautifulSoup(page_html, "html.parser")

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
        login_button                        = driver.find_element(By.XPATH, "//button[contains(text(), 'Send')]")
        login_button.click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "btn-enter")))
        
        logger.info("Login successful.")

    except Exception as e:
        logger.critical(f"[{type(e).__name__}] - [{e}]")
        driver.quit()
        exit(3)


def get_course_topics(driver: webdriver) -> Dict | None:

    html_code = get_page_code(driver=driver)

    soup = BeautifulSoup(html_code, "html.parser")

    div = soup.find("div", class_="col-md-12")

    if div:
        table = div.find("table", class_="stream-table")

        if table:

            links = [a.get("href") for a in table.find_all("a") if a.get("href")]
            names = [span.get_text(strip=True) for span in table.find_all("span", class_="stream-title")]

            topics = dict(zip(names, links))
            try:
                topics.pop("Step№1. Instructions to the course.")
            except (ValueError, KeyError) as e:
                pass

            return topics


def get_topic_lessons(driver: webdriver) -> Dict | None:

    html_code = get_page_code(driver=driver)

    soup = BeautifulSoup(html_code, "html.parser")

    lessons = soup.find_all("li", class_="user-state-reached")

    links = []
    lesson_names = []
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
                full_str = f"{config_data.export_path}\\{topic_name}\\{lesson_name}:{video_link}"
                file.write(full_str)

    driver.back()


def parse_lesson(driver: webdriver, topic_name, lesson_name: str, lesson_link: str):

    make_get_request(driver=driver, url=lesson_link)

    html = get_page_code(driver)

    all_links = get_data_links(driver, html)

    driver.back()

    return all_links.video_links


def get_data_links(driver: webdriver, html : str) -> namedtuple:

    soup = BeautifulSoup(html, "html.parser")
    blocks = soup.find_all("div", attrs={"data-code": True, "data-block-id": True})

    links = []
    player_links = []

    for block in blocks:

        for tag in block.find_all("iframe"):
            src = tag.get("src")
            if src:
                player_links.append(src)

        for tag in block.find_all("a"):
            href = tag.get("href")
            if href:
                links.append(href)

        for tag in block.find_all("a"):
            src = tag.get("img")
            if src:
                links.append(src)

    #Getting video links
    video_links = []
    for player_link in player_links:
        video_links.append(get_video_playlist_url(driver=driver, player_url=player_link))

    return Data_Links(img_links=links, file_links=None,video_links=video_links)


def get_video_playlist_url(driver: webdriver, player_url: str) -> str:

    make_get_request(driver=driver, url=player_url)

    html = get_page_code(driver=driver)

    soup = BeautifulSoup(html, "html.parser")

    try:
        tag = soup.find("script", text=re.compile(r"window\.configs\s*=\s*\{"))

        if not tag:
            raise Exception("Failed to get masterPlaylistUrl.")

        script = tag.string
        match = re.search(r"window\.configs\s*=\s*(\{.*?\})(?:\s*;|\s*$)", script, re.DOTALL)

        if not match:
            raise Exception("Failed to get JSON.")

        json_str = match.group(1).rstrip(";")

        master_url = json.loads(json_str).get("masterPlaylistUrl")

    except (Exception, JSONDecodeError) as e:
        logger.critical(f"[{type(e).__name__}] - [{e}]")
        exit(3)

    driver.back()

    logger.info(f"Link to download video acquired: {master_url}")

    return master_url


def download_videos(video_data: List[tuple[str, str]]):
    with multiprocessing.Pool() as pool:
        pool.map(download_video, video_data)


def download_video(video_data: tuple[str,str]) -> None:

    path, url = video_data

    if data_handler.has_video(path=path):
        return

    ydl_set = {"format" : "best",
               "hls_prefer_native": True,
               "hls_use_mpegts": True,
               "verbose": True,
               "outtmpl": f"{path}/%(title)s.%(ext)s",
               "ffmpeg_location": "ffmpeg\\bin\\ffmpeg.exe",}

    for attempt in range(0,5):
        try:
            with youtube_dl.YoutubeDL(ydl_set) as ydl:
                ydl.download([url])
            break

        except DownloadError:
            logger.critical(f"Failed to download a video. Try number: {attempt}")
