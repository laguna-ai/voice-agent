from openai import AzureOpenAI
from configuration import config_AOAI

# Configuración para sumarización con Azure OpenAI
summ_cfg = config_AOAI["summarization"]
endpoint = summ_cfg["endpoint"]
subscription_key = summ_cfg["key"]
api_version = summ_cfg["api_version"]
deployment = summ_cfg["deployment"]

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)


def get_completion_from_messages(messages, model=deployment, temperature=0):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content
