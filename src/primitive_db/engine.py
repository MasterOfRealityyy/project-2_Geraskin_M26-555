import shlex

from prettytable import PrettyTable

from primitive_db.core import create_table, delete, drop_table, insert, select, update
from primitive_db.decorators import create_cacher
from primitive_db.parser import convert_values, parse_set, parse_where
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help() -> None:
    """Выводит справочную информацию по командам."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\n***Операции с данными***")
    print("Функции:")
    print("<command> insert into <имя_таблицы> "
          "values (<значение1>, <значение2>, ...) - создать запись")
    print("<command> select from <имя_таблицы> "
          "where <столбец> = <значение> - прочитать записи по условию")
    print("<command> select from <имя_таблицы> - прочитать все записи")
    print("<command> update <имя_таблицы> set <столбец> = <новое_значение> "
          "where <столбец_условия> = <значение_условия> - обновить запись")
    print("<command> delete from <имя_таблицы> "
          "where <столбец> = <значение> - удалить запись")
    print("<command> info <имя_таблицы> - вывести информацию о таблице")


    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

def print_table(rows: list[dict]) -> None:
    if not rows:
        print("Таблица пуста или ничего не найдено.")
        return

    table = PrettyTable()
    table.field_names = rows[0].keys()

    for row in rows:
        table.add_row(list(row.values()))

    print(table)

def run() -> None:
    cache_result = create_cacher()
    while True:
        current_metadata = load_metadata("db_meta.json")

        try:
            command = input("Введите команду: ")
            args = shlex.split(command)
        except (EOFError, KeyboardInterrupt):
            print("Работа программы завершена")
            break
        if not args:
            print("Пустой ввод")
            continue

        match args[0]:
            case "exit":
                break

            case "help":
                print_help()

            case "create_table":
                if len(args) < 2:
                    print("Укажите имя таблицы и её колонки")
                    continue
                try:
                    create_table(current_metadata, args[1], columns = args[2:])
                    save_metadata("db_meta.json", current_metadata)
                    print(f"Таблица '{args[1]}' создана")
                except ValueError:
                    continue

            case "drop_table":
                if len(args) < 2:
                    print("Укажите имя таблицы")
                    continue
                try:
                    result = drop_table(current_metadata, args[1])

                    if result is not None:
                        save_metadata("db_meta.json", current_metadata)
                        print(f"Таблица '{args[1]}' удалена")

                except ValueError:
                    continue

            case "list_tables":
                if not current_metadata:
                    print("База данных пуста")
                else:
                    print("Список таблиц:")
                    for table_name in current_metadata:
                        print(f"- {table_name}")
            case "insert":
                if len(args) < 5 or args[1] != "into" or args[3] != "values":
                    print("Ошибка формата. "
                          "Ожидается: insert into <таблица> values (<значения>)")
                    continue

                table_name = args[2]
                if table_name not in current_metadata:
                    print(f"Таблицы '{table_name}' не существует")
                    continue

                raw_values_str = " ".join(args[4:]).strip("()")
                raw_values = [v.strip().strip("'\"") for v in raw_values_str.split(",")]

                try:
                    columns = current_metadata[table_name]["columns"]
                    converted_values = convert_values(raw_values, columns)

                    insert(current_metadata, table_name, converted_values)
                    print(f"Запись успешно добавлена в '{table_name}'")
                    cache_result = create_cacher()

                except ValueError:
                    continue

            case "select":
                if len(args) < 3 or args[1] != "from":
                    print("Ошибка формата. "
                          "Ожидается: select from <таблица> [where <условие>]")
                    continue

                table_name = args[2]
                if table_name not in current_metadata:
                    print(f"Таблицы '{table_name}' не существует")
                    continue

                where_clause = None
                if "where" in args:
                    where_idx = args.index("where")
                    where_str = " ".join(args[where_idx + 1:])
                    columns = current_metadata[table_name]["columns"]
                    try:
                        where_clause = parse_where(where_str, columns)
                    except ValueError:
                        continue

                cache_key = f"{table_name}_{where_clause}"

                def value_func():
                    t_data = load_table_data(table_name)
                    return select(t_data, where_clause)

                result = cache_result(cache_key, value_func)

                print_table(result)

            case "update":
                if len(args) < 6 or args[2] != "set":
                    print("Ошибка формата. Ожидается: update <таблица> "
                          "set <колонка> = <значение> [where <условие>]")
                    continue

                table_name = args[1]
                if table_name not in current_metadata:
                    print(f"Таблицы '{table_name}' не существует")
                    continue

                where_idx = args.index("where") if "where" in args else -1

                if where_idx != -1:
                    set_str = " ".join(args[3:where_idx])
                    where_str = " ".join(args[where_idx + 1:])
                else:
                    set_str = " ".join(args[3:])
                    where_str = None

                try:
                    columns = current_metadata[table_name]["columns"]
                    set_clause = parse_set(set_str, columns)

                    where_clause = None
                    if where_str:
                        where_clause = parse_where(where_str, columns)

                    table_data = load_table_data(table_name)
                    updated_data = update(table_data, set_clause, where_clause)
                    save_table_data(table_name, updated_data)

                    print("Данные успешно обновлены.")
                    cache_result = create_cacher()
                except ValueError:
                    continue

            case "delete":
                if len(args) < 5 or args[1] != "from" or args[3] != "where":
                    print("Ошибка формата. "
                          "Ожидается: delete from <таблица> where <условие>")
                    continue

                table_name = args[2]
                if table_name not in current_metadata:
                    print(f"Таблицы '{table_name}' не существует")
                    continue

                where_str = " ".join(args[4:])

                try:
                    columns = current_metadata[table_name]["columns"]
                    where_clause = parse_where(where_str, columns)

                    table_data = load_table_data(table_name)
                    updated_data = delete(table_data, where_clause)

                    if updated_data is not None:
                        save_table_data(table_name, updated_data)
                        print("Записи успешно удалены.")
                        cache_result = create_cacher()

                except ValueError:
                    continue

            case "info":
                if len(args) != 2:
                    print("Ошибка формата. Ожидается: info <таблица>")
                    continue

                table_name = args[1]

                if table_name not in current_metadata:
                    print(f"Таблицы '{table_name}' не существует")
                    continue

                columns = current_metadata[table_name]["columns"]
                columns_str = ", ".join(columns)
                table = load_table_data(table_name)

                print(f"Таблица: {table_name}")
                print(f"Столбцы: {columns_str}")
                print(f"Количество записей: {len(table)}")

            case _:
                print(f"Неизвестная команда: {args[0]}. "
                      f"Введите 'help' для списка команд.")








