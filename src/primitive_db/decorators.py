import functools
import time
from typing import Any, Callable


def handle_db_errors(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, FileNotFoundError) as e:
            print(f"\n[Ошибка]: {e}")
            raise

    return wrapper


def confirm_action(action_name: str) -> Callable:

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


def log_time(func: Callable) -> Callable:

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:

        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        elapsed = end_time - start_time
        print(f"Функция {func.__name__} выполнялась за {elapsed:.3f} секунд")

        return result

    return wrapper