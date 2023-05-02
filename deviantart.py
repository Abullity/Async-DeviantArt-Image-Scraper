#!/usr/bin/env python3

import sys
import os
import signal
import requests
import configparser
import argparse
from urllib.request import urlretrieve

def sigint_handler(signal, frame):
    print("\nInterrupted. Exiting...")
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

def get_access_token(client_id, client_secret):
    url = "https://www.deviantart.com/oauth2/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception("Failed to get access token")

def read_credentials_from_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)

    client_id = config.get("credentials", "client_id")
    client_secret = config.get("credentials", "client_secret")

    return client_id, client_secret

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

def list_galleries(username, access_token):
    galleries = get_user_galleries(username, access_token)

    for gallery in galleries:
        print(f"{gallery['name']} [{gallery['folderid']}]")

def download_gallery(author, access_token, default_filetype=None):
    author_dir = author
    if os.path.exists(author_dir):
        overwrite = input(f"Folder '{author_dir}' already exists. Overwrite contents? [Y/N]: ")
        if overwrite.strip().lower() != "y":
            print("Cancelled.")
            return
    else:
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
                    urlretrieve(item["content"]["src"], file_path)
                    print(f"Downloaded {file_name}")
            if data["has_more"]:
                params["offset"] += len(data["results"])
            else:
                break
        else:
            raise Exception("Failed to fetch gallery data")

def download_folder(author, folder_id, access_token, default_filetype=None):
    # Fetch the folder name using its ID
    galleries = get_user_galleries(author, access_token)
    folder_name = None
    for gallery in galleries:
        if gallery["folderid"] == folder_id:
            folder_name = gallery["name"]
            break

    if not folder_name:
        print("Folder not found.")
        return

    # Create the author directory if it doesn't exist
    if not os.path.exists(author):
        os.makedirs(author)
        
    # Create the folder directory inside the author directory
    author_dir = os.path.join(author, folder_name)
    if os.path.exists(author_dir):
        overwrite = input(f"Folder '{author_dir}' already exists. Overwrite contents? [Y/N]: ")
        if overwrite.strip().lower() != "y":
            print("Cancelled.")
            return
    else:
        os.makedirs(author_dir)

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
                    file_path = os.path.join(author_dir, file_name)
                    urlretrieve(item["content"]["src"], file_path)
                    print(f"Downloaded {file_name}")
            if data["has_more"]:
                params["offset"] += len(data["results"])
            else:
                break
        else:
            raise Exception("Failed to fetch folder data")
            
def download_all_folders(author, access_token, default_filetype=None):
    galleries = get_user_galleries(author, access_token)
    for gallery in galleries:
        download_folder(author, gallery["folderid"], access_token, default_filetype)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download an author's full gallery from DeviantArt.")
    parser.add_argument("author", type=str, help="The username of the author")
    parser.add_argument("-f", "--filetype", type=str, default="jpg", help="Default file type to use if the original file type is missing (e.g., jpg, png)")
    parser.add_argument("-l", "--list", action="store_true", help="List the gallery folders of the author instead of downloading their full gallery")
    parser.add_argument("--folder", type=str, help="Download images from the specified folder ID")
    parser.add_argument("--all", action="store_true", help="Download all images and folders")

    if len(sys.argv) <= 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    client_id, client_secret = read_credentials_from_config("client_auth.config")
    access_token = get_access_token(client_id, client_secret)

    if args.list:
        list_galleries(args.author, access_token)
    elif args.folder:
        download_folder(args.author, args.folder, access_token, args.filetype)
    elif args.all:
        download_gallery(args.author, access_token, args.filetype)
        download_all_folders(args.author, access_token, args.filetype)
    else:
        download_gallery(args.author, access_token, args.filetype)

