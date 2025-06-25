from Postgres.postgres import create_postgres_connection
from langchain_openai import OpenAIEmbeddings
from configuration import config_OAI


key = config_OAI["key"]


def cargar_diccionario_categorias(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id, categoria FROM categories")
        rows = cur.fetchall()
        return {categoria: id for id, categoria in rows}


def homologar_categorias(categorias_raw, dict_categorias):
    return [dict_categorias.get(cat, None) for cat in categorias_raw]


def create_vectorstore(splits):

    inputs = [item.page_content for item in splits]
    Embeddings = OpenAIEmbeddings(openai_api_key=key, model=config_OAI["embeddings"])
    embeddings = Embeddings.embed_documents(texts=inputs)
    categories = [item.metadata.get("categoria", "default") for item in splits]

    with create_postgres_connection() as conn:  # pylint: disable=E1129
        dict_categorias = cargar_diccionario_categorias(conn)
        category_ids = homologar_categorias(categories, dict_categorias)
        with conn.cursor() as cur:
            for content, embedding, categoria_id in zip(
                inputs, embeddings, category_ids
            ):
                cur.execute(
                    """
                    INSERT INTO documents (content, embedding, categoria_id)
                    VALUES (%s, %s, %s)
                    """,
                    (content, embedding, categoria_id),
                )
    print("Índice creado en postgres!")
