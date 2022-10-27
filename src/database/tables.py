from sqlalchemy import Boolean, Column, Integer, String, Float, CheckConstraint, PickleType, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Session, declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    login = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, " \
               f"name=\"{self.name}\")>"


class Idea(Base):
    __tablename__ = "idea"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    author = Column(Integer, ForeignKey("user.id"), nullable=False)
    title = Column(String, nullable=False, unique=True)
    description = Column(String)
    project_directory_id = Column(String, nullable=False)
    photo_id = Column(String, nullable=False)
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