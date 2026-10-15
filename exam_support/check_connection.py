"""Проверяет подключение из Python; БД и данные не изменяет."""

import json
from pathlib import Path

import psycopg


def main():
    config_path = Path(__file__).resolve().parent / "config.local.json"
    if not config_path.is_file():
        raise SystemExit("Создай config.local.json из config.example.json и укажи выданные параметры БД.")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    try:
        with psycopg.connect(**config) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT current_database(), current_user, version()")
                database, user, version = cursor.fetchone()
    except psycopg.Error as error:
        raise SystemExit(f"Подключение не выполнено: {error}") from error
    print(f"База: {database}\nПользователь PostgreSQL: {user}\nСервер: {version}")


if __name__ == "__main__":
    main()
