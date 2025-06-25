import requests
from typing import Optional
from configuration import config_AOAI

def text_to_speech_azure(text: str, voice: str = "alloy", model: str = None) -> Optional[bytes]:
    """
    Convierte texto a audio usando Azure OpenAI TTS.
    Args:
        text (str): Texto a convertir en audio.
        voice (str): Voz a utilizar (por defecto 'alloy').
        model (str): Modelo a utilizar (por defecto el de config_AOAI).
    Returns:
        bytes: Audio en binario (formato WAV/MP3 según configuración del endpoint).
    """
    tts_cfg = config_AOAI["tts"]
    endpoint = tts_cfg["endpoint_root"]
    api_key = tts_cfg["key"]
    tts_deployment = model or tts_cfg["deployment"]
    api_version = tts_cfg["api_version"]
    if not endpoint or not api_key:
        raise ValueError("Faltan variables de entorno AOAI_TTS_ENDPOINT o AOAI_TTS_KEY")

    url = f"{endpoint}/openai/deployments/{tts_deployment}/audio/speech?api-version={api_version}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": tts_deployment,
        "input": text,
        "voice": voice
    }
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    if response.status_code == 200:
        return response.content
    else:
        raise requests.exceptions.HTTPError(f"Error en TTS Azure: {response.status_code} - {response.text}")
