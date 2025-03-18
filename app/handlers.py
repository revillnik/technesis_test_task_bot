import datetime
import os

import pandas as pd
from aiogram import Bot, F, Router
from aiogram.filters import CommandStart
from aiogram.types import ContentType, Document, Message

from .keyboards import keyboard
from .parsing import gather_data
from .requests import add_site, get_count_product

StaticFileDir = rf"{os.getcwd()}\static"

router = Router()


@router.message(F.content_type == ContentType.DOCUMENT)
async def cmd_start(message: Message, bot: Bot):
    if message.document.file_name.endswith(".xlsx"):
        FileDir = (
            StaticFileDir
            + rf'\{message.from_user.username}_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}'
        )
        File_path = rf"{FileDir}\{message.document.file_name}"
        os.mkdir(FileDir)

        await bot.download(
            message.document.file_id,
            File_path,
        )

        data_file = pd.read_excel(File_path)
        if tuple(data_file.head(1)) == (
            "title",
            "url",
            "xpath",
        ):
            for row in data_file.itertuples():
                await add_site(row.title, row.url, row.xpath)

            data_file_dict = data_file.to_dict()
            res_message = list()
            for i in range(len(data_file_dict["title"])):
                res_message.append(f"{i+1} запись:")
                for j in data_file_dict:
                    res_message.append(f"{j} = {data_file_dict[j][i]}")
            res_message = "\n".join(res_message)

            await message.answer(
                f"файл был загружен, его содержимое:\n{res_message}",
                disable_web_page_preview=True,
            )
        else:
            await message.reply(
                "Данный файл имеет недопустимые поля у записей, требуемый формат: title, url, xpath"
            )
    else:
        await message.reply(
            "Данный файл имеет неправильное расширение, требуется .xlsx"
        )


@router.message(F.text == "Средняя цена")
async def show_average_price(message: Message):
    result_dict = await gather_data()

    if result_dict:
        for i in list(result_dict.keys())[
            1::
        ]:  # берем [1::] чтобы не захватить ключ Errors
            count_product = await get_count_product(i)
            result_dict[i] = result_dict[i] / count_product
        result_message = "\n".join(
            [" = ".join(map(str, i)) for i in list(result_dict.items())[1:]]
        )

        if result_dict.get("Errors"):
            result_dict["Errors"] = "\n".join(result_dict["Errors"])
        else:
            result_dict["Errors"] = ""

        await message.answer(
            f"{"Средняя цена по товарам: \n"+result_message if result_message else ''}{"\n"+result_dict["Errors"]}"
        )

    else:
        await message.answer("Нет данных в базе")


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Отправьте боту excel файл в формате таблицы с полями title, url, xpath!",
        reply_markup=keyboard,
    )
