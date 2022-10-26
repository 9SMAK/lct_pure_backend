from sqlalchemy import Boolean, Column, Integer, String, Float, CheckConstraint, PickleType
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Session, declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, " \
               f"name=\"{self.name}\")>" \
            # f"lvl={self.lvl})>" \
        # f"exp=\"{self.nick}\", " \
        # f"is_admin=\"{self.desc}\", " \
        # f"={self.lvl})>"