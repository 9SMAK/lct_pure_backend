import os
import aiofiles
from src.config import FILES_PATH


async def create_dir(name):
    os.mkdir(f'{FILES_PATH}/{name}')


async def async_upload_file(file, project_directory_id, file_id, ext):
    async with aiofiles.open(f'{FILES_PATH}{project_directory_id}{file_id}{ext}', 'wb+') as out_file:
        while content := await file.read(1024):
            await out_file.write(content)