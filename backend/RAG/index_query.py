from langchain_openai import OpenAIEmbeddings
import numpy as np
from pgvector.psycopg import register_vector
import os
from psycopg.errors import DatabaseError, ProgrammingError

key = os.environ["OPENAI_API_KEY"]


def search(query, k, score_threshold):
    return query + str(k) + score_threshold


def get_docs(conn, query: str, k: int = 4):
    """
    Versión que devuelve el contenido (content TEXT) de los k documentos más cercanos.
    Devuelve un único string con todos los contenidos concatenados.
    """
    Embeddings = OpenAIEmbeddings(openai_api_key=key, model="text-embedding-3-small")
    query_embedding = np.array(Embeddings.embed_query(text=query))
    register_vector(conn)

    with conn.cursor() as cur:
        # Recupera “content” de los k primeros documentos más cercanos.
        cur.execute(
            "SELECT content FROM documents ORDER BY embedding <=> %s LIMIT %s;",
            (query_embedding, k),
        )
        rows = cur.fetchall()

    # Concatenamos todos los contenidos en un único string (como hacía la versión anterior).
    doc_string = "\n\n".join(r[0] for r in rows)
    return doc_string


def get_docs_hybrid(conn, query: str, k: int = 4, rrf_k: int = 60) -> str:
    """
    Devuelve un string concatenado con el contenido de los k documentos más relevantes
    usando búsqueda híbrida (semántica + por palabras clave) con fusión RRF.
    """

    # Configuración inicial
    register_vector(conn)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    query_embedding = np.array(embeddings.embed_query(query))

    # Consulta SQL para búsqueda híbrida con obtención de contenido
    sql = """
    WITH semantic_search AS (
        SELECT id, RANK() OVER (ORDER BY embedding <=> %(embedding)s) AS rank
        FROM documents ORDER BY embedding <=> %(embedding)s LIMIT 20
    ),
    keyword_search AS (
        SELECT id, RANK() OVER (ORDER BY ts_rank_cd(to_tsvector('spanish', content), query) DESC) AS rank
        FROM documents, plainto_tsquery('spanish', %(query)s) query
        WHERE to_tsvector('spanish', content) @@ query
        ORDER BY ts_rank_cd(to_tsvector('spanish', content), query) DESC LIMIT 20
    ),
    combined AS (
        SELECT
            COALESCE(s.id, k.id) AS id,
            COALESCE(1.0/(%(rrf_k)s + s.rank), 0.0) + 
            COALESCE(1.0/(%(rrf_k)s + k.rank), 0.0) AS score
        FROM semantic_search s
        FULL OUTER JOIN keyword_search k ON s.id = k.id
    ),
    final_ranking AS (
        SELECT id, score
        FROM combined
        ORDER BY score DESC
        LIMIT %(k)s
    )
    SELECT d.content 
    FROM final_ranking r
    JOIN documents d ON r.id = d.id
    ORDER BY r.score DESC  -- ¡Mismo orden que el ranking RRF!
    """

    try:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                {"query": query, "embedding": query_embedding, "k": k, "rrf_k": rrf_k},
            )
            rows = cur.fetchall()

            # Concatenar contenidos
            contents = [row[0] for row in rows]
            result = "\n\n".join(contents)

            return result

    except ProgrammingError as e:
        print(f"Error en la consulta híbrida: {e}")
        return ""


def get_doc_ids(conn, query: str, k: int = 4):
    """
    Devuelve una lista de IDs de los k documentos más cercanos al embedding de la consulta.
    Imprime las distancias. Usa manejo de errores específico para psycopg v3.
    """
    register_vector(conn)

    Embeddings = OpenAIEmbeddings(openai_api_key=key, model="text-embedding-3-small")
    query_embedding = np.array(Embeddings.embed_query(text=query))
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, embedding <=> %s AS distance
                FROM documents
                ORDER BY distance
                LIMIT %s;
                """,
                (query_embedding, k),
            )
            rows = cur.fetchall()
    except DatabaseError as e:
        print(f"Error en la consulta a PostgreSQL: {e}")
        return []

    doc_ids = []
    print(f"Resultados más cercanos para: '{query}'")
    for i, (doc_id, distance) in enumerate(rows):
        print(f"[{i+1}] ID: {doc_id} | Distancia: {distance:.6f}")
        doc_ids.append(doc_id)

    return doc_ids


def get_doc_ids_hybrid(conn, query: str, k: int = 4, rrf_k: int = 60):
    """
    Devuelve una lista de IDs de los k documentos más relevantes usando una combinación
    de búsqueda semántica (vector) y búsqueda por palabras clave (full-text search).
    Usa RRF (Reciprocal Rank Fusion) para fusionar ambos rankings.
    """

    register_vector(conn)

    Embeddings = OpenAIEmbeddings(openai_api_key=key, model="text-embedding-3-small")
    query_embedding = np.array(Embeddings.embed_query(text=query))

    sql = """
    WITH semantic_search AS (
        SELECT id, RANK () OVER (ORDER BY embedding <=> %(embedding)s) AS rank
        FROM documents
        ORDER BY embedding <=> %(embedding)s
        LIMIT 20
    ),
    keyword_search AS (
        SELECT id, RANK () OVER (ORDER BY ts_rank_cd(to_tsvector('spanish', content), query) DESC)
        FROM documents, plainto_tsquery('spanish', %(query)s) query
        WHERE to_tsvector('spanish', content) @@ query
        ORDER BY ts_rank_cd(to_tsvector('spanish', content), query) DESC
        LIMIT 20
    )
    SELECT
        COALESCE(semantic_search.id, keyword_search.id) AS id,
        COALESCE(1.0 / (%(rrf_k)s + semantic_search.rank), 0.0) +
        COALESCE(1.0 / (%(rrf_k)s + keyword_search.rank), 0.0) AS score
    FROM semantic_search
    FULL OUTER JOIN keyword_search ON semantic_search.id = keyword_search.id
    ORDER BY score DESC
    LIMIT %(k)s
    """
    try:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                {
                    "query": query,
                    "embedding": query_embedding,
                    "k": k,
                    "rrf_k": rrf_k,
                },
            )
            rows = cur.fetchall()
    except ProgrammingError as e:
        print(f"Error en la consulta híbrida (ProgrammingError): {e}")
        return []

    doc_ids = []
    print(f"Resultados híbridos para: '{query}'")
    for i, (doc_id, score) in enumerate(rows):
        print(f"[{i+1}] ID: {doc_id} | RRF Score: {score:.6f}")
        doc_ids.append(doc_id)

    return doc_ids


def get_doc_ids_fulltext(conn, query: str, k: int = 5):
    """
    Devuelve una lista de IDs de los k documentos más relevantes usando solo búsqueda full-text.
    """
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, ts_rank_cd(to_tsvector('spanish', content), plainto_tsquery('spanish', %s)) AS rank
                FROM documents
                WHERE to_tsvector('spanish', content) @@ plainto_tsquery('spanish', %s)
                ORDER BY rank DESC
                LIMIT %s;
                """,
                (query, query, k),
            )
            rows = cur.fetchall()
    except ProgrammingError as e:
        print(f"Error en la consulta full-text (ProgrammingError): {e}")
        return []

    doc_ids = []
    print(f"Resultados full-text para: '{query}'")
    for i, (doc_id, rank) in enumerate(rows):
        print(f"[{i+1}] ID: {doc_id} | Rank: {rank:.6f}")
        doc_ids.append(doc_id)

    return doc_ids
