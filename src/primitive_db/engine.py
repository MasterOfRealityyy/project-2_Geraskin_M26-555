from primitive_db.utils import load_metadata, save_metadata
from primitive_db.core import create_table, drop_table
import shlex

def print_help() -> None:
    """Выводит справочную информацию по командам."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

def run() -> None:
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
                except ValueError as e:
                    print(e)
            case "drop_table":
                if len(args) < 2:
                    print("Укажите имя таблицы")
                    continue
                try:
                    drop_table(current_metadata, args[1])
                    save_metadata("db_meta.json", current_metadata)
                    print(f"Таблица '{args[1]}' удалена")
                except ValueError as e:
                    print(e)
            case "list_tables":
                if not current_metadata:
                    print("База данных пуста")
                else:
                    print("Список таблиц:")
                    for table_name in current_metadata:
                        print(f"- {table_name}")
            case _:
                print(f"Неизвестная команда: {args[0]}. Введите 'help' для списка команд.")





