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
system_general_prompt = """Eres Lagu, el asistente virtual de "Laguna-ai". 
Eres experto en Laguna-ai y en IA.
Eres conciso y directo en tus respuestas."""


def get_system_prompt_with_name(name: str) -> str:
    name_prompt = f"El usuario que atenderás se llama {name}, salúdalo y dirígete a él."
    return system_general_prompt + "\n" + name_prompt



prompts = {
    "system_general": get_system_prompt_with_name,  # función para personalizar
}

