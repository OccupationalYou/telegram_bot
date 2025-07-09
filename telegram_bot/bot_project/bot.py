import asyncio, sys, json, logging

from telegram_bot.bot_project.config import BOT_TOKEN as TOKEN

from aiogram.filters import StateFilter
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Bot, Dispatcher, html, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, URLInputFile, CallbackQuery
from telegram_bot.bot_logging.log import log_function_call
from telegram_bot.bot_project.commands import (
    SORT_BY_ALPHABET_COMMAND,
    RECOMMEND_MOVIE_COMMAND,
    RATE_MOVIE_COMMAND,
    EDIT_MOVIE_COMMAND,
    DELETE_MOVIE_COMMAND,
    SEARCH_MOVIE_COMMAND,
    FILTER_MOVIES_COMMAND,
    SHOW_FILMS_COMMAND,
    FILM_CREATE_COMMAND,
    SORT_BY_ACTOR_COMMAND,
    BOT_COMMANDS,
)

from telegram_bot.bot_project.data import get_films, add_film
from telegram_bot.bot_project.keyboards import films_keyboard_markup, FilmCallback
from telegram_bot.bot_project.models import Film

dp = Dispatcher()


class FilmForm(StatesGroup):
    name = State()
    description = State()
    rating = State()
    genre = State()
    actors = State()
    poster = State()


class MovieStates(StatesGroup):
    search_actor_query = State()
    search_query = State()
    filter_criteria = State()
    delete_query = State()
    edit_query = State()
    edit_description = State()


