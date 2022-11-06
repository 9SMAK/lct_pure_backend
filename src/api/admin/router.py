import shutil
import uuid

from fastapi import APIRouter
from PIL import ImageFont, Image, ImageDraw

from src.api.schemas import OkResponse
from src.database.repositories import IDEA, SKILL, IDEATAG
from src.config import FILES_PATH

router = APIRouter(prefix="/admin", tags=["Admin"])

size = 100


async def generate_circles(text, circle_id, color="red"):
    font = ImageFont.truetype(f'src/api/admin/arial.ttf', 15)
    image = Image.new('RGBA', (size, size))
    draw = ImageDraw.Draw(image)
    draw.ellipse((0, 0, size, size), fill=color)
    draw.text((size // 2, size // 2), text, font=font, align="center", anchor="mm")
    image.save(f'{FILES_PATH}{circle_id}.png')


# TODO check if admin
@router.post('/approve_idea', response_model=OkResponse)
async def approve_idea(id: int) -> OkResponse:
    await IDEA.approve_idea(idea_id=id)
    return OkResponse()


@router.post('/add_skill', response_model=OkResponse)
async def add_skill(name: str) -> OkResponse:
    circle_id = str(uuid.uuid4())
    await generate_circles(text=name, circle_id=circle_id, color="red")

    await SKILL.add(name=name,
                    circle_id=circle_id)
    return OkResponse()


@router.post('/add_idea_tag', response_model=OkResponse)
async def add_idea_tag(name: str) -> OkResponse:
    circle_id = str(uuid.uuid4())
    await generate_circles(text=name, circle_id=circle_id, color="red")

    await IDEATAG.add(name=name,
                      circle_id=circle_id)
    return OkResponse()
