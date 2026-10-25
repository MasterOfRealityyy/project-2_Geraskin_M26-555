from typing import Any
from pathlib import Path
from primitive_db.utils import load_table_data, save_table_data



def create_table(metadata: dict[str, Any], table_name: str, columns: list[str]) -> dict[str, Any]:
    if table_name in metadata:
        raise ValueError(f"Таблица с именем {table_name} уже существует")

    parsed_columns = []

    for column in columns:
        if ":" not in column:
            raise ValueError(f"Неверный формат столбца '{column}'")

        column_name, column_type = column.split(":", 1)
        column_type = column_type.strip().lower()


        if column_type not in ["int", "str", "bool"]:
            raise ValueError(f"Тип данных {column_type} некорректен")

        parsed_columns.append(f"{column_name.strip()}:{column_type}")

    final_columns = ["ID:int"] + parsed_columns

    metadata[table_name] = {"columns": final_columns}

    return metadata

def drop_table(metadata: dict[str, Any], table_name: str) -> dict[str, Any]:
    if table_name not in metadata:
        raise ValueError(f"Таблицы с именем '{table_name}' не существует")

    del metadata[table_name]

    filepath = Path("data").joinpath(table_name + ".json")
    if filepath.exists():
        filepath.unlink()

    return metadata

def insert(metadata: dict[str, Any], table_name: str, values: list[Any]) -> None:
    if table_name not in metadata:
        raise ValueError(f"Таблицы с именем '{table_name}' не существует")

    if len(values) != len(metadata[table_name]["columns"]) - 1:
        raise ValueError(f"Количество переданных значений не соответствует количеству столбцов таблицы")

    for value in values:
        if not isinstance(value, (int, str, bool)):
            raise ValueError(f"Тип данных значения {value} некорректен")

    table_data = load_table_data(table_name)

    if not table_data:
        new_id = 1
    else:
        new_id = max(value["ID"] for value in table_data) + 1

    col_names = [col.split(":")[0] for col in metadata[table_name]["columns"][1:]]

    new_row = {"ID": new_id}
    new_row.update(zip(col_names, values))

    table_data.append(new_row)

    save_table_data(table_name, table_data)

def select(table_data: list[dict[str, Any]], where_clause=None) -> list[dict[str, Any]]:
    if where_clause is None:
        return table_data

    table = [row for row in table_data if all(row.get(key) == value for key, value in where_clause.items())]
    return table


def update(table_data: list[dict[str, Any]], set_clause: dict[str, Any], where_clause: dict[str, Any] | None) -> list[dict[str, Any]]:

    if not where_clause:
        raise ValueError("Не указано условие where. Обновление всей таблицы запрещено.")

    for row in table_data:
        if all(row.get(key) == value for key, value in where_clause.items()):
            row.update(set_clause)

    return table_data


def delete(table_data: list[dict[str, Any]], where_clause: dict[str, Any]) -> list[dict[str, Any]]:
    if not where_clause:
        raise ValueError("Отсутствует условие. Удаление всей таблицы запрещено.")

    updated_table = [row for row in table_data if not all(row.get(key) == value for key, value in where_clause.items())]

    return updated_table










