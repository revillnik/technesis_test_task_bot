from sqlalchemy import func, select

from .database.models import Site, async_session


async def add_site(
    title: str, url: str, xpath: str
):  # создаем запрос на добавление в базу данных записей из файла
    async with async_session() as session:
        record = await session.scalar(
            select(Site).where(
                Site.title == title, Site.url == url, Site.xpath == xpath
            )
        )  # проверяем, есть ли уже такие записи, если есть, не допускаю дупликатов (решил по всем полям проверять)
        if not record:
            session.add(
                Site(title=title, url=url, xpath=xpath)
            )  # добавляю уникальные записи
            await session.commit()


async def get_products() -> list[dict]:
    async with async_session() as session:  # получаем список всех записей из базы данных
        records = await session.scalars(select(Site))
        list_db = []
        for i in records:
            list_db.append({"title": i.title, "url": i.url, "xpath": i.xpath})
        return list_db


async def get_count_product(
    title: str,
) -> int:  # получаем число записей определенного продукта
    async with async_session() as session:
        query = select(func.count()).where(
            Site.title == title
        )  # получаем число записей с одинаковым названием
        db_objects = await session.execute(query)
        records_count = db_objects.scalars().first()
        return records_count