class MovieRatingStates(StatesGroup):
    rate_query = State()
    set_rating = State()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Стартова команда привітання
    """
    user = message.from_user
    name = user.first_name
    await message.answer(f"Вітаю {name} !")


@dp.message(SHOW_FILMS_COMMAND)
@log_function_call
async def show_films(message: Message) -> None:
    """
    Показує усі фільми
    """
    data = get_films()
    markup = films_keyboard_markup(films_list=data)
    await message.answer(
        f"Перелік фільмів. Натисніть на назву фільму для отримання деталей.",
        reply_markup=markup,
    )


@dp.message(FILM_CREATE_COMMAND)
@log_function_call
async def film_create(message: Message, state: FSMContext) -> None:
    """
    Створює новий фільм у json файл
    """
    await state.set_state(FilmForm.name)
    await message.answer(
        f"Введіть назву фільму.",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.name)
async def film_name(message: Message, state: FSMContext) -> None:

    await state.update_data(name=message.text)
    await state.set_state(FilmForm.description)
    await message.answer(
        f"Введіть опис фільму.",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.description)
async def film_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await state.set_state(FilmForm.rating)
    await message.answer(
        f"Вкажіть рейтинг фільму від 0 до 10.",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.rating)
async def film_rating(message: Message, state: FSMContext) -> None:
    await state.update_data(rating=float(message.text))
    await state.set_state(FilmForm.genre)
    await message.answer(
        f"Введіть жанр фільму.",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.genre)
async def film_genre(message: Message, state: FSMContext) -> None:
    await state.update_data(genre=message.text)
    await state.set_state(FilmForm.actors)
    await message.answer(
        text=f"Введіть акторів фільму через роздільник ', '\n"
             + html.bold("Обов'язкова кома та відступ після неї."),
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.actors)
async def film_actors(message: Message, state: FSMContext) -> None:
    await state.update_data(actors=[x for x in message.text.split(", ")])
    await state.set_state(FilmForm.poster)
    await message.answer(
        f"Введіть посилання на постер фільму.",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.poster)
async def film_poster(message: Message, state: FSMContext) -> None:
    data = await state.update_data(poster=message.text)
    film = Film(**data)
    add_film(film.model_dump())
    await state.clear()
    await message.answer(
        f"Фільм {film.name} успішно додано!",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.callback_query(FilmCallback.filter())
async def callb_film(callback: CallbackQuery, callback_data: FilmCallback) -> None:
    film_id = callback_data.id
    film_data = get_films(film_id=film_id)
    film = Film(**film_data)

    text = f"Фільм: {film.name}\n" \
           f"Опис: {film.description}\n" \
           f"Рейтинг: {film.rating}\n" \
           f"Жанр: {film.genre}\n" \
           f"Актори: {', '.join(film.actors)}\n"

    await callback.message.answer_photo(
        caption=text,
        photo=URLInputFile(
            film.poster,
            filename=f"{film.name}_poster.{film.poster.split('.')[-1]}"
        )
    )


@dp.message(FILTER_MOVIES_COMMAND)
@log_function_call
async def filter_movies(message: types.Message, state: FSMContext):
    """
    Фільтрує фільми за жанром
    """
    await message.answer("Введіть жанр для фільтрації:")
    await state.set_state(MovieStates.filter_criteria)


@dp.message(StateFilter(MovieStates.filter_criteria))
async def get_filter_criteria(message: types.Message, state: FSMContext):
    criteria = message.text.lower()
    films_list = get_films()

    filtered = [film for film in films_list if criteria in film["genre"].lower()]

    if filtered:
        for film in filtered:
            await message.answer(f"Знайдено: {film['name']} - {film['description']}")
    else:
        await message.answer("Фільм не знайдено за цими критеріями.")

    await state.clear()


@dp.message(SEARCH_MOVIE_COMMAND)
@log_function_call
async def search_movie(message: types.Message, state: FSMContext):
    """
    Шукає фільм за назвою
    """
    await message.answer("Введіть назву фільму для пошуку:")
    await state.set_state(MovieStates.search_query)


@dp.message(StateFilter(MovieStates.search_query))
async def get_search_query(message: types.Message, state: FSMContext):
    query = message.text.lower()
    films_list = get_films()

    results = [film for film in films_list if query in film["name"].lower()]

    if results:
        for film in results:
            await message.answer(f"Знайдено: {film['name']} - {film['description']}")
    else:
        await message.answer("Фільм не знайдено.")

    await state.clear()


@dp.message(DELETE_MOVIE_COMMAND)
@log_function_call
async def delete_movie(message: types.Message, state: FSMContext):
    """
    Видаляє фільм з json файлу
    """
    await message.answer("Введіть назву фільму, який бажаєте видалити:")
    await state.set_state(MovieStates.delete_query)


def delete_film_from_json(film_name):
    filename = "data.json"

    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    data["films"] = [film for film in data["films"] if film["name"].lower() != film_name.lower()]

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    return True


@dp.message(StateFilter(MovieStates.delete_query))
async def get_delete_query(message: types.Message, state: FSMContext):
    film_to_delete = message.text.lower()

    if delete_film_from_json(film_to_delete):
        await message.answer(f"Фільм '{film_to_delete}' успішно видалено зі списку.")
    else:
        await message.answer("Фільм не знайдено.")

    await state.clear()


@dp.message(EDIT_MOVIE_COMMAND)
@log_function_call
async def edit_movie(message: types.Message, state: FSMContext):
    """
    Редагую опис фільму
    """
    await message.answer("Введіть назву фільму, який бажаєте редагувати:")
    await state.set_state(MovieStates.edit_query)


@dp.message(StateFilter(MovieStates.edit_query))
async def get_edit_query(message: types.Message, state: FSMContext):
    film_to_edit = message.text.lower()
    films_list = get_films()

    filtered_films = [film for film in films_list if film["name"].lower() == film_to_edit]

    if filtered_films:
        await state.update_data(film_name=film_to_edit)
        await message.answer("Введіть новий опис фільму:")
        await state.set_state(MovieStates.edit_description)
    else:
        await message.answer("Фільм не знайдено.")
        await state.clear()


def update_film_description(film_name, new_description):
    filename = "data.json"

    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    for film in data["films"]:
        if film["name"].lower() == film_name.lower():
            film["description"] = new_description
            break
    else:
        return False

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    return True


@dp.message(StateFilter(MovieStates.edit_description))
async def get_new_description(message: types.Message, state: FSMContext):
    new_description = message.text
    data = await state.get_data()
    film_to_edit = data.get("film_name")

    if film_to_edit:
        if update_film_description(film_to_edit, new_description):
            await message.answer(f"Опис фільму '{film_to_edit}' успішно оновлено.")
        else:
            await message.answer("Фільм не знайдено для оновлення опису.")
    else:
        await message.answer("Сталася помилка, назву фільму не знайдено.")

    await state.clear()


@dp.message(RATE_MOVIE_COMMAND)
@log_function_call
async def rate_movie(message: types.Message, state: FSMContext):
    """
    Задає оцінку для фільму
    """
    await message.answer("Введіть назву фільму, щоб оцінити:")
    await state.set_state(MovieRatingStates.rate_query)


@dp.message(StateFilter(MovieRatingStates.rate_query))
async def get_rate_query(message: types.Message, state: FSMContext):
    film_to_rate = message.text.lower()
    films_list = get_films()  # Отримуємо список фільмів

    filtered_films = [film for film in films_list if film["name"].lower() == film_to_rate]

    if filtered_films:
        await state.update_data(film_name=film_to_rate)
        await message.answer("Введіть рейтинг від 1 до 10:")
        await state.set_state(MovieRatingStates.set_rating)
    else:
        await message.answer("Фільм не знайдено.")
        await state.clear()


def update_film_rating(film_name, new_rating):
    filename = "data.json"

    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    for film in data["films"]:
        if film["name"].lower() == film_name.lower():
            film["rating"] = new_rating
            break
    else:
        return False

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    return True


@dp.message(StateFilter(MovieRatingStates.set_rating))
async def set_rating(message: types.Message, state: FSMContext):
    data = await state.get_data()
    film_name = data["film_name"]

    try:
        rating = int(message.text)
        if 1 <= rating <= 10:
            if update_film_rating(film_name, rating):
                await message.answer(f"Рейтинг для '{film_name}' оновлено на {rating}.")
            else:
                await message.answer("Фільм не знайдено для оновлення.")
            await state.clear()
        else:
            await message.answer("Введіть рейтинг від 1 до 10.")
    except ValueError:
        await message.answer("Введіть число.")


@dp.message(RECOMMEND_MOVIE_COMMAND)
@log_function_call
async def recommend_movie(message: types.Message):
    """
    Показує фільм з найвищім рейтингом
    """
    recommended = get_best_rated_film()

    if recommended:
        await message.answer(
            f"Рекомендуємо переглянути: {recommended['name']} - {recommended['description']} (Рейтинг: {recommended['rating']})"
        )
    else:
        await message.answer("Немає фільмів з рейтингом для рекомендації.")


def get_best_rated_film():
    filename = "data.json"

    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    rated_films = [film for film in data["films"] if film.get("rating") is not None]

    return max(rated_films, key=lambda film: film["rating"]) if rated_films else None


@dp.message(SORT_BY_ALPHABET_COMMAND)
@log_function_call
async def sort_by_alphabet(message: types.Message, state: FSMContext):
    """
    Сортує список фільмів за алфавітом та виводить їх у телеграм-чат.
    """
    films = get_films()

    if not films:
        await message.answer("Список фільмів порожній.")
        return

    sorted_films = sorted(films, key=lambda film: film['name'].lower())

    output_text = "Список фільмів (відсортовано за алфавітом):\n"
    for film in sorted_films:
        output_text += f"- {film['name']}\n"

    max_message_length = 4096
    if len(output_text) > max_message_length:
        for i in range(0, len(output_text), max_message_length):
            await message.answer(output_text[i:i + max_message_length])
    else:
        await message.answer(output_text)

    await state.clear()


@dp.message(SORT_BY_ACTOR_COMMAND)
@log_function_call
async def search_by_actor(message: types.Message, state: FSMContext):
    """
    Запитує ім'я актора для пошуку.
    """
    await message.answer("Введіть ім'я актора для пошуку:")
    await state.set_state(MovieStates.search_actor_query)


@dp.message(StateFilter(MovieStates.search_actor_query))
async def get_search_actor_query(message: types.Message, state: FSMContext):
    query = message.text.lower()
    films = get_films()
    results = []
    for film in films:
        if "actors" in film and any(query in actor.lower() for actor in film["actors"]):
            results.append(film)

    if results:
        output_text = "Знайдено фільми з цим актором:\n"
        for film in results:
            output_text += f"- {film['name']} ({', '.join(film['actors'])})\n"
        # Розбиваємо великий текст на менші повідомлення, якщо потрібно
        max_message_length = 4096
        if len(output_text) > max_message_length:
            for i in range(0, len(output_text), max_message_length):
                await message.answer(output_text[i:i + max_message_length])
        else:
            await message.answer(output_text)
    else:
        await message.answer("Фільмів з таким актором не знайдено.")

    await state.clear()


async def main() -> None:
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        ),
    )
    await bot.set_my_commands(BOT_COMMANDS)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
