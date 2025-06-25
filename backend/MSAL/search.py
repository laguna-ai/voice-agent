# get a list of files in onedrive for Redimed folder
from .authentication import get_token
import requests
import json
import io
import pandas as pd

graph_url = "https://graph.microsoft.com/v1.0"
site_ID = "lagunaai.sharepoint.com,9a2e4810-7465-473b-831b-62c1032b1015,4e47b86c-7705-4994-a0b3-861e3fcdcaa9"
# lista de resúmenes de conversaciones de Learnia
list_ID = "fc2df33e-880f-41a7-b623-eff93a22c8bd"


def post_request(url, body):
    token = get_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, data=json.dumps(body), timeout=10)
    return response


def add_to_list(data, site_id=site_ID, list_id=list_ID):
    url = f"{graph_url}/sites/{site_id}/lists/{list_id}/items"
    response = post_request(url, {"fields": data})
    if response.status_code == 201:
        print("Item agregado exitosamente.")
        # print(json.dumps(response.json(), indent=4))
    else:
        print(f"Error al agregar el item: {response.status_code}")
        # print(response.text)


def get_response(url):
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers, timeout=10)
    return response


# Get dataframe from excel file with known id


def get_df(file_id, site_id=site_ID):
    url = f"{graph_url}/sites/{site_id}/drive/items/{file_id}/content"
    response = get_response(url)
    df = pd.read_excel(io.BytesIO(response.content))
    return df


# Función para obtener todos los IDs de archivos y carpetas
def get_all_file_ids(site_id=site_ID):
    ids = []
    # Cola ahora almacena tuplas (folder_id, ruta_padre)
    queue = [("root", "")]  # Iniciamos con la raíz y ruta vacía

    while queue:
        current_folder_id, parent_path = queue.pop(0)
        url = f"{graph_url}/sites/{site_id}/drive/items/{current_folder_id}/children"

        while url:
            response = get_response(url)
            if response.status_code != 200:
                print(f"Error obteniendo items: {response.status_code}")
                url = None
                continue

            data = response.json()
            for item in data.get("value", []):
                item_id = item.get("id")
                item_name = item.get("name", "")

                # Construir ruta completa
                current_path = (
                    f"{parent_path}/{item_name}" if parent_path else item_name
                )
                print(f"Ruta: {current_path}")  # Imprimimos la ruta

                ids.append(item_id)

                # Si es carpeta, añadir a la cola con su ruta
                if "folder" in item:
                    queue.append((item_id, current_path))

            # Manejar paginación
            url = data.get("@odata.nextLink")

    return ids


# En el archivo sharepoint_utils.py
def get_all_files_info(site_id=site_ID):
    """Obtiene todos los archivos y carpetas con su metadata completa"""
    items_info = []
    queue = [("root", "")]  # (folder_id, parent_path)

    while queue:
        current_folder_id, parent_path = queue.pop(0)
        url = f"{graph_url}/sites/{site_id}/drive/items/{current_folder_id}/children"

        while url:
            response = get_response(url)
            if response.status_code != 200:
                print(f"Error obteniendo items: {response.status_code}")
                break

            data = response.json()
            for item in data.get("value", []):
                # Construir metadata básica
                item_info = {
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "type": "folder" if "folder" in item else "file",
                    "path": (
                        f"{parent_path}/{item.get('name')}"
                        if parent_path
                        else item.get("name")
                    ),
                }

                # Añadir información específica para archivos
                if item_info["type"] == "file":
                    item_info.update(
                        {
                            "file_extension": item.get("file", {})
                            .get("mimeType", "")
                            .split(".")[-1],
                            "size": item.get("size", 0),
                        }
                    )

                items_info.append(item_info)

                # Si es carpeta, añadir a la cola para procesar hijos
                if item_info["type"] == "folder":
                    queue.append((item_info["id"], item_info["path"]))

            # Manejar paginación
            url = data.get("@odata.nextLink")

    return items_info


def get_file_content(file_id, site_id=site_ID):
    """Obtiene el contenido binario de un archivo"""
    url = f"{graph_url}/sites/{site_id}/drive/items/{file_id}/content"
    response = get_response(url)

    if response.status_code == 200:
        return response.content
    elif response.status_code == 404:
        raise FileNotFoundError(f"Archivo no encontrado (ID: {file_id})")
    elif response.status_code == 403:
        raise PermissionError(f"Sin permisos para acceder al archivo (ID: {file_id})")
    elif response.status_code == 401:
        raise ConnectionError("Error de autenticación con SharePoint")
    else:
        raise ConnectionError(
            f"Error {response.status_code} al descargar archivo {file_id}"
        )


# print("Archivos en sitio de Learnia:")
# # Obtener todos los archivos y carpetas
# all_items = get_all_files_info()
# for item in all_items:
#     print(item)
