import datetime
import time
import json
import uuid

# funciones de time trigger


def get_sessions_to_finish(conn):

    # Calcula la fecha límite para las sesiones activas (18 horas antes de ahora)
    cutoff_time = datetime.datetime.utcnow() - datetime.timedelta(hours=18)

    with conn.cursor() as cur:
        query = """
            SELECT * FROM sessions
            WHERE created_at < %s
        """
        cur.execute(query, (cutoff_time,))
        sessions_to_update = cur.fetchall()

    return sessions_to_update


def finish_session(conn, session):
    ID = session[0]
    history = session[1]
    created_at = session[2]
    closed_at = time.time()

    with conn.cursor() as cur:
        query = """
        INSERT INTO closed_sessions (id, history, closed_at, created_at)
        VALUES (%s, %s, to_timestamp(%s), %s);
        """
        cur.execute(
            query,
            (
                ID + "_" + str(uuid.uuid4()),
                json.dumps(history),
                closed_at,
                created_at,
            ),
        )
        query_delete = """
        DELETE FROM sessions WHERE id = %s;
        """
        cur.execute(query_delete, (ID,))
