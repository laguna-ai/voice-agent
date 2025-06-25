import openai
from configuration import config_OAI

# Configura tu clave de API de OpenAI aquí o usa variables de entorno
openai.api_key = config_OAI["key"]


# ChatGPT completion
llm_name = config_OAI["sum"]


def get_completion_from_messages(messages, model=llm_name, temperature=0):
    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,  # this is the degree of randomness of the model's output
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content
