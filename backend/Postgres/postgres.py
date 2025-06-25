import json
import psycopg
import time
from configuration import config_postgres


def create_postgres_connection():
    # open database connection
    PASSWORD = config_postgres["password"]
    DATABASE = config_postgres["dbname"]
    USER = config_postgres["user"]
    HOST = config_postgres["host"]
    PORT = config_postgres["port"]

    connection = psycopg.connect(
        dbname=DATABASE,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        autocommit=True,
    )
    return connection


# def find_or_create_session(conn, tel):
#     with conn.cursor() as cur:
#         # Consulta unificada usando CTEs para manejar la lógica de sesión
#         query = """
#         INSERT INTO sessions (id, history, created_at)
#         SELECT
#             %s, %s, to_timestamp(%s)
#         WHERE NOT EXISTS (
#             SELECT 1 FROM sessions WHERE id = %s
#         )
#         ON CONFLICT (id) DO NOTHING
#         RETURNING *;
#         """
#         timestamp = time.time()

#         params = (
#             tel,
#             json.dumps(build_sysPrompt("Pepito")),
#             timestamp,
#             tel,
#         )

#         cur.execute(query, params)
#         session = cur.fetchone()

#         # Determinar si se dio la bienvenida basado en si se creó una sesión o no
#         welcome = session is not None
#         if not welcome:
#             query1 = """
#             SELECT * FROM sessions
#             WHERE id = %s
#             """
#             cur.execute(query1, (tel,))
#             session = cur.fetchone()

#         return session[1], welcome  # 1 for history


# def update_session(conn, tel, new_messages):

#     new_messages_json = json.dumps(new_messages)

#     with conn.cursor() as cur:
#         # Concatena el arreglo JSONB existente con el nuevo arreglo de mensajes
#         query = """
#         UPDATE sessions
#         SET history = history || %s::jsonb
#         WHERE id = %s
#         """

#         cur.execute(query, (new_messages_json, tel))


# For Dialogflow CX webhook
def upsert_session_history(conn, session_id, history):
    with conn.cursor() as cur:
        # Preparar el historial como JSONB para insertarlo o actualizarlo
        history_json = json.dumps(history)

        # Query para hacer upsert en la tabla 'sessions'
        query = """
        INSERT INTO sessions (id, history, created_at)
        VALUES (%s, %s::jsonb, to_timestamp(%s))
        ON CONFLICT (id)
        DO UPDATE SET history = %s::jsonb
        RETURNING *;
        """
        timestamp = time.time()

        cur.execute(query, (session_id, history_json, timestamp, history_json))
