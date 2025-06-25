import os

# Configuración de la base de datos de Postgres
config_postgres = {
    "password": os.environ["POSTGRES_PASS"],
    "dbname": "citus",
    "user": "citus",
    "host": "c-voice-db.sl2ylaoczcx2yr.postgres.cosmos.azure.com",
    "port": "5432",
}


# Configuración para Azure OpenAI (AOAI) anidada por modelo
config_AOAI = {
    "llm": {
        "endpoint": "https://juana-mcaz6bvc-swedencentral.cognitiveservices.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2025-01-01-preview",
        "key": os.getenv("AOAI_KEY"),
        "deployment": "gpt-4o",
        "api_version": "2025-01-01-preview",
    },
    "whisper": {
        "endpoint": "https://juana-mcaz6bvc-swedencentral.cognitiveservices.azure.com/openai/deployments/whisper/audio/translations?api-version=2024-06-01",
        "key": os.getenv("AOAI_KEY"),
        "deployment": "whisper",
        "api_version": "2024-06-01",
    },
    "tts": {
        "endpoint_root": "https://juana-mcaz6bvc-swedencentral.cognitiveservices.azure.com",
        "key": os.getenv("AOAI_KEY"),
        "deployment": "tts",
        "api_version": "2025-03-01-preview",
    },
    "summarization": {
        "endpoint": "https://juana-mcaz6bvc-swedencentral.cognitiveservices.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2025-01-01-preview",
        "key": os.getenv("AOAI_KEY"),
        "deployment": "gpt-4o-mini",
        "api_version": "2025-01-01-preview",
    },
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

