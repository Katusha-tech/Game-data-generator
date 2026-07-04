import psycopg2
from config import DB_CONFIG

# 1. Обновление аналитической витрины
def update_user_activity_summary():
    """Обновляет витрину user_activity_summary"""

    try:
        conn = psycopg2.connect(**DB_CONFIG)

        with conn.cursor() as cur:

            # очищаем витрину
            cur.execute("""
                TRUNCATE TABLE user_activity_summary;
            """)

            # загружаем агрегаты
            cur.execute("""
                INSERT INTO user_activity_summary (
                    user_id,
                    total_events,
                    total_sessions,
                    total_purchases,
                    total_ad_views
                )

                SELECT
                    user_id,
                    COUNT(*) AS total_events,
                    COUNT(DISTINCT session_id) AS total_sessions,
                    SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) AS total_purchases,
                    SUM(CASE WHEN event_type = 'ad_view' THEN 1 ELSE 0 END) AS total_ad_views

                FROM raw_events
                GROUP BY user_id;
            """)

        conn.commit()

        print("Витрина user_activity_summary обновлена")

    except Exception as e:
        print(f"Ошибка обновления витрины: {e}")

    finally:
        if 'conn' in locals():
            conn.close()