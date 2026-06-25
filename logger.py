import psycopg2
from datetime import datetime
from config import DB_CONFIG


# 1. Создание таблицы логов
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


# 2. Функция логирования ETL
def log_etl(table_name, rows_loaded, status, message='', rows_dropped=0):
    """Логирование ETL процесса в таблицу etl_logs"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO etl_logs (table_name, load_date, rows_loaded, status, message, rows_dropped)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (table_name, datetime.now(), rows_loaded, status, message, rows_dropped))
        conn.commit()
    except Exception as e:
        print(f"Ошибка при логировании ETL: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

