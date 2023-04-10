import os
import sys
import time
import asyncio
import aiohttp
import aiofiles


API_URL = "https://www.deviantart.com/_napi/da-user-profile/api/gallery/contents"


async def download_img(session, title, url):
    url = "https://backend.deviantart.com/oembed?url=" + url

    async with session.get(url) as response:
        if response.ok:
            json = await response.json()
    
    async with session.get(json["url"]) as response:
        if response.ok:
            async with aiofiles.open(title, mode='wb') as file:
                await file.write(await response.read())


async def request_next_bunch(session, params):
    tasks = []
    async with session.get(API_URL, params=params) as response:
        if response.ok:
            json = await response.json()
            
            for index, img in enumerate(json["results"]):
                title, url = str(params["offset"] + index) + ".jpg", img["deviation"]["url"]
                tasks.append(asyncio.create_task(download_img(session, title, url)))

            params["offset"] = json["nextOffset"]    
            
            await asyncio.gather(*tasks)


async def main(account):
    params = {
        "username": account,
        "offset": 0,
        "limit": 20
    }

    async with aiohttp.ClientSession() as session:
        while params["offset"] is not None:
            await request_next_bunch(session, params)
