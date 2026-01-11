from logging import getLogger
from os import walk, remove, listdir, rmdir, mkdir
from os.path import isdir, exists
from queue import LifoQueue
from typing import List
from config_data import config_data

logger = getLogger(__name__)

def clear_old_files(path: str) -> None:

    try:
        if exists(path):

            if not isdir(path):
                raise ValueError("Path: {path} leads to file not to directory.")

            folder_remain_to_delete     = LifoQueue()
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


def create_folders(folder_names: List[str]) -> None:

    if exists(config_data.export_path):

        for folder_name in folder_names:
            path  = f"{config_data.export_path}\\{folder_name}"
            mkdir(path)

