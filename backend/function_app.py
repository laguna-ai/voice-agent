import azure.functions as func
import logging
from finish_sessions.blueprint import blueprint
from AI.conversation_manager import respond_message
from Postgres.postgres import create_postgres_connection, upsert_session_history
from Dialogflow_webhook.request_manager import (
    get_personal_info,
    prepare_history,
    create_webhook_response,
)


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
app.register_blueprint(blueprint)


@app.route(route="webhook")
def webhook(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    request_json = req.get_json()
    prompt, session_id = get_personal_info(request_json)
    history = prepare_history(request_json)
    respuesta, _ = respond_message(prompt, history)
    logging.info("Usuario: %s", prompt)
    logging.info("Chatbot: %s", respuesta)

    with create_postgres_connection() as conn:  # pylint: disable=E1129
        upsert_session_history(conn, session_id, history)

    res = create_webhook_response(respuesta, history)

    return res
