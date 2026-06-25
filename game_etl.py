import psycopg2
from datetime import datetime, timedelta
import json
from data_generator import generate_users, generate_sessions, generate_events
from config import DB_CONFIG  
from analytics import update_user_activity_summary
from logger import create_etl_logs_table, log_etl



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
# 4. Функция валидации событий
# -----------------------------
def validate_events(events_list):
    """Проверка событий перед загрузкой"""
    valid_events = []

    for event in events_list:
        # 1. Проверка обязательных полей
        if not event.get("event_id"):
            continue
        if not event.get("event_time"):
            continue
        if not event.get("user_id"):
            continue
        if not event.get("session_id"):
            continue
        if not event.get("event_type"):
            continue

        # 2. Проверка типа события
        allowed_types = ["session_start", "level_start", "level_complete", "ad_view", "purchase"]
        if event["event_type"] not in allowed_types:
            continue

        # 3. Добавляем валидные события
        valid_events.append(event)

    return valid_events


# -----------------------------
# 5. Основной ETL процесс
# -----------------------------
if __name__ == "__main__":
    # 5.1 Создаём таблицу логов
    create_etl_logs_table()

    # 5.2 Настройки ETL
    n_days = 5
    n_users = 5
    users = generate_users(n_users)
    base_date = datetime(2024, 1, 1)

    # 5.3 Очищаем raw_events перед загрузкой
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE raw_events;")
        conn.commit()
    finally:
        if 'conn' in locals():
            conn.close()

    # 5.4 Генерация и загрузка событий по дням
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
