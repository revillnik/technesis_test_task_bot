import datetime
import os

import pandas as pd
from aiogram import Bot, F, Router
from aiogram.filters import CommandStart
from aiogram.types import ContentType, Document, Message

from .keyboards import keyboard
from .parsing import gather_data
from .requests import add_site, get_count_product

StaticFileDir = (
    rf"{os.getcwd()}\static"  # формирую стандартный путь для статических файлов
)

router = Router()


@router.message(F.content_type == ContentType.DOCUMENT)
async def cmd_start(message: Message, bot: Bot):
    if message.document.file_name.endswith(".xlsx"):
        """формируем директории для excel файлов, причем необходимо,
        чтобы сохранялись все версии файлов, именно поэтому ставлю время вплоть до секунд
        """
        FileDir = (
            StaticFileDir
            + rf'\{message.from_user.username}_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}'
        )  # формирую директорию для файлов
        File_path = (
            rf"{FileDir}\{message.document.file_name}"  # формирую путь для файла
        )
        os.mkdir(FileDir)  # создаем директорию для каждого файла
        await bot.download(
            message.document.file_id,
            File_path,
        )  # бот скачивает excel таблицу, которую впоследствии будем парсить

        data_file = pd.read_excel(File_path)  # читаю загруженный файл с сайтами
        if tuple(data_file.head(1)) == (
            "title",
            "url",
            "xpath",
        ):  # проверяем соответствие полей
            for i in data_file.itertuples():  # перебираю содержимое файла построчно
                await add_site(
                    i.title, i.url, i.xpath
                )  # записываю построчно содержимое файла в Базу данных

            """ тут блок кода для удобного вывода содержимого excel файла """
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
            )  # выводим пользователю содрежимое файла
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
            count_product = await get_count_product(
                i
            )  # получаем число продуктов с данным названием
            result_dict[i] = (
                result_dict[i] / count_product
            )  # получаем среднюю стоимость продукта
        result_message = "\n".join(
            [" = ".join(map(str, i)) for i in list(result_dict.items())[1:]]
        )  # формируем сообщение со средней стоимостью всех продуктов
        if result_dict.get(
            "Errors"
        ):  # проверяем наличие ошибок и формируем сообщение для них
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
