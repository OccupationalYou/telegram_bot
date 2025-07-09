from aiogram.filters import Command
from aiogram.types.bot_command import BotCommand


SHOW_FILMS_COMMAND = Command('show_films')
FILM_CREATE_COMMAND = Command("create_film")
FILTER_MOVIES_COMMAND = Command("filter_movies")
SEARCH_MOVIE_COMMAND = Command("search_movie")
DELETE_MOVIE_COMMAND = Command("delete_movie")
EDIT_MOVIE_COMMAND = Command("edit_movie")
RATE_MOVIE_COMMAND = Command("rate_movie")
RECOMMEND_MOVIE_COMMAND = Command("recommend_movie")
SORT_BY_ALPHABET_COMMAND = Command("sort_by_alphabet")
SORT_BY_ACTOR_COMMAND = Command("sort_by_actor")


BOT_COMMANDS = [
    BotCommand(command="show_films", description="Перегляд списку фільмів"),
    BotCommand(command="create_film", description="Додати новий фільм"),
    BotCommand(command="filter_movies", description="Вілфільтрувати за жанром"),
    BotCommand(command="search_movie", description="Знайти фільм зі списку"),
    BotCommand(command="delete_movie", description="Видалити фільм за списку"),
    BotCommand(command="edit_movie", description="Змінити опис фільму"),
    BotCommand(command="rate_movie", description="Оцінити фільм"),
    BotCommand(command="recommend_movie", description="Рекомендації"),
    BotCommand(command="sort_by_alphabet", description="Сортувати за алфавітом"),
    BotCommand(command="sort_by_actor", description="Сортувати за актором")

]
