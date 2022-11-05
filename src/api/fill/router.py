import os
import random
import shutil

from faker import Faker

from src.api.auth.authentication import get_password_hash
from src.api.user.schemas import EditProfileRequest
from src.database.repositories import USER

import uuid
import json
from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, Body

from src.api.helpers import async_upload_file, remove_file
from src.api.idea.schemas import TeamRequest
from src.database.repositories import USERIDEARELATIONS, IDEA, USER, SKILLTOUSER, COMMENT, TAGTOIDEA
from src.api.auth.authentication import AuthenticatedUser, get_current_user
from src.api.schemas import OkResponse
from src.config import RelationsTypes
from src.api.user.schemas import EditProfileRequest, EditSkillsRequest
from src.database.schemas import Idea, SkillToUser, User

router = APIRouter(prefix="/fake", tags=["Faker"])
faker = Faker(["ru_RU"])


async def fake_users(count):
    cur_id = 2
    while cur_id <= count + 1:
        try:
            profile = faker.simple_profile()
            profile2 = faker.simple_profile()
            profile3 = faker.simple_profile()

            await USER.add(
                login=profile["username"],
                hashed_password=get_password_hash(f'{profile["username"]}1'),
            )

            edit_info = EditProfileRequest(
                name=profile["name"],
                email=profile["mail"],
                telegram=profile2["username"],
                github=profile3["username"]
            )

            await USER.edit_profile(cur_id, **edit_info.dict(exclude_none=True))
            cur_id += 1
        except Exception as e:
            pass


async def fake_ideas():
    with open('src/api/fill/ideas.json', 'r', encoding='utf-8') as f:
        ideas = json.loads(f.read())

    users = await USER.get_all()
    for idx, idea in enumerate(ideas):

        if idx + 1 in [1, 3, 9, 16, 18, 21, 24, 28, 29, 30]:
            continue

        try:
            random_user = random.randint(1, len(users) - 1)

            logo_id = str(uuid.uuid4())
            video_id = str(uuid.uuid4()) if f'{idx}.mp4' in os.listdir('src/api/fill/videos') else None
            photos = (str(uuid.uuid4()))

            if f'{idx + 1}.jpg' in os.listdir('src/api/fill/images'):
                photo = f'src/api/fill/images/{idx}.jpg'
            else:
                photo = f'src/api/fill/images/{idx}.png'

            shutil.copyfile(photo, f'src/files/{photos}.jpg')

            if video_id:
                shutil.copyfile(f'src/api/fill/videos/{idx}.mp4', f'src/files/{video_id}.mp4')

            idea = await IDEA.add(
                title=idea["name"],
                description=idea["description"],
                author_id=random_user,
                likes_count=0,
                comments_count=0,
                logo_id=logo_id,
                photo_ids=[photos],
                video_id=video_id,
                approved=True
            )
        except Exception as e:
            pass


async def make_relation(users, ideas, type):
    for i in range(70):
        random_user = random.randint(1, len(users) - 1)
        random_idea = random.randint(1, len(ideas) - 1)
        like_exist = await USERIDEARELATIONS.get_relation_by_user_id(user_id=random_user,
                                                                     idea_id=random_idea,
                                                                     relation=RelationsTypes.like)

        dislike_exist = await USERIDEARELATIONS.get_relation_by_user_id(user_id=random_user,
                                                                        idea_id=random_idea,
                                                                        relation=RelationsTypes.dislike)

        if like_exist or dislike_exist:
            continue

        relation = await USERIDEARELATIONS.add(
            user_id=random_user,
            idea_id=random_idea,
            relation=type
        )

        if type == RelationsTypes.like:
            await IDEA.safe_increase_like(
                idea_id=random_idea
            )


async def fake_relations():
    users = await USER.get_all()
    ideas = await IDEA.get_all()
    await make_relation(users, ideas, RelationsTypes.like)
    await make_relation(users, ideas, RelationsTypes.dislike)
    # await make_relation(users, ideas, RelationsTypes.request_membership)
    # await make_relation(users, ideas, RelationsTypes.member)


@router.post('/fake_db', response_model=OkResponse)
async def fill_users(users_count: int):
    await USERIDEARELATIONS.delete_repository()
    await SKILLTOUSER.delete_repository()
    await TAGTOIDEA.delete_repository()
    await COMMENT.delete_repository()
    await IDEA.delete_repository()
    await USER.delete_repository()

    await USER.create_repository()
    await IDEA.create_repository()
    await SKILLTOUSER.create_repository()
    await TAGTOIDEA.create_repository()
    await COMMENT.create_repository()
    await USERIDEARELATIONS.create_repository()

    await USER.add(
        login='sam',
        hashed_password=get_password_hash(f'123'),
    )

    edit_info = EditProfileRequest(
        telegram='akanolifer',
    )

    await USER.edit_profile(1, **edit_info.dict(exclude_none=True))

    await fake_users(users_count)
    await fake_ideas()
    await fake_relations()

    return OkResponse()
