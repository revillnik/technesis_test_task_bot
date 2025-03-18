import asyncio
import re

import aiohttp
from bs4 import BeautifulSoup

from .requests import get_products


async def parsing_requests(session, db_dict: dict, result_dict: dict) -> dict:
    result_dict.setdefault("Errors", list())
    try:
        response = await session.get(url=db_dict["xpath"])
        soup = BeautifulSoup(await response.text(), "lxml")
        result_dict.setdefault(db_dict["title"], 0)
        if "haslestore.com" in db_dict["xpath"]:
            price = int(
                "".join(
                    i
                    for i in soup.find("span", class_=re.compile("priceNew")).text
                    if i in "0123456789"
                )
            )
            result_dict[db_dict["title"]] += price
        elif "amazingred.ru" in db_dict["xpath"]:
            price = int(soup.find("meta", property="product:price:amount")["content"])
            result_dict[db_dict["title"]] += price
    except:
        result_dict["Errors"].append(
            f'Ошибка title: {db_dict["title"]}, url: {db_dict["url"]}'
        )


async def gather_data() -> dict:
    """создаем серию задач tasks для асинхронного парсинга сайтов"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        result_dict = dict()
        list_db = await get_products()
        for i in list_db:
            task = asyncio.create_task(parsing_requests(session, i, result_dict))
            tasks.append(task)

        await asyncio.gather(*tasks)
        return result_dict
