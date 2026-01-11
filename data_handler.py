import os.path
from logging import getLogger
from os import walk, remove, listdir, rmdir, mkdir
from os.path import isdir, exists, isfile
from queue import LifoQueue
from typing import List

logger = getLogger(__name__)

def clear_old_files(path: str) -> None:

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

    if exists(path):
        clear_old_files(path)

    mkdir(path)

def create_folders(location: str, folder_names: List[str]) -> None:

    forbidden_symbols = ["<", ">", ":", "\"", "/", "\\", "|", "?", "*"]

    if exists(location):

        for folder_name in folder_names:
            #Getting rid of forbidden symbols
            for symbol in forbidden_symbols:
                if symbol in folder_name:
                    folder_name = folder_name.replace(symbol, "")

            path = f"{location}\\{folder_name}"

            mkdir(path)

def read_video_data(path: str) -> List[tuple[str,str]]:

    res = []
    try:
        with open(file=path, mode="r", encoding="utf-8") as file:
            for line in file:
                values = line.split(":")
                res.append(tuple(values))
    except FileNotFoundError as e:
        logger.critical(f"[{type(e).__name__}] - [{e}]")
        exit(3)

    return res

def has_video(path: str) -> bool:
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

