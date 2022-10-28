import os
from typing import Generator

import aiofiles
from src.config import FILES_PATH


async def create_dir(name):
    os.mkdir(f'{FILES_PATH}/{name}')


async def remove_file(dir_id, file):
    os.remove(f'{FILES_PATH}/{dir_id}/{file}')


async def async_upload_file(file, project_directory_id, file_id, ext):
    async with aiofiles.open(f'{FILES_PATH}{project_directory_id}/{file_id}{ext}', 'wb+') as out_file:
        while content := await file.read(1024):
            await out_file.write(content)


async def read_from_file(project_directory_id, file_id, ext) -> Generator:
    with open(file=f'{FILES_PATH}{project_directory_id}/{file_id}{ext}', mode="rb") as file_like:
        yield file_like.read()