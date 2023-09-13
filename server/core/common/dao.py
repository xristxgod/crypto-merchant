import abc
from typing import TypeVar, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import Base, db_query_handler

ModelType = TypeVar('ModelType', bound=Base)


class RawCRUD(metaclass=abc.ABCMeta):
    model = ModelType
    db: str = 'default'

    @classmethod
    @db_query_handler(db=db)
    async def raw_get(cls, filters: list, session: AsyncSession):
        query = select(cls.model).where(*filters).limit(1)
        qs = await session.execute(query)
        return qs.scalar()

    @classmethod
    @db_query_handler(db=db)
    async def raw_filter(cls, filters: list, session: AsyncSession, order_by: Optional[list] = None,
                         limit: Optional[int] = None, offset: Optional[int] = None):
        query = select(cls.model).where(*filters)
        if filters:
            query = query.where(*filters)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        if order_by:
            query = query.order_by(*order_by)

        result = await session.execute(query)
        return result.scalars()

    @classmethod
    @db_query_handler(db=db)
    async def raw_create(cls, obj: model, session: AsyncSession, auto_commit: bool = True):
        session.add(obj)
        if auto_commit:
            await session.commit()
        return obj

    @classmethod
    @db_query_handler(db=db)
    async def raw_update(cls, obj: model, data: dict, session: AsyncSession, auto_commit: bool = True):
        for column, value in data.items():
            setattr(obj, column, value)
        session.add(obj)
        if auto_commit:
            await session.commit()
        return obj

    @classmethod
    @db_query_handler(db=db)
    async def raw_delete(cls, obj: model, session: AsyncSession, auto_commit: bool = True):
        await session.delete(obj)
        if auto_commit:
            await session.commit()


class BaseDAO(RawCRUD, metaclass=abc.ABCMeta):
    model: ModelType = NotImplemented

    class ObjectNotExist(Exception):
        pass

    @classmethod
    async def get_or_none(cls, filters: list, *, session: Optional[AsyncSession] = None) -> model:
        return await cls.raw_get(filters=filters, session=session)

    @classmethod
    async def all(cls, *, session: Optional[AsyncSession] = None) -> list[model]:
        return await cls.raw_filter(filters=[], session=session)

    @classmethod
    async def filter(cls, filters: list, *, limit: Optional[int] = None,
                     offset: Optional[int] = None, order_by: Optional[list] = None,
                     session: Optional[AsyncSession] = None) -> list[model]:
        return await cls.raw_filter(
            filters=filters,
            session=session,
            limit=limit,
            offset=offset,
            order_by=order_by,
        )

    @classmethod
    async def create(cls, obj: model, *, session: Optional[AsyncSession] = None, **kwargs) -> model:
        return await cls.raw_create(obj=obj, session=session, **kwargs)

    @classmethod
    async def update(cls, obj: model, data: dict, *, session: Optional[AsyncSession] = None, **kwargs) -> model:
        return await cls.raw_update(obj=obj, data=data, session=session, **kwargs)

    @classmethod
    async def delete(cls, obj: model, *, session: Optional[AsyncSession] = None, **kwargs):
        return await cls.raw_delete(obj=obj, session=session, **kwargs)
