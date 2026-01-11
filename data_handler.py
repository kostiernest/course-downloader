import os.path
from logging import getLogger
from os import walk, remove, listdir, rmdir, mkdir
from os.path import isdir, exists, isfile
from queue import LifoQueue
from typing import List

logger = getLogger(__name__)


def clear_old_files(path: str) -> None:
    """
    Deletes all files in directory. And directory itself.
    Args:
        path(str): Path to folder.

    Returns:
        Returns nothing.

    """
    try:
        if exists(path):

            if not isdir(path):
                raise ValueError("Path: {path} leads to file not to directory.")

            folder_remain_to_delete = LifoQueue()
            for root, dirs, files in walk(path):

                if isdir(root):
                    for file in files:
                        remove(f"{root}\\{file}")

                    if not listdir(root):
                        rmdir(root)
                    else:
                        folder_remain_to_delete.put(root)

            while not folder_remain_to_delete.empty():
                path = folder_remain_to_delete.get()
                rmdir(path)

    except (ValueError, FileNotFoundError) as e:
        logger.critical(f"[{type(e).__name__}] - [{e}]")
        exit(3)


def create_folder(path: str) -> None:
    """
    Creates folder.
    Args:
        path(str): Path to folder.

    Returns:
        Returns nothing.

    """
    if exists(path):
        clear_old_files(path)

    mkdir(path)


def get_rid_of_forbidden_symbols(string: str)->str:
    """
    Gets of all prohibited symbols in str ["<", ">", ":", "\"", "/", "\\", "|", "?", "*"]
    Args:
        string(str): Path.

    Returns:
        std: Forbidden symbols free str.

    """
    forbidden_symbols = ["<", ">", ":", "\"", "/", "\\", "|", "?", "*"]
    for symbol in forbidden_symbols:
        if symbol in string:
            string = string.replace(symbol, "")

    return string


def create_folders(location: str, folder_names: List[str]) -> None:
    """
    Creates folders.
    Args:
        location(str): Location of folders
        folder_names(List[str]): List of names of folders.

    Returns:
        Returns nothing.

    """
    if exists(location):

        for folder_name in folder_names:
            #Getting rid of forbidden symbols
            folder_name = get_rid_of_forbidden_symbols(folder_name)

            path = f"{location}\\{folder_name}"

            mkdir(path)


def read_video_data(path: str) -> List[tuple[str,str]]:
    """
    Reads file with video data.
    Args:
        path(str): Path to file.

    Returns:
        List[tuple[str,str]]: List of data (name of the lesson of video, playlist_link).

    """
    res = []
    try:
        with open(file=path, mode="r", encoding="utf-8") as file:
            for line in file:
                values = line.split("|")
                res.append((values[0].strip(), values[1].strip()))
    except FileNotFoundError as e:
        logger.critical(f"[{type(e).__name__}] - [{e}]")
        exit(3)

    return res


def has_video(path: str) -> bool:
    """
    Checks if there is a video (.mp4 file) in folder.
    Args:
        path(str): Folder path.

    Returns:
        bool: True if there is atleast one video. Otherwise, False.

    """
    try:

        found = False
        for root, dirs, files in walk(path):
            if isfile(root):
                base,extension   = os.path.splitext(root)
                if extension == ".mp4":
                    found = True
                    break

    except FileNotFoundError as e:
        logger.critical(f"[{type(e).__name__}] - [{e}]")
        exit(3)

    return found

