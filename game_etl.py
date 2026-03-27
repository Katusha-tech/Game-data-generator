import psycopg2
from datetime import datetime, timedelta
import json
from data_generator import generate_users, generate_sessions, generate_events
from config import DB_CONFIG  

# -----------------------------
# 1. Создание таблицы логов
# -----------------------------
def create_etl_logs_table():
    """Создаёт таблицу etl_logs"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS etl_logs (
                    id SERIAL PRIMARY KEY,
                    table_name VARCHAR(50) NOT NULL,
                    load_date TIMESTAMP NOT NULL,
                    rows_loaded INT NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    message TEXT
                );
            """)
        conn.commit()
    except Exception as e:
        print(f"Ошибка при создании таблицы etl_logs: {e}")
    finally:
        if 'conn' in locals():
            conn.close()


# -----------------------------
# 2. Функция логирования ETL
# -----------------------------
def log_etl(table_name, rows_loaded, status, message=''):
    """Логирование ETL процесса в таблицу etl_logs"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO etl_logs (table_name, load_date, rows_loaded, status, message)
                VALUES (%s, %s, %s, %s, %s)
            """, (table_name, datetime.now(), rows_loaded, status, message))
        conn.commit()
    except Exception as e:
        print(f"Ошибка при логировании ETL: {e}")
    finally:
        if 'conn' in locals():
            conn.close()


# -----------------------------
# 3. Функция загрузки событий
# -----------------------------
def load_events(events_list):
    """Вставка сгенерированных событий в таблицу raw_events"""
    rows_loaded = 0
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            for event in events_list:
                cur.execute("""
                    INSERT INTO raw_events
                    (event_id, event_time, user_id, session_id, event_type, event_params, load_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    str(event['event_id']),
                    event['event_time'],
                    event['user_id'],
                    str(event['session_id']),
                    event['event_type'],
                    json.dumps(event['event_params']),
                    datetime.today().date()
                ))
                rows_loaded += 1
        conn.commit()
        print(f"Загружено строк: {rows_loaded}")
        return rows_loaded
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        raise e
    finally:
        if 'conn' in locals():
            conn.close()


# -----------------------------
# 4. Основной ETL процесс
# -----------------------------
if __name__ == "__main__":
    # 4.1 Создаём таблицу логов
    create_etl_logs_table()

    # 4.2 Настройки ETL
    n_days = 5
    n_users = 5
    users = generate_users(n_users)
    base_date = datetime(2024, 1, 1)

    # 4.3 Очищаем raw_events перед загрузкой
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE raw_events;")
        conn.commit()
    finally:
        if 'conn' in locals():
            conn.close()

    # 4.4 Генерация и загрузка событий по дням
    for day in range(n_days):
        current_date = base_date + timedelta(days=day)
        print(f"Дата: {current_date}")

        try:
            # Генерация сессий и событий
            sessions = generate_sessions(users, current_date)
            events = generate_events(sessions)
            print(f"Сгенерировано событий: {len(events)}")

            # Загрузка в БД и логирование
            rows_loaded = load_events(events)
            log_etl("raw_events", rows_loaded, "SUCCESS")

        except Exception as e:
            print(f"Ошибка ETL за {current_date}: {e}")
            log_etl("raw_events", 0, "ERROR", str(e))