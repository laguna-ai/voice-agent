import csv
import pytest
from Postgres.postgres import create_postgres_connection
from RAG.index_query import get_doc_ids_hybrid, get_docs_hybrid

# Lee el CSV y construye { pregunta: [lista_de_ids] }


def load_queries_and_expected(path_csv):
    mapping = {}
    with open(path_csv, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pregunta = row["pregunta"].strip()
            try:
                doc_id = int(row["documento_id"])
            except ValueError as exc:
                raise ValueError(
                    f"documento_id inválido en CSV: '{row['documento_id']}'"
                ) from exc
            if pregunta not in mapping:
                mapping[pregunta] = []
            mapping[pregunta].append(doc_id)
    return mapping


# Ruta al CSV con preguntas e IDs esperados
CSV_PATH = "csv_data/bateria.csv"
_QUESTIONS_TO_EXPECTED = load_queries_and_expected(CSV_PATH)

print(f"Batería cargada desde {CSV_PATH}: {_QUESTIONS_TO_EXPECTED}")

# Parametrize: lista de (pregunta, [ids_esperados])
PARAMS = [
    (q, _QUESTIONS_TO_EXPECTED[q]) for q in _QUESTIONS_TO_EXPECTED
]  # Últimos para pruebas rápidas


@pytest.mark.parametrize("query, expected_ids", PARAMS)
def test_search_results_include_expected_ids(query, expected_ids):
    """
    Para cada pregunta, invocamos get_doc_ids(...) con k >= len(expected_ids)
    y comprobamos que cada ID esperado esté en los resultados.
    """
    with create_postgres_connection() as conn:
        k = max(len(expected_ids), 4)
        returned_ids = get_doc_ids_hybrid(conn, query, k=k)
        for expected in expected_ids:
            assert expected in returned_ids, (
                f"El documento con ID={expected} NO se encontró en"
                f"{returned_ids}"
                f"query='{query}'"
            )


def get_docs_by_ids(conn, ids):
    """
    Devuelve el contenido de los documentos dados sus IDs, concatenado en un string.
    """
    if not ids:
        return ""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT content FROM documents WHERE id = ANY(%s) ORDER BY array_position(%s, id);",
            (ids, ids),
        )
        rows = cur.fetchall()
    return "\n\n".join(r[0] for r in rows)


def test_hybrid_docs_consistency():
    query = "de que trata la unidad 1 del curso Diseño de Autor?"
    k = 4
    rrf_k = 60
    with create_postgres_connection() as conn:
        ids = get_doc_ids_hybrid(conn, query, k, rrf_k)
        docs_by_ids = get_docs_by_ids(conn, ids)
        docs_hybrid = get_docs_hybrid(conn, query, k, rrf_k)

    assert (
        docs_by_ids.strip() == docs_hybrid.strip()
    ), "Los documentos obtenidos por ambos métodos no coinciden"
