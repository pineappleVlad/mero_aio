from sqlalchemy import Column, String, Integer, ForeignKey, Date, Table, Time, BigInteger
from sqlalchemy.orm import relationship
from .db_connection import Base


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    chat_id = Column(BigInteger, unique=True)
    city = Column(String)

class Advertisements(Base):
    __tablename__ = "advertisements"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    city_publish = Column(String)
    theme = Column(String)
    name = Column(String)
    photo = Column(String)
    date = Column(String)
    time = Column(String)
    members_count = Column(String)
    offer = Column(String)
    heading = Column(String)
    hashtags = Column(String)
    description = Column(String)
    address = Column(String)
    price = Column(String)
    url_registration = Column(String)
    tg_name_owner = Column(String)
    day_and_month = Column(String)

class CurrentSessions(Base):
    __tablename__ = "current_sessions"

    adv_id = Column(Integer, ForeignKey("advertisements.id"), nullable=True, primary_key=True)
    user_chat_id = Column(Integer, ForeignKey("users.chat_id"), nullable=False, primary_key=True)




