import logging
from typing import List, Dict

from pydantic import BaseModel
from sqlalchemy import select, delete, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.ddl import DropTable, CreateTable

import src.database.schemas as schemas
from .database import DATABASE
from sqlalchemy.ext.asyncio import AsyncEngine

from src.database.tables import User, UserIdeaRelations, Comment, Idea

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Repository:
    _table = None
    _pydantic_schema = BaseModel

    def __init__(self, engine: AsyncEngine, sessionmaker):
        self._engine = engine
        self._sessionmaker = sessionmaker

    async def create_repository(self):
        async with self._engine.begin() as conn:
            await conn.execute(CreateTable(self._table.__table__, if_not_exists=True))

    async def delete_repository(self):
        async with self._engine.begin() as conn:
            await conn.execute(DropTable(self._table.__table__, if_exists=True))

    async def get_all(self) -> List[_pydantic_schema]:
        async with self._sessionmaker() as session:
            session: AsyncSession
            # async with session.begin(): - this for massive selects?
            statement = select(self._table)
            result = await session.execute(statement)
            return self._pydantic_convert_list(result)

    async def get_by_id(self, id: int) -> _pydantic_schema:
        async with self._sessionmaker() as session:
            statement = select(self._table).filter(self._table.id == id)
            res = (await session.execute(statement)).first()
            return self._pydantic_convert_object(res)

    # TODO add check if already exists
    async def add(self, **kwargs) -> bool:
        async with self._sessionmaker() as session:
            try:
                session: AsyncSession
                new_elem = self._table(**kwargs)
                session.add(new_elem)
                await session.commit()
                await session.refresh(new_elem)
                return True
            except IntegrityError:
                await session.rollback()
                return False

    async def update_values(self, statement):
        async with self._sessionmaker() as session:
            try:
                await session.execute(statement)
                await session.commit()
                await session.flush()
            except IntegrityError:
                await session.rollback()
                return False
        return True

    def _pydantic_convert_object(self, sqlalchemy_object):
        return self._pydantic_schema.from_orm(sqlalchemy_object[0])

    def _pydantic_convert_list(self, sqlalchemy_list):
        return [self._pydantic_schema.from_orm(x[self._table.__name__]) for x in sqlalchemy_list]


class UserRepository(Repository):
    _table = User
    _pydantic_schema = schemas.User

    async def get_by_login(self, login: str) -> _pydantic_schema:
        async with self._sessionmaker() as session:
            statement = select(self._table).filter(self._table.login == login)
            res = (await session.execute(statement)).first()
            return self._pydantic_convert_object(res)

    async def edit_profile(self, user_id, **kwargs):
        statement = update(self._table).where(
            self._table.id == user_id
        ).values(kwargs)
        await self.update_values(statement)
        return True


USER = UserRepository(DATABASE.get_engine(), DATABASE.get_sessionmaker())


class IdeaRepository(Repository):
    _table = Idea
    _pydantic_schema = schemas.Idea

    async def get_approved(self):
        async with self._sessionmaker() as session:
            statement = select(self._table).filter(self._table.approved == True)
            res = (await session.execute(statement))
            return self._pydantic_convert_list(res)

    async def get_my_ideas(self, user_id):
        async with self._sessionmaker() as session:
            statement = select(self._table).filter(self._table.author == user_id)
            res = (await session.execute(statement))
            return self._pydantic_convert_list(res)

    async def safe_increase_like(self, idea_id: int):
        statement = update(self._table).where(
            self._table.id == idea_id
        ).values(likes_count=self._table.likes_count + 1)
        await self.update_values(statement)

    async def safe_increase_comments(self, idea_id: int):
        statement = update(self._table).where(
            self._table.id == idea_id
        ).values(comments_count=self._table.comments_count + 1)
        await self.update_values(statement)

    async def approve_idea(self, idea_id: int):
        statement = update(self._table).where(
            self._table.id == idea_id
        ).values(approved=True)
        await self.update_values(statement)

    async def edit_idea(self, idea_id, **kwargs):
        statement = update(self._table).where(
            self._table.id == idea_id
        ).values(kwargs)
        await self.update_values(statement)
        return True


IDEA = IdeaRepository(DATABASE.get_engine(), DATABASE.get_sessionmaker())


class UserIdeaRelationsRepository(Repository):
    _table = UserIdeaRelations
    _pydantic_schema = schemas.UserIdeaRelations

    async def get_relation_by_user_id(self, user_id: str, relation: int) -> _pydantic_schema:
        async with self._sessionmaker() as session:
            statement = select(self._table).filter(self._table.user_id == user_id, self._table.relation == relation)
            res = (await session.execute(statement))
            return self._pydantic_convert_list(res)

    async def get_all_by_user_id(self, user_id: str) -> _pydantic_schema:
        async with self._sessionmaker() as session:
            statement = select(self._table).filter(self._table.user_id == user_id)
            res = (await session.execute(statement))
            return self._pydantic_convert_list(res)


USERIDEARELATIONS = UserIdeaRelationsRepository(DATABASE.get_engine(), DATABASE.get_sessionmaker())


class CommentRepository(Repository):
    _table = Comment
    _pydantic_schema = schemas.Comment

    async def get_comments_by_id(self, idea_id):
        async with self._sessionmaker() as session:
            statement = select(self._table).filter(self._table.idea_id == idea_id)
            res = (await session.execute(statement))
            return self._pydantic_convert_list(res)


COMMENT = CommentRepository(DATABASE.get_engine(), DATABASE.get_sessionmaker())
