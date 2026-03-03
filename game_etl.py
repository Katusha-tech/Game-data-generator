import psycopg2
from datetime import datetime
import json
from data_generator import generate_users, generate_sessions, generate_events


DB_CONFIG = {
    'host': 'localhost',
    'database': 'game_data',  
    'user': 'game_user',       
    'password': 'secure_password'  
}

def load_events(events_list):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        rows_loaded = 0

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

    except Exception as e:
        print(f"Ошибка при загрузке: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    # 1. Генерация пользователей
    users = generate_users(5)

    # 2. Базовая дата
    base_date = datetime(2024, 1, 1)

    # 3. Генерация сессии
    sessions = generate_sessions(users, base_date)

    # 4. Генерация событий
    events = generate_events(sessions)

    print(f"Сгенерировано событий: {len(events)}")
    load_events(events)