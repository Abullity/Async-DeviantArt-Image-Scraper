#!/usr/bin/env python3

import sys
import os
import signal
import requests
import configparser
import argparse
from urllib.request import urlretrieve

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

def read_credentials_from_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)

    client_id = config.get("credentials", "client_id")
    client_secret = config.get("credentials", "client_secret")

    return client_id, client_secret

def authenticate(client_id, client_secret):
    client_id, client_secret = read_credentials_from_config("config.ini")
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }
    response = requests.post("https://www.deviantart.com/oauth2/token", data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception("Failed to authenticate")

def get_user_galleries(username, access_token):
    url = f"https://www.deviantart.com/api/v1/oauth2/gallery/folders"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"username": username, "offset": 0, "limit": 10}
    galleries = []

    while True:
        response = requests.get(url, headers=headers, params=params)
        response_data = response.json()

        if "results" not in response_data:
            break

        galleries.extend(response_data["results"])

        if not response_data["has_more"]:
            break

        params["offset"] += response_data["next_offset"]

    return galleries

def list_folders(author, access_token):
    galleries = get_user_galleries(author, access_token)

    for gallery in galleries:
        folder_id = gallery["folderid"]
        folder_name = gallery["name"].replace('/', '-')
        print(f"{folder_name} [{folder_id}]")

def download_gallery(author, access_token, default_filetype=None):
    author_dir = author
    if not os.path.exists(author_dir):
        os.makedirs(author_dir)

    url = "https://www.deviantart.com/api/v1/oauth2/gallery/all"
    params = {
        "access_token": access_token,
        "username": author,
        "offset": 0,
        "limit": 24,
    }

    while True:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            for item in data["results"]:
                if item["is_downloadable"]:
                    title = item["title"].replace('/', '-')
                    try:
                        file_ext = item["content"]["filetype"].split('/')[-1]
                    except KeyError:
                        if default_filetype:
                            file_ext = default_filetype
                        else:
                            print(f"Failed to download {item['title']} due to missing filetype information")
                            continue
                    file_name = f"{title}.{file_ext}"
                    file_path = os.path.join(author_dir, file_name)
                    if not os.path.exists(file_path):
                        urlretrieve(item["content"]["src"], file_path)
                        print(f"Downloaded {file_name}")
                    else:
                        print(f"Skipped {file_name} (already exists)")
            if data["has_more"]:
                params["offset"] += len(data["results"])
            else:
                break
        else:
            raise Exception("Failed to fetch gallery data")

def download_folder(author, folder_id, access_token, folder_name, default_filetype=None):
    folder_dir = os.path.join(author, folder_name)
    
    if not os.path.exists(folder_dir):
        os.makedirs(folder_dir)

    url = f"https://www.deviantart.com/api/v1/oauth2/gallery/{folder_id}"
    params = {
        "access_token": access_token,
        "username": author,
        "offset": 0,
        "limit": 24,
    }

    while True:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            for item in data["results"]:
                if item["is_downloadable"]:
                    title = item["title"].replace('/', '-')
                    try:
                        file_ext = item["content"]["filetype"].split('/')[-1]
                    except KeyError:
                        if default_filetype:
                            file_ext = default_filetype
                        else:
                            print(f"Failed to download {item['title']} due to missing filetype information")
                            continue
                    file_name = f"{title}.{file_ext}"
                    file_path = os.path.join(folder_dir, file_name)
                    if os.path.exists(file_path):
                        print(f"Skipping existing file: {file_path}")
                        continue
                    urlretrieve(item["content"]["src"], file_path)
                    print(f"Downloaded {file_name}")
            if data["has_more"]:
                params["offset"] += len(data["results"])
            else:
                break
        else:
            raise Exception("Failed to fetch gallery data")

def download_all_folders(author, access_token, default_filetype=None):
    galleries = get_user_galleries(author, access_token)
    
    if not os.path.exists(author):
        os.makedirs(author)
    
    for gallery in galleries:
        folder_id = gallery["folderid"]
        folder_name = gallery["name"].replace('/', '-')
        download_folder(author, folder_id, access_token, folder_name, default_filetype)

def get_folder_name_and_dir(author, folder_id):
    galleries = get_user_galleries(author, access_token)
    for gallery in galleries:
        if gallery["folderid"] == folder_id:
            folder_name = gallery["name"].replace('/', '-')
            folder_dir = os.path.join(author, folder_name)
            return folder_name, folder_dir
    else:
        raise Exception(f"Folder {folder_id} not found for author {author}")

if __name__ == "__main__":
    args = parser.parse_args()

    if not args.author:
        parser.print_help()
        sys.exit(0)

    client_id, client_secret = read_credentials_from_config("config.ini")
    access_token = authenticate(client_id, client_secret)

    if args.list:
        list_folders(args.author, access_token)
    elif args.folder:
        folder_id = args.folder
        folder_name, _ = get_folder_name_and_dir(args.author, folder_id)
        download_folder(args.author, folder_id, access_token, folder_name, args.filetype)
    elif args.all:
        download_gallery(args.author, access_token, args.filetype)
        download_all_folders(args.author, access_token, args.filetype)
    else:
        download_gallery(args.author, access_token, args.filetype)

