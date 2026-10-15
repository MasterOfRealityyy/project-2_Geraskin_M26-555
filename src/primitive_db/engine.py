def welcome() -> None:
    print("***")
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")

    while True:
        try:
            command = input("Введите команду: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if command == "exit":
            break
        elif command == "help":
            print("<command> exit - выйти из программы")
            print("<command> help - справочная информация")
        elif command == "":
            continue
        else:
            print(f"Неизвестная команда: {command}")
