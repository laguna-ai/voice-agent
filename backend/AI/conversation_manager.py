from azure.core.exceptions import HttpResponseError
from .Chat_Response import get_completion_from_messages
import logging

def respond_message( message, History):
    History.append({"role": "user", "content": message})

    try:
        respuesta = get_completion_from_messages(History)
        respuesta_texto = respuesta[0]

    except HttpResponseError as e:
        respuesta_texto = "Error en el llamado a openAI: " + str(e)

    # Add the assistant's response to the history
    History.append({"role": "assistant", "content": respuesta_texto})

    new_messages = History[-2:]

    return respuesta_texto, new_messages
