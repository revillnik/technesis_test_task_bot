from sqlalchemy import func, select

from .database.models import Site, async_session


async def add_site(title: str, url: str, xpath: str):
    async with async_session() as session:
        record = await session.scalar(
            select(Site).where(
                Site.title == title, Site.url == url, Site.xpath == xpath
            )
        )
        if not record:
            session.add(Site(title=title, url=url, xpath=xpath))
            await session.commit()


async def get_products() -> list[dict]:
    async with async_session() as session:
        records = await session.scalars(select(Site))
        list_db = []
        for record in records:
            list_db.append(
                {"title": record.title, "url": record.url, "xpath": record.xpath}
            )
        return list_db


async def get_count_product(
    title: str,
) -> int:
    async with async_session() as session:
        query = select(func.count()).where(Site.title == title)  #
        db_objects = await session.execute(query)
        return db_objects.scalars().first()
