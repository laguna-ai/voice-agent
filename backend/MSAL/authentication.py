# authentication constnats and function
import os
from msal import ConfidentialClientApplication

client_secret = os.environ["CLIENT_SECRET"]
app_id = "db49d90d-cf46-4104-8fb0-f0c3d0a417f1"
scopes = ["https://graph.microsoft.com/.default"]
tenant = "29e1c754-dbb2-4730-92b2-29ab15b7d888"


def get_token():
    token = None

    app = ConfidentialClientApplication(
        client_id=app_id,
        client_credential=client_secret,
        authority=f"https://login.microsoftonline.com/{tenant}",
    )

    result = app.acquire_token_silent(scopes=scopes, account=None)

    if not result:
        result = app.acquire_token_for_client(scopes=scopes)
        token = result["access_token"]
        print("New token generated")  # , token)
    elif "access_token" in result:
        token = result["access_token"]
        print("Access token already acquired:")  # , token)
    else:
        print("Error:", result)
    return token
