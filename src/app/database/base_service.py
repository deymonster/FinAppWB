from typing import List, Optional, Generic, TypeVar, Type

from sqlalchemy.orm import selectinload, class_mapper, ColumnProperty, RelationshipProperty, load_only

from app.database.models import Base
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select, update, delete

ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD)
        :param model: A SQLAlchemy model class
        """
        self.model = model

    async def get_all_with_related(self, async_session: async_sessionmaker[AsyncSession]):
        async with async_session() as session:
            stmt = select(self.model)
            model_mapper = class_mapper(self.model)
            for prop in model_mapper.iterate_properties:
                if isinstance(prop, ColumnProperty):
                    stmt = stmt.options(load_only(getattr(self.model, prop.key)))
                elif isinstance(prop, RelationshipProperty):
                    stmt = stmt.options(selectinload(getattr(self.model, prop.key)))
            result = await session.execute(stmt)
            objects = result.scalars().all()
            return objects


