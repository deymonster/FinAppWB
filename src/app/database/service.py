import logging
import pdb

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.orm import selectinload

import config
from app.database.models import User, Request, Media, async_session, UserRole, OperationType, Address, RequestStatus
from sqlalchemy import select, update, delete
from app.database.base_service import CRUDBase
from app.notify.notify_utils import notify_user_test


async def get_users():
    async with async_session() as session:
        stmt = select(User).options(selectinload(User.role))

        result = await session.execute(stmt)
        return result.scalars().all()


async def get_user_by_id(user_id: int):
    async with async_session() as session:
        stmt = select(User).options(selectinload(User.role)).where(User.id == user_id)
        result = await session.execute(stmt)
        return result.scalars().first()


async def get_director():
    async with async_session() as session:
        stmt = select(User).options(selectinload(User.role)).where(User.role.id == config.DIRECTOR_ROLE_ID)
        result = await session.execute(stmt)
        return result.scalars().first()


async def get_user_by_tg_id(tg_id: int):
    async with async_session() as session:
        stmt = select(User).options(selectinload(User.role)).where(User.tg_id == tg_id)
        result = await session.execute(stmt)
        return result.scalars().first()


async def add_user(tg_id: int, name: str, middle_name: str, last_name: str, role_id: int):
    """ Save model User to DB
    :param tg_id: Telegram ID
    :param name: User name
    :param middle_name: User middle name
    :param last_name: User last name
    :param role_id: Role ID of user
    """
    user = User(tg_id=tg_id, name=name,
                middle_name=middle_name,
                last_name=last_name,
                role_id=role_id,
                confirmed_status=False)
    # pdb.set_trace()
    async with async_session() as session:
        async with session.begin():
            session.add(user)


async def delete_user_by_id(user_id: int):
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            stmt = delete(User).where(User.id == user_id)
            await session.execute(stmt)
            await session.commit()


async def update_user(user_id: int, user_data: dict):
    async with async_session() as session:
        async with session.begin():
            user = await session.get(User, user_id)
            if user:
                previous_status = user.confirmed_status
                stmt = (
                    update(User).where(User.id == user_id).values(**user_data)
                )
                await session.execute(stmt)
                new_status = user.confirmed_status
                if new_status and new_status != previous_status:
                    await notify_user_test(user.tg_id, config.REGISTRATION)


async def get_all_media_by_request_id(request_id: int):
    async with async_session() as session:
        stmt = select(Media).where(Media.request_id == request_id)
        result = await session.execute(stmt)
        return result.scalars().all()


async def add_media(file_id):
    """Function to add media

    :param file_id: str - file_id
    :return
    """
    media = Media(file_id=file_id)
    async with async_session() as session:
        async with session.begin():
            session.add(media)
            await session.flush()
            return media.id


async def update_media(media_id: int, request_id: int):
    """Function to update media with request_id

    :param media_id: int
    :param request_id: int
    """
    async with async_session() as session:
        async with session.begin():
            media = await session.get(Media, media_id)
            if media:
                media.request_id = request_id


async def get_roles():
    async with async_session() as session:
        stmt = select(UserRole)
        result = await session.execute(stmt)
        return result.scalars().all()


async def get_role_by_id(role_id: int):
    async with async_session() as session:
        stmt = select(UserRole).where(UserRole.id == role_id)
        result = await session.execute(stmt)
        return result.scalars().first()


async def get_request_by_id(request_id: int):
    async with async_session() as session:
        stmt = select(Request).options(selectinload(Request.type),
                                       selectinload(Request.status),
                                       selectinload(Request.address),
                                       selectinload(Request.user),
                                       selectinload(Request.media)).\
                where(Request.id == request_id)
        result = await session.execute(stmt)
        return result.scalars().first()


async def get_requests_by_user_id(user_id: int):
    async with async_session() as session:
        stmt = select(Request).options(selectinload(Request.type),
                                       selectinload(Request.address),
                                       selectinload(Request.media),
                                       selectinload(Request.user),
                                       selectinload(Request.status)).\
            where(Request.user_id == user_id)
        result = await session.execute(stmt)
        return result.scalars().all()


