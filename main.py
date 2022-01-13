import asyncio
import os
import aiofiles as aiofiles
import requests
import aiohttp
from utils import time_tracker


ALBUMS_URL = 'https://jsonplaceholder.typicode.com/albums/'
PHOTOS_URL = 'https://jsonplaceholder.typicode.com/photos/'
CONCURRENT_REQUESTS = 100


class UploadInfo:

    @staticmethod
    def get_all_albums(url: str) -> dict:
        resp = requests.get(url)
        albums = resp.json()
        albums_dict = {album['id']: album['title'] for album in albums}
        return albums_dict

    @staticmethod
    def get_all_photos(url: str) -> dict:
        resp = requests.get(url)
        return resp.json()


class PhotoSaver:
    """Класс для сохранения фото по нужным папкам"""

    @staticmethod
    async def save_photo(url: str, photo_title: str, album_name: str) -> None:
        async with aiohttp.ClientSession() as session:
            if not os.path.exists(f'{album_name}'):
                os.makedirs(f'{album_name}')
            response = await session.get(url)
            if response.status == 200:
                f = await aiofiles.open(f'{album_name}/{photo_title}.png', mode='wb')
                await f.write(await response.read())
                await f.close()


@time_tracker
async def main():
    photos = UploadInfo.get_all_photos(PHOTOS_URL)
    albums = UploadInfo.get_all_albums(ALBUMS_URL)
    tasks = []
    for photo in photos:
        task = asyncio.create_task(
            PhotoSaver.save_photo(
                photo['url'],
                photo['title'],
                albums[photo['albumId']]
            )
        )
        tasks.append(task)

        if len(tasks) >= CONCURRENT_REQUESTS:
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            # asyncio.gather(*tasks) - почему такой вариант работает очень долго не понятно
            tasks = []

    if len(tasks) > 0:
        await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

if __name__ == '__main__':
    asyncio.run(main())
