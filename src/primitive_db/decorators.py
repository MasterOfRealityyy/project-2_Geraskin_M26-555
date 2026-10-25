import functools
from typing import Callable, Any


def handle_db_errors(func: Callable) -> Callable:
    """Декоратор для перехвата и вывода ошибок базы данных.

    Перехватывает KeyError, ValueError и FileNotFoundError,
    выводит сообщение об ошибке и пробрасывает её дальше,
    чтобы вызывающая функция (engine.py) могла корректно обработать сбой.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, FileNotFoundError) as e:
            print(f"\n[Ошибка]: {e}")
            raise

    return wrapper


def confirm_action(action_name: str) -> Callable:
    """Фабрика декораторов для запроса подтверждения опасных действий.

    Пример: @confirm_action("удаление таблицы")
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            answer = input(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ')
            if answer.strip().lower() != "y":
                print("Операция отменена.")
                return None

            return func(*args, **kwargs)

        return wrapper

    return decorator


import time


def log_time(func: Callable) -> Callable:
    """Декоратор для замера времени выполнения функции."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:

        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        elapsed = end_time - start_time
        print(f"Функция {func.__name__} выполнялась за {elapsed:.3f} секунд")

        return result

    return wrapper