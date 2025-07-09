from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class FilmCallback(CallbackData, prefix="film", sep=";"):
    id: int
    name: str


def films_keyboard_markup(films_list: list[dict]) -> InlineKeyboardBuilder:
    """Створює клавіатуру на основі отриманого списку фільмів"""

    builder = InlineKeyboardBuilder()
    builder.adjust(3, False)

    if not films_list or not isinstance(films_list, list):
        print("films_list пустий або має неправильний тип:", films_list)
        return builder.as_markup()

    for index, film_data in enumerate(films_list):
        if not isinstance(film_data, dict):
            continue  # Пропустити некоректні елементи

        if "name" not in film_data:
            continue  # Пропустити, якщо немає назви

        # Створюємо об'єкт CallbackData
        callback_data = FilmCallback(id=index, name=film_data["name"])

        # Додаємо кнопку до клавіатури
        builder.button(text=film_data["name"], callback_data=callback_data.pack())


    return builder.as_markup()  # Повернення клавіатури




