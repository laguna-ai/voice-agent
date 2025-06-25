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
from AI.whisper import transcribe_audio_azure
from AI.tts import text_to_speech_azure


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


@app.route(route="transcribe", methods=["POST"])
def transcribe(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint para transcribir audio usando Azure OpenAI Whisper.
    Espera un archivo de audio en el campo 'file' del formulario.
    """
    try:
        audio_file = req.files.get("file")
        if not audio_file:
            return func.HttpResponse(
                "No se proporcionó archivo de audio.", status_code=400
            )
        texto = transcribe_audio_azure(audio_file)
        return func.HttpResponse(texto, status_code=200)
    except KeyError:
        return func.HttpResponse(
            "Campo 'file' no encontrado en la solicitud.", status_code=400
        )
    except ValueError as ve:
        return func.HttpResponse(f"Error de valor: {str(ve)}", status_code=400)


@app.route(route="tts", methods=["POST"])
def tts(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint para convertir texto a audio usando Azure OpenAI TTS.
    Espera un JSON con el campo 'text'.
    """
    try:
        data = req.get_json()
        text = data.get("text")
        if not text:
            return func.HttpResponse("No se proporcionó texto.", status_code=400)
        audio = text_to_speech_azure(text)
        return func.HttpResponse(audio, status_code=200, mimetype="audio/mpeg")
    except KeyError:
        return func.HttpResponse(
            "Campo 'text' no encontrado en la solicitud.", status_code=400
        )
    except ValueError as ve:
        return func.HttpResponse(f"Error de valor: {str(ve)}", status_code=400)
