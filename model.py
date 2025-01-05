from aiogram import Bot
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import String, select, or_
from dotenv import load_dotenv 
from os import getenv

import logging
import re


load_dotenv()
# , echo = True
engine = create_async_engine(url = getenv("DBROOT"))
async_session = async_sessionmaker(engine, expire_on_commit = True)
bot = Bot(token = getenv("TOKEN"))


class Base(AsyncAttrs, DeclarativeBase):
    pass

class Courses(Base):
    __tablename__ = 'Courses'

    # email: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    email: Mapped[str] = mapped_column(String(128), primary_key = True)
    phone: Mapped[str] = mapped_column(String(25))
    

    async def Create_User(email: str, phone_input: str, course: str) -> str | None:
        async with async_session() as session:
            try:
                phone = re.sub('\D', '', phone_input)

                if getenv("1COURSE_NAME") in course:
                    new_record = Courses(email = email, phone = phone)
                elif (getenv("2COURSE_NAME") in course) or (getenv("3COURSE_NAME") in course) or (getenv("UPDATE_NAME") in course):
                    new_record = Courses(email = email, phone = phone)
                elif getenv("4COURSE_NAME") in course:
                    new_record = Courses(email = email, phone = phone)
                elif getenv("5COURSE_NAME") in course:
                    new_record = Courses(email = email, phone = phone)

                # Применяем изменения
                session.add(new_record)
                await session.commit()

                if getenv("1COURSE_NAME") in course:
                    channel = await bot.create_chat_invite_link(chat_id = getenv('1COURSE_CHANNEL'), member_limit = 1) 
                    return channel.invite_link
                elif (getenv("2COURSE_NAME") in course) or (getenv("3COURSE_NAME") in course) or (getenv("UPDATE_NAME") in course):
                    channel = await bot.create_chat_invite_link(chat_id = getenv('2COURSE_CHANNEL'), member_limit = 1)
                    chat = await bot.create_chat_invite_link(chat_id = getenv('2COURSE_CHAT'), member_limit = 1)
                    return f"{channel.invite_link} | {chat.invite_link}"
                elif getenv("4COURSE_NAME") in course:
                    channel = await bot.create_chat_invite_link(chat_id = getenv('4COURSE_CHANNEL'), member_limit = 1) 
                    return channel.invite_link 
                elif getenv("5COURSE_NAME") in course:
                    channel = await bot.create_chat_invite_link(chat_id = getenv('5COURSE_CHANNEL'), member_limit = 1) 
                    return channel.invite_link  

            except Exception as e:
                await session.rollback()
                raise e
            
            finally:
                await session.close()

    async def Update_User(email: str, phone_input: str, course: str) -> str | None:
        """True - Операция выполнена успешно
        \nFalse - Пользователь отсутсвует в БД"""
        async with async_session() as session:
            try:
                phone = re.sub('\D', '', phone_input)
                user = await session.execute(select(Courses.email) # Получаем PK пользователя из бд по номеру или имени
                    .filter(or_(Courses.email == email, Courses.phone == phone[1:], Courses.phone == phone))) 
                upd = await session.get(Courses, user.unique().scalars().all()) # Получаем пользователя из бд

                if upd != None: # Проверка существует ли пользователь
                    # Обновляем значение в соответсвии с курсом
                    if getenv("1COURSE_NAME") in course:
                        channel = await bot.create_chat_invite_link(chat_id = getenv('1COURSE_CHANNEL'), member_limit = 1) 
                        return channel.invite_link
                    elif (getenv("2COURSE_NAME") in course) or (getenv("UPDATE_NAME") in course) or (getenv("3COURSE_NAME") in course):
                        channel = await bot.create_chat_invite_link(chat_id = getenv('2COURSE_CHANNEL'), member_limit = 1)
                        chat = await bot.create_chat_invite_link(chat_id = getenv('2COURSE_CHAT'), member_limit = 1)
                        return f"{channel.invite_link} | {chat.invite_link}"
                    elif getenv("4COURSE_NAME") in course:
                        channel = await bot.create_chat_invite_link(chat_id = getenv('4COURSE_CHANNEL'), member_limit = 1) 
                        return channel.invite_link 
                    elif getenv("5COURSE_NAME") in course:
                        channel = await bot.create_chat_invite_link(chat_id = getenv('5COURSE_CHANNEL'), member_limit = 1) 
                        return channel.invite_link   
                    else:
                        return None
                else:
                    return None
                
            except Exception as e:
                await session.rollback()
                logging.exception(f"{e}")
                return None
            
            finally:
                await session.close()
                

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)