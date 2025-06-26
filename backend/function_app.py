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
import base64
import io

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
    Espera un JSON con el campo 'audio' en base64.
    """

    try:
        req_body = req.get_json()
        audio_base64 = req_body.get("audio")
        if not audio_base64:
            logging.info("No se proporcionó audio en base64.")
            return func.HttpResponse(
                "No se proporcionó audio en base64.", status_code=400
            )
        audio_binary = base64.b64decode(audio_base64)
        audio_stream = io.BytesIO(audio_binary)
        audio_stream.name = "audio.webm"  # O "audio.wav" si grabas en wav
        texto = transcribe_audio_azure(audio_stream)
        return func.HttpResponse(texto, status_code=200)
    except KeyError:
        logging.info("Campo 'audio' no encontrado en la solicitud.")
        return func.HttpResponse(
            "Campo 'audio' no encontrado en la solicitud.", status_code=400
        )
    except ValueError as ve:
        logging.info("Error de valor %s", ve)
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
