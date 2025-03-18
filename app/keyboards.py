from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Средняя цена")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Узнать среднюю цену по каждому товару",
)
