import json
from pathlib import Path
from typing import Any, Callable

def load_metadata(filepath: str) -> dict:
    try:
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_metadata(filepath: str, data: dict) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_table_data(table_name: str) -> list:
    filepath = Path("data").joinpath(table_name + ".json")
    try:
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_table_data(table_name: str, data: list) -> None:
    Path("data").mkdir(exist_ok=True)
    filepath = Path("data").joinpath(table_name + ".json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)



def create_cacher() -> Callable[[str, Callable[[], Any]], Any]:
    """Создает функцию для кэширования результатов.

    Возвращает функцию cache_result(key, value_func), которая хранит
    вычисленные значения в замыкании (словаре).
    """
    cache = {}

    def cache_result(key: str, value_func: Callable[[], Any]) -> Any:
        if key in cache:
            return cache[key]

        result = value_func()
        cache[key] = result
        return result

    return cache_result
