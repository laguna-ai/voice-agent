import os

# Configuración de la base de datos de Postgres
config_postgres = {
    "password": os.environ["POSTGRES_PASS"],
    "dbname": "citus",
    "user": "citus",
    "host": "c-learnia-postgres.mzd54eshacvnl4.postgres.cosmos.azure.com",
    "port": "5432",
}

# Configuración de Azure OpenAI
config_OAI = {
    "llm": "gpt-4o",
    "sum": "gpt-4o-mini",
    "embeddings": "text-embedding-3-small",
    "key": os.environ["OPENAI_API_KEY"],
}


# Prompts
system_general_prompt = """Eres MentIA, el tutor virtual de "Learnia" \
para resolver dudas de los estudiantes de la plataforma. \
Ofreces acompañamiento claro, preciso y personalizado sobre los cursos de Learnia \
y todo tipo de información administrativa como fechas, evaluaciones, etc. de la plataforma. \
Eres conciso y directo en tus respuestas.\
No remitas a otro sitio ni compartas información ajena a la plataforma \
como deportes, entretenimiento, ciencias, humanidades, etc."""


def get_system_prompt_with_name(name: str) -> str:
    name_prompt = f"El usuario que atenderás se llama {name}, salúdalo y dirígete a él."
    return system_general_prompt + "\n" + name_prompt


system_particular_prompt = """No hablas de cosas diferentes a "Learnia", como matemáticas, deportes, música, etc.
"""

improve_query_prompt="""Basado en el historial de conversacióny partir del último
mensaje del usuario debes generar una pregunta que sea más explícita y \
que ayude a obtener una respuesta más clara.
Por favor, evita repetir la pregunta del usuario.
Es importante que la pregunta mencione el contexto relevante actual \
del cual se está hablando, por ejemplo:
- curso Diseño Instruccional.
- curso Diseño de Autor.
- ADMINISTRATIVO Y SOPORTE.
- CERTIFICACIÓN Y EVALUACIÓN.
O categorías más específicas si es necesario.
Nueva pregunta o prompt mejorado:
"""

prompts = {
    "system_general": get_system_prompt_with_name,  # función para personalizar
    "system_particular": system_particular_prompt,
    "improve_query": improve_query_prompt,
}

