import shlex
from typing import Any

from primitive_db.decorators import handle_db_errors


@handle_db_errors
def convert_values(raw_values: list[str], columns_info: list[str]) -> list[Any]:
    converted = []

    for raw_val, col in zip(raw_values, columns_info[1:]):
        col_name, col_type = col.split(":")

        match col_type:
            case "int":
                try:
                    converted.append(int(raw_val))
                except ValueError:
                    raise ValueError(f"Для колонки '{col_name}' ожидалось число, "
                                     f"получено '{raw_val}'")
            case "bool":
                val_lower = str(raw_val).lower()
                converted.append(val_lower in ("true", "1", "yes"))
            case "str":
                converted.append(str(raw_val))
            case _:
                raise ValueError(f"Для колонки '{col_name}' "
                                 f"ожидалось число, получено '{raw_val}'")

    return converted

@handle_db_errors
def parse_where(where_str: str, columns_info: list[str]) -> dict[str, Any]:
    parts = shlex.split(where_str)

    if len(parts) != 3 or parts[1] != "=":
        raise ValueError("Неправильно введено условие where")

    column_name = parts[0]
    raw_value = parts[2]

    columns_dict = {col.split(":")[0]: col.split(":")[1] for col in columns_info}

    if column_name not in columns_dict:
        raise ValueError(f"Колонка '{column_name}' отсутствует в таблице")

    target_type = columns_dict[column_name]

    match target_type:
        case "int":
            try:
                return {column_name: int(raw_value)}
            except ValueError:
                raise ValueError(f"Ожидалось число, получено '{raw_value}'")
        case "bool":
            return {column_name: raw_value.lower() in ("true", "1", "yes")}
        case "str":
            return {column_name: str(raw_value)}
        case _:
            raise ValueError(f"Некорректный тип данных для колонки '{column_name}'")

@handle_db_errors
def parse_set(set_str: str, columns_info: list[str]) -> dict[str, Any]:
    return parse_where(set_str, columns_info)