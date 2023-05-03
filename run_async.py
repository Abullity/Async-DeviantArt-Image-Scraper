#!/usr/bin/env python3

import os
import sys
import time
import asyncio
import aiohttp
import aiofiles
import re

API_URL = "https://www.deviantart.com/_napi/da-user-profile/api/gallery/contents"


async def download_img(session, index, url, file_type):
    url = "https://backend.deviantart.com/oembed?url=" + url

    async with session.get(url) as response:
        if response.ok:
            json = await response.json()
            # Replace any invalid characters for file names with underscores
            safe_title = re.sub(r'[\\/*?:"<>|]', '_', json["title"]) + f".{file_type}"

            async with session.get(json["url"]) as img_response:
                if img_response.ok:
                    async with aiofiles.open(safe_title, mode='wb') as file:
                        await file.write(await img_response.read())
                        print(f"Downloaded {safe_title}")


async def request_next_bunch(session, params, file_type):
    tasks = []
    async with session.get(API_URL, params=params) as response:
        if response.ok:
            json = await response.json()

            for index, img in enumerate(json["results"]):
                url = img["deviation"]["url"]
                tasks.append(asyncio.create_task(download_img(session, index, url, file_type)))

            params["offset"] = json["nextOffset"]

            await asyncio.gather(*tasks)


async def main(account, file_type):
    params = {
        "username": account,
        "offset": 0,
        "limit": 20
    }

    async with aiohttp.ClientSession() as session:
        while params["offset"] is not None:
            await request_next_bunch(session, params, file_type)
