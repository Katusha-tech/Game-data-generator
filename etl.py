import psycopg2
import json
from datetime import datetime
from config import DB_CONFIG


# 1. Функция загрузки событий
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


# 2. Функция валидации событий
def validate_events(events_list):
    """Проверка событий перед загрузкой"""
    valid_events = []

    for event in events_list:
        # 2.1 Проверка обязательных полей
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

        # 2.2 Проверка типа события
        allowed_types = ["session_start", "level_start", "level_complete", "ad_view", "purchase"]
        if event["event_type"] not in allowed_types:
            continue

        # 2.3 Добавляем валидные события
        valid_events.append(event)

    return valid_events

