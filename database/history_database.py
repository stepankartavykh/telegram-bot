import sqlite3
from dataclasses import dataclass
from time import time


@dataclass
class Entry:
    """
    Класс одной записи в базе данных истории поиска.
    :command: Название команды.
    :time_call: Время вызова команды.
    """
    command: str
    time_call: int = time()


class DatabaseAndTableCreate:
    """
    Класс для создания базы данных и таблицы с историей запросов пользователя.
    """
    table_name = "history_entries"
    create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                entry_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                entry_name TEXT, 
                call_time INTEGER
            )
            """

    def __init__(self, database_name: str):
        """
        Конструктор объекта базы данных. Создает файл базы данных.
        :param database_name: Название файла базы данных.
        """
        self.database_name = database_name
        self.entries_table_name = self.table_name
        with sqlite3.connect(database_name) as connection:
            connection.cursor()

    def create_table_history(self):
        """
        Метод создает таблицу в базе данных
        """
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            cursor.execute(self.create_table_query)


class Operations:
    """
    Класс для операций с базой данных.
    """
    @staticmethod
    def add_entry(database_file: DatabaseAndTableCreate, entry: Entry):
        """
        Добавление записи в базу данных.
        :param database_file: Файл базы данных с историей запросов.
        :param entry: Запись, которую нужно добавить в базу.
        """
        with sqlite3.connect(database_file.database_name) as connection:
            cursor = connection.cursor()
            query = f"INSERT INTO {database_file.entries_table_name} (entry_name, call_time) " \
                    f"VALUES ('{entry.command}', {entry.time_call})"
            cursor.execute(query)

    @staticmethod
    def get_entries(database_file: DatabaseAndTableCreate, how_many: int) -> list:
        """
        Функция получения определенного количества последних команд.
        :param database_file: Файл базы данных.
        :param how_many: Количество записей для получения.
        :return: Список из кортежей, в которых лежат записи из базы данных(id, entry_name, time_call).
        """
        with sqlite3.connect(database_file.database_name) as connection:
            cursor = connection.cursor()
            query = f"SELECT * FROM {database_file.entries_table_name}"
            cursor.execute(query)
            data = []
            for result in cursor.fetchall()[-how_many:]:
                data.append(result)
            return data

    @staticmethod
    def clean_all_entries(database_file: DatabaseAndTableCreate):
        """ Функция для очистки таблицы с запросами. """
        with sqlite3.connect(database_file.database_name) as connection:
            cursor = connection.cursor()
            query = f"DELETE FROM {database_file.entries_table_name}"
            cursor.execute(query)
