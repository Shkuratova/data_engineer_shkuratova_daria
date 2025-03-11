from Generator import Generator
from datetime import datetime
import psycopg2.extras
from os import getenv

start = datetime(2025, 2, 10, 0, 0, 0)
end = datetime(2025, 3, 11, 0, 0, 0)
g = Generator(start, end)
g.gen_data()

conn = psycopg2.connect(
    host=getenv("DB_HOST", "localhost"),
    port=getenv("DB_PORT", "5432"),
    dbname=getenv("POSTGRES_DB", "postgres"),
    user=getenv("POSTGRES_USER", "postgres"),
    password=getenv("POSTGRES_PASSWORD", "admin")
)
cursor = conn.cursor()
psycopg2.extras.register_uuid()

# Log_event
for k, v in g.log_events.items():
    cursor.execute(
        "INSERT INTO log_event (guid, event_name) "
        "VALUES (%s, %s)", (v, k)
    )

# Users
for i in range(g.user_cnt):
    cursor.execute(
        "INSERT INTO users (guid, username, email, date_joined)"
        "VALUES (%s, %s, %s, %s)", (g.users[i], g.username[i], g.user_email[i], g.user_joined[i])
    )

# Topics
for i, j in enumerate(g.topics.items()):
    k, v = j
    cursor.execute(
        "INSERT INTO topics (guid, user_guid, title, content, date_created)"
        "VALUES (%s, %s, %s, %s, %s)", (
            k, v.user_guid, g.topic_title[i], g.topic_content[i], v.date_created)
    )

# Messages
for i, j in enumerate(g.messages.items()):
    k, v = j
    cursor.execute(
        "INSERT INTO messages (guid, topic_guid, user_guid, date_created, body)"
        "VALUES (%s, %s, %s, %s, %s)", (
            k, v.topic_guid, v.user_guid, v.date_created, g.message_body[i])
    )

# Logs
for i in range(g.log_cnt):
    cursor.execute(
        "INSERT INTO logs (guid, log_date, user_guid, response_status_code, log_message, event_guid, topic_guid, message_guid)"
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (
            g.log_guid[i], g.log_date[i], g.user_guid[i], g.server_response[i],
            g.log_message[i], g.log_event_guid[i], g.topic_guid[i], g.message_guid[i]
        )
    )

conn.commit()
cursor.close()
conn.close()
