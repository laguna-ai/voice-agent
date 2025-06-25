from openai import AzureOpenAI
from configuration import config_AOAI

llm_cfg = config_AOAI["llm"]
endpoint = llm_cfg["endpoint"]
subscription_key = llm_cfg["key"]
api_version = llm_cfg["api_version"]
deployment = llm_cfg["deployment"]

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
    )
    return response.choices[0].message.content, response.usage
