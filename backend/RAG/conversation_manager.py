from azure.core.exceptions import HttpResponseError
from .index_query import get_docs_hybrid
from .Chat_Response import get_completion_from_messages, plantilla_sys
from configuration import prompts
import logging

def respond_message(conn, message, History):
    History.append({"role": "user", "content": message})
    
    new_query = message
    improved = False
    # Mejorar la pregunta del usuario
    if len(History) > 1:
        # Usar máximo últimos 7 mensajes para mejorar la pregunta
        recent_History = History[-7:]
        recent_History.append({"role": "system", "content":  prompts["improve_query"]})
        try:
            respuesta = get_completion_from_messages(recent_History)
            new_query = respuesta[0]
            History.append({"role": "user", "content": new_query})
            logging.info(f"Pregunta mejorada: {new_query}")
            improved = True
        except HttpResponseError as e:
            log_msg = "Error en el llamado a openAI para mejorar la pregunta: " + str(e)
            logging.error(log_msg)

    # Obtener contexto de documentos relevantes
    context = get_docs_hybrid(conn,  new_query)
    History.append({"role": "system", "content": plantilla_sys(context)})

    try:
        respuesta = get_completion_from_messages(History)
        respuesta_texto = respuesta[0]

    except HttpResponseError as e:
        respuesta_texto = "Error en el llamado a openAI: " + str(e)

    History.pop()  # delete the context prompt

    # delete the improved query prompt if it was added 
    if  improved:
        History.pop()

    # Add the assistant's response to the history
    History.append({"role": "assistant", "content": respuesta_texto})

    new_messages = History[-2:]

    return respuesta_texto, new_messages
