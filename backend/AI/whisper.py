from openai import AzureOpenAI
from typing import IO
from configuration import config_AOAI
import logging

def transcribe_audio_azure(audio_file: IO, deployment_id: str = None) -> str:
    """
    Transcribe audio using Azure OpenAI Whisper deployment.
    Args:
        audio_file (IO): File-like object containing audio data (e.g., from request.files['file']).
        deployment_id (str): Name of the Azure OpenAI Whisper deployment.
    Returns:
        str: Transcribed text.
    """
    whisper_cfg = config_AOAI["whisper"]
    endpoint = whisper_cfg["endpoint"]
    api_key = whisper_cfg["key"]
    api_version = whisper_cfg["api_version"]
    whisper_deployment = deployment_id or whisper_cfg["deployment"]

    client = AzureOpenAI(
        api_key=api_key, api_version=api_version, azure_endpoint=endpoint
    )
    result = client.audio.transcriptions.create(
        file=audio_file, 
        model=whisper_deployment, 
        language="es"
    )
    # logging  the result for debugging purposes
    logging.info("Transcription result: %s", result)
    return result.text