async def get_all_requests():
    async with async_session() as session:
        # pdb.set_trace()
        stmt = select(Request).options(selectinload(Request.type),
                                       selectinload(Request.address),
                                       selectinload(Request.media),
                                       selectinload(Request.user),
                                       selectinload(Request.status))
        result = await session.execute(stmt)
        return result.scalars().all()


async def get_requests_with_status(status_id: int):
    async with async_session() as session:
        stmt = select(Request).options(selectinload(Request.type),
                                       selectinload(Request.address),
                                       selectinload(Request.media),
                                       selectinload(Request.user),
                                       selectinload(Request.status)).\
            where(Request.status_id == status_id)
        result = await session.execute(stmt)
        return result.scalars().all()


async def add_request_with_user_id(request_data: dict):
    request = Request(**request_data)
    async with async_session() as session:
        async with session.begin():
            session.add(request)
            await session.flush()
    return request.id


async def delete_request(request_id: int):
    async with async_session() as session:
        request = await session.get(Request, request_id)
        if request:
            stmt = delete(Request).where(Request.id == request_id)
            await session.execute(stmt)
            await session.commit()


async def get_all_operations():
    async with async_session() as session:
        stmt = select(OperationType)
        result = await session.execute(stmt)
        return result.scalars().all()


async def get_operation_by_id(operation_id: int):
    async with async_session() as session:
        stmt = select(OperationType).where(OperationType.id == operation_id)
        result = await session.execute(stmt)
        return result.scalars().first()


async def update_request(request_id: int, request_data: dict):
    async with async_session() as session:
        async with session.begin():
            request = await session.get(Request, request_id)
            # pdb.set_trace()
            if request:
                stmt = (
                    update(Request).where(Request.id == request_id).values(**request_data)
                )
                await session.execute(stmt)

async def get_all_addresses():
    async with async_session() as session:
        stmt = select(Address)
        result = await session.execute(stmt)
        return result.scalars().all()


async def get_address_by_id(address_id: int):
    async with async_session() as session:
        stmt = select(Address).where(Address.id == address_id)
        result = await session.execute(stmt)
        return result.scalars().first()


async def get_type_request(request_id: int):
    async with async_session() as session:
        stmt = select(Request, OperationType).join(OperationType).where(Request.id == request_id)
        result = await session.execute(stmt)
        record = result.fetchone()
        if record:
            request, operation_type = record
            return operation_type.name
    return None


async def get_user_role(tg_id: int):
    """ Используя TG ID получаем пользователя из БД и потом его же роль
    Если роль есть возращаем ее название или ничего
    """
    async with async_session() as session:
        stmt = (
            select(User, UserRole)
            .join(UserRole, User.role_id == UserRole.id)
            .where(User.tg_id == tg_id)
        )
        # stmt = (
        #     select(UserRole)
        #     .join(User)
        #     .where(User.tg_id == tg_id)
        #     .where(User.role_id == UserRole.id)
        # )
        # pdb.set_trace()
        result = await session.execute(stmt)
        record = result.fetchone()
        if record:
            user, role = record
            return role
        # if record:
        #     return record[0]
    return None


async def is_admin(tg_id: int):
    """ Function to detect admin rights"""
    async with async_session() as session:
        stmt = (
            select(User, UserRole).
            join(UserRole, User.role_id == UserRole.id)
            .where(User.tg_id == tg_id)
        )
        result = await session.execute(stmt)
        record = result.fetchone()
        if record:
            user, role = record
            if role.name == "Администратор":
                return True
            else:
                return False
        return False


class CRUDRequest(CRUDBase[Request]):
    def get_all_request_with_related(self, session: async_sessionmaker[AsyncSession]):
        requests = super().get_all_with_related(async_session=session)
        return requests


crud_request = CRUDRequest(Request)
