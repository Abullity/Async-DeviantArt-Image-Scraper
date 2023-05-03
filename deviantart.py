#!/usr/bin/env python3

import sys
import os
import signal
import configparser
import argparse
import asyncio
import aiohttp
from urllib.parse import urlsplit
from pathlib import Path

import nest_asyncio

nest_asyncio.apply()  # Required to use asyncio in Jupyter/IPython

parser = argparse.ArgumentParser(description="Download DeviantArt galleries and folders.")
parser.add_argument("author", nargs="?", type=str, help="Author's DeviantArt username")
parser.add_argument("--list", action="store_true", help="List the author's folders")
parser.add_argument("-f", "--filetype", type=str, default="jpg", help="Default file type to use if the original file type is missing (e.g., jpg, png)")
parser.add_argument("--folder", type=str, help="Download the specified folder by its ID")
parser.add_argument("--all", action="store_true", help="Download all images from the author's gallery and all folders")

def sigint_handler(signal, frame):
    print("\nInterrupted. Exiting...")
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

def read_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)

    try:
        client_id = config.get("credentials", "client_id")
        if not client_id:
            print("Please set the client_id in the config file.")
            sys.exit(1)
    except (configparser.NoSectionError, configparser.NoOptionError):
        print("Please set the client_id in the config file.")
        sys.exit(1)

    try:
        client_secret = config.get("credentials", "client_secret")
        if not client_secret:
            print("Please set the client_secret in the config file.")
            sys.exit(1)
    except (configparser.NoSectionError, configparser.NoOptionError):
        print("Please set the client_secret in the config file.")
        sys.exit(1)

    try:
        max_concurrent_downloads = config.getint("settings", "max_concurrent_downloads")
        if max_concurrent_downloads < 1:
            print("Please set max_concurrent_downloads to a value of 1 or greater.")
            sys.exit(1)
    except (configparser.NoSectionError, configparser.NoOptionError):
        print("Please set max_concurrent_downloads in the config file.")
        sys.exit(1)

    return client_id, client_secret, max_concurrent_downloads

async def authenticate(client_id, client_secret):
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post("https://www.deviantart.com/oauth2/token", data=data) as response:
            if response.status == 200:
                response_json = await response.json()
                return response_json["access_token"]
            else:
                raise Exception("Failed to authenticate")

async def download_file(session, url, file_path):
    async with session.get(url) as response:
        if response.status == 200:
            with open(file_path, "wb") as f:
                while True:
                    chunk = await response.content.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
            print(f"Downloaded {file_path.name}")
        else:
            print(f"Failed to download {file_path.name}")

async def download_items(author, access_token, folder_id=None, folder_name=None, default_filetype=None):
    target_path = Path(author)
    if folder_name:
        target_path /= folder_name

    target_path.mkdir(parents=True, exist_ok=True)

    url = "https://www.deviantart.com/api/v1/oauth2/gallery/all" if folder_id is None else f"https://www.deviantart.com/api/v1/oauth2/gallery/{folder_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"username": author, "offset": 0, "limit": 24}

    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)

        async def download_item(item):
            async with semaphore:
                if item["is_downloadable"]:
                    title = item["title"].replace('/', '-')
                    try:
                        file_ext = item["content"]["filetype"].split('/')[-1]
                    except KeyError:
                        if default_filetype:
                            file_ext = default_filetype
                    else:
                        print(f"Failed to download {item['title']} due to missing filetype information")
                        return
                    file_name = f"{title}.{file_ext}"
                    file_path = target_path / file_name
                    if not file_path.exists():
                        await download_file(session, item["content"]["src"], file_path)
                    else:
                        print(f"Skipped {file_name} (already exists)")

        while True:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    await asyncio.gather(*(download_item(item) for item in data["results"]))

                    if data["has_more"]:
                        params["offset"] += len(data["results"])
                    else:
                        break
                else:
                    raise Exception("Failed to fetch gallery data")

async def get_user_galleries(username, access_token):
    url = f"https://www.deviantart.com/api/v1/oauth2/gallery/folders"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"username": username, "offset": 0, "limit": 10}
    galleries = []

    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(url, headers=headers, params=params) as response:
                response_data = await response.json()

                if "results" not in response_data:
                    break

                galleries.extend(response_data["results"])

                if not response_data["has_more"]:
                    break

                params["offset"] += response_data["next_offset"]

    return galleries

def list_folders(author, access_token):
    galleries = asyncio.run(get_user_galleries(author, access_token))

    for gallery in galleries:
        folder_id = gallery["folderid"]
        folder_name = gallery["name"].replace('/', '-')
        print(f"{folder_name} [{folder_id}]")

async def download_all_folders(author, access_token, default_filetype=None):
    galleries = await get_user_galleries(author, access_token)

    for gallery in galleries:
        folder_id = gallery["folderid"]
        folder_name = gallery["name"].replace('/', '-')
        await download_items(author, access_token, folder_id, folder_name, default_filetype)

def get_folder_name_and_dir(author, folder_id, access_token):
    folder_name = None
    folder_dir = None

    galleries = asyncio.run(get_user_galleries(author, access_token))
    for gallery in galleries:
        if gallery["folderid"] == folder_id:
            folder_name = gallery["name"].replace('/', '-')
            folder_dir = os.path.join(author, folder_name)
            break

    return folder_name, folder_dir

if __name__ == "__main__":
    args = parser.parse_args()

    if not args.author:
        parser.print_help()
        sys.exit(0)

    client_id, client_secret, MAX_CONCURRENT_DOWNLOADS = read_config("config.ini")
    access_token = asyncio.run(authenticate(client_id, client_secret))

    if args.list:
        list_folders(args.author, access_token)
    elif args.folder:
        folder_id = args.folder
        folder_name, _ = get_folder_name_and_dir(args.author, folder_id, access_token)
        asyncio.run(download_items(args.author, access_token, folder_id, folder_name, args.filetype))
    elif args.all:
        asyncio.run(download_items(args.author, access_token, default_filetype=args.filetype))
        asyncio.run(download_all_folders(args.author, access_token, args.filetype))
    else:
        asyncio.run(download_items(args.author, access_token, default_filetype=args.filetype))
