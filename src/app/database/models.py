import asyncio
from typing import Optional

from sqlalchemy import BigInteger, Column, String, Date, ForeignKey, inspect, select, exists
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession

from config import SQLALCHEMY_URL, ADDRESSES, ROLES, OPERATION_TYPE, REQUEST_STATUS, USERS

engine = create_async_engine(SQLALCHEMY_URL, echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class UserRole(Base):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)


class OperationType(Base):
    __tablename__ = 'operation_types'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)


class Address(Base):
    __tablename__ = 'addresses'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)


class RequestStatus(Base):
    __tablename__ = 'request_status'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)


class User(Base):
    """ Model User """
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    tg_id: Mapped[BigInteger] = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column()
    middle_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()

    role_id: Mapped[Optional[int]] = mapped_column(ForeignKey('roles.id'), nullable=True)
    role = relationship('UserRole')
    confirmed_status: Mapped[bool] = mapped_column()

    requests = relationship('Request', back_populates='user')

    def __repr__(self):
        return f'<User {self.name}>'


class Request(Base):
    __tablename__ = 'requests'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    date: Mapped[Date] = mapped_column(Date)

    type_id: Mapped[int] = mapped_column(ForeignKey('operation_types.id'), nullable=False)
    type = relationship('OperationType')

    status_id: Mapped[int] = mapped_column(ForeignKey('request_status.id'), nullable=False)
    status = relationship('RequestStatus')

    address_id: Mapped[int] = mapped_column(ForeignKey('addresses.id'), nullable=False)
    address = relationship('Address')

    user = relationship('User', back_populates='requests')
    summ: Mapped[int] = mapped_column()
    description: Mapped[str] = mapped_column()

    media = relationship('Media', back_populates='request')

    purpose: Mapped[str] = mapped_column()
    comment: Mapped[str] = mapped_column(nullable=True)


class Media(Base):
    __tablename__ = 'media'
    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey('requests.id'), nullable=True)
    file_id: Mapped[str] = mapped_column()
    request = relationship('Request', back_populates='media')


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        async with AsyncSession(engine) as session:


            if not await session.scalar(select(exists().where(UserRole.id.isnot(None)))):
                for role_name in ROLES:
                    role = UserRole(name=role_name)
                    session.add(role)

            if not await session.scalar(select(exists().where(OperationType.id.isnot(None)))):
                for operation_name in OPERATION_TYPE:
                    operation_type = OperationType(name=operation_name)
                    session.add(operation_type)

            if not await session.scalar(select(exists().where(Address.id.isnot(None)))):
                for address in ADDRESSES:
                    address = Address(name=address)
                    session.add(address)

            if not await session.scalar(select(exists().where(RequestStatus.id.isnot(None)))):
                for status in REQUEST_STATUS:
                    status = RequestStatus(name=status)
                    session.add(status)

            admin_role = await session.execute(select(UserRole.id).filter_by(id=1))
            admin_role = admin_role.scalar_one()
            if not await session.scalar(select(exists().where(User.id.isnot(None)))):
                for user_data in USERS:
                    user = User(
                        tg_id=user_data["tg_id"],
                        name=user_data["name"],
                        middle_name=user_data["middle_name"],
                        last_name=user_data["last_name"],
                        confirmed_status=user_data.get("confirmed_status"),
                        role_id=admin_role
                    )
                    session.add(user)

            await session.commit()
