import uuid
import random 
from datetime import datetime, timedelta

def generate_users(n_users: int) -> list[int]:
    """
    Генерирует список user_id от 1 до n_users
    """
    if n_users <= 0:
        raise ValueError("n_users должен быть больше 0")
    return list(range(1, n_users + 1))

def generate_sessions(users: list[int], base_date: datetime) -> list[dict]:
    """
    Генерирует сессии для списка пользователей за один день 

    """
    sessions = []
    for user_id in users:
        n_sessions = random.randint(1, 3)

        for _ in range(n_sessions):
            session_id = uuid.uuid4()

            start_time = base_date + timedelta(minutes=random.randint(0, 24 * 60))
            duration_minutes = random.randint(1, 10)
            end_time = start_time + timedelta(minutes=duration_minutes)

            sessions.append({
                "user_id": user_id,
                "session_id": session_id,
                "session_start": start_time,
                "session_end": end_time
            })
    return sessions

def generate_events(sessions: list[dict]) -> list[dict]:
    """
    Превращает сессии в события

    """
    events = []
    for s in sessions:
        user_id = s["user_id"]
        session_id = s["session_id"]
        start = s["session_start"]
        end = s["session_end"]

        # session_start
        events.append({
            "event_id": uuid.uuid4(),
            "user_id": user_id,
            "session_id": session_id,
            "event_type": "session_start",
            "event_time": start,
            "event_params": {}
        })

        # случайное количество уровней (1-3) в сессии
        n_levels = random.randint(1, 3)
        for lvl in range(1, n_levels + 1):
            level_start_time = start + timedelta(minutes=random.randint(0, max(0, int((end - start).total_seconds() // 60) - 1)))
            level_complete_time = min(level_start_time + timedelta(minutes=random.randint(1, 5)), end)


            events.append({
                "event_id": uuid.uuid4(),
                "user_id": user_id,
                "session_id": session_id,
                "event_type": "level_start",
                "event_time": level_start_time,
                "event_params": {"level": lvl}
            })

            events.append({
                "event_id": uuid.uuid4(),
                "user_id": user_id,
                "session_id": session_id,
                "event_type": "level_complete",
                "event_time": level_complete_time,
                "event_params": {"level": lvl}
            })

        # ad_view
        n_ads = random.randint(0, 2)
        for _ in range(n_ads):
            ad_time = start + timedelta(minutes=random.randint(0, int((end - start).total_seconds() // 60)))
            events.append({
                "event_id": uuid.uuid4(),
                "user_id": user_id,
                "session_id": session_id,
                "event_type": "ad_view",
                "event_time": ad_time,
                "event_params": {}
            })

        # purchase
        if random.random() < 0.1:
            purchase_time = start + timedelta(minutes=random.randint(0, int((end - start).total_seconds() // 60)))
            amount = random.choice([1.99, 4.99, 9.99])
            events.append({
                "event_id": uuid.uuid4(),
                "user_id": user_id,
                "session_id": session_id,
                "event_type": "purchase",
                "event_time": purchase_time,
                "event_params": {"amount": amount}
            })

    return sorted(events, key=lambda x: x["event_time"])

if __name__ == "__main__":
    users = generate_users(3)
    base_date = datetime(2024, 1, 1)
    sessions = generate_sessions(users, base_date)
    events = generate_events(sessions)

    for e in events:
        print(e)


