
import asyncio
import os
import aiofiles as aiofiles
import requests
import aiohttp
from utils import time_tracker


ALBUMS_URL = 'https://jsonplaceholder.typicode.com/albums/'
PHOTOS_URL = 'https://jsonplaceholder.typicode.com/photos/'


class UploadInfo:

    @classmethod
    def get_all_albums(cls, url: str) -> dict:
        resp = requests.get(url)
        albums = resp.json()
        albums_dict = {album['id']: album['title'] for album in albums}
        return albums_dict

    @classmethod
    def get_all_photos(cls, url: str) -> dict:
        resp = requests.get(url)
        return resp.json()


class PhotoSaver:
    """Класс для сохранения фото по нужным папкам"""

    @classmethod
    async def save_photo(cls, session, url: str, photo_title: str, album_name: str) -> None:
        async with session.get(url, allow_redirects=True) as response:
            f = await aiofiles.open(f'{album_name}/{photo_title}.png', mode='wb')
            await f.write(await response.read())
            await f.close()


@time_tracker
async def main():
    photos = UploadInfo.get_all_photos(PHOTOS_URL)
    albums = UploadInfo.get_all_albums(ALBUMS_URL)
    for album in albums.values():
        if not os.path.exists(f"{album}"):
            os.mkdir(f"{album}")
    tasks = []
    async with aiohttp.ClientSession() as session:
        for photo in photos:
            task = asyncio.create_task(
                PhotoSaver.save_photo(
                    session,
                    photo['url'],
                    photo['title'],
                    albums[photo['albumId']]
                )            )
            tasks.append(task)
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
