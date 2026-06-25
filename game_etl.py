import psycopg2
from datetime import datetime, timedelta
import json
from data_generator import generate_users, generate_sessions, generate_events
from config import DB_CONFIG  
from analytics import update_user_activity_summary
from logger import create_etl_logs_table, log_etl
from etl import validate_events, load_events


# 1. Основной ETL процесс

if __name__ == "__main__":
    # 5.1 Создаём таблицу логов
    create_etl_logs_table()

    # 1.2 Настройки ETL
    n_days = 5
    n_users = 5
    users = generate_users(n_users)
    base_date = datetime(2024, 1, 1)

    # 1.2 Очищаем raw_events перед загрузкой
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE raw_events;")
        conn.commit()
    finally:
        if 'conn' in locals():
            conn.close()

    # 1.3 Генерация и загрузка событий по дням
    for day in range(n_days):
        current_date = base_date + timedelta(days=day)
        print(f"Дата: {current_date}")

        try:
            # Генерация сессий и событий
            sessions = generate_sessions(users, current_date)
            events = generate_events(sessions)
            print(f"Сгенерировано событий: {len(events)}")

            # проверка данных
            valid_events = validate_events(events)
            print(f"После очистки: {len(valid_events)}")

            # количество отброшенных событий
            dropped = len(events) - len(valid_events)
            print(f"Отброшено событий: {dropped}")

            # Загрузка в БД и логирование
            rows_loaded = load_events(valid_events)
            update_user_activity_summary()
            log_etl("raw_events", rows_loaded, "SUCCESS", rows_dropped=dropped)

        except Exception as e:
            print(f"Ошибка ETL за {current_date}: {e}")
            log_etl("raw_events", 0, "ERROR", str(e), rows_dropped=0)
