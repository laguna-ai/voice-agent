import logging
from RAG.SysPrompt import build_sysPrompt
import copy
import azure.functions as func
import json


def get_personal_info(request_json):

    logging.info("## JSON CONTENTS ##: %s", str(request_json))
    prompt = request_json["text"]
    session_id = request_json["sessionInfo"]["session"].split("/")[-1]

    return prompt, session_id


def prepare_history(request_json):
    try:
        history = request_json["sessionInfo"]["parameters"]["context"]
    except KeyError:
        history = copy.deepcopy(build_sysPrompt("Pepito"))
    return history


def create_webhook_response(respuesta, history):
    # Construimos la respuesta JSON manualmente y la retornamos usando func.HttpResponse
    response_body = json.dumps(
        {
            "sessionInfo": {
                "parameters": {
                    "context": history,
                }
            },
            "fulfillmentResponse": {"messages": [{"text": {"text": [respuesta]}}]},
        }
    )

    return func.HttpResponse(
        body=response_body, status_code=200, mimetype="application/json"
    )
