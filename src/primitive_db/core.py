from typing import Any


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
    return metadata










