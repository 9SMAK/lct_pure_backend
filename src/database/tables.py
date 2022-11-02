from typing import List

from sqlalchemy import Boolean, Column, Integer, String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Session, declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    login = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    avatar_id = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    birth = Column(Date)
    email = Column(String)
    phone = Column(String)
    telegram = Column(String)
    github = Column(String)

    def __repr__(self):
        return f"<User(id={self.id}, " \
               f"name=\"{self.name}\")>"


class Idea(Base):
    __tablename__ = "idea"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    title = Column(String, nullable=False, unique=True)
    description = Column(String)
    likes_count = Column(Integer)
    comments_count = Column(Integer)
    logo_id = Column(String, nullable=False)
    photo_ids = Column(ARRAY(String), nullable=False)
    video_id = Column(String)
    approved = Column(Boolean)

    def __repr__(self):
        return f"<Idea(id={self.id}, " \
               f"author=\"{self.name}\"" \
               f"name=\"{self.name}\")>"


class UserIdeaRelations(Base):
    __tablename__ = "user_idea_relations"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    idea_id = Column(Integer, ForeignKey("idea.id"), nullable=False)
    relation = Column(Integer, nullable=False)


class Comment(Base):
    __tablename__ = "comment"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    idea_id = Column(Integer, ForeignKey("idea.id"), nullable=False)
    reply_comment_id = Column(Integer)
    text = Column(String, nullable=False)


class Skill(Base):
    __tablename__ = "skill"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String, nullable=False)


class SkillToUser(Base):
    __tablename__ = "skill_to_user"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skill.id"), nullable=False)
    weight = Column(Integer, nullable=False)


class IdeaTag(Base):
    __tablename__ = "idea_tag"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String, nullable=False)


class IdeaTagToIdea(Base):
    __tablename__ = "idea_tag_to_idea"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    idea_id = Column(Integer, ForeignKey("idea.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("idea_tag.id"), nullable=False)
    weight = Column(Integer, nullable=False)

