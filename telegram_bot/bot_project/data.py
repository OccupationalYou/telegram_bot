import json

def get_films(file_path: str = "data.json", film_id: int | None = None) -> list[dict] | dict:
    with open(file_path, "r", encoding="utf-8") as fp:
        data = json.load(fp)

        # Переконайся, що data містить ключ "films"
        if "films" in data and isinstance(data["films"], list):
            films = data["films"]
        else:
            films = []  # Повертаємо порожній список, якщо структура неправильна

        if film_id is not None and film_id < len(films):
            return films[film_id]
        return films


def add_film(film: dict, file_path: str = "data.json"):
    data = get_films(file_path=file_path, film_id=None)

    if isinstance(data, list):  # Якщо data - список, загорнімо його в {"films": ...}
        films = data
    elif isinstance(data, dict) and "films" in data:  # Якщо це словник і є ключ "films"
        films = data["films"]
    else:
        films = []  # Якщо структура неправильна, створюємо новий список

    films.append(film)

    with open(file_path, "w", encoding="utf-8") as fp:
        json.dump(
            {"films": films},  # Додаємо ключ "films"
            fp,
            indent=4,
            ensure_ascii=False
        )

