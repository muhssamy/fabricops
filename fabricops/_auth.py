"""
    Acquire Tokens
    
    Acquire Entra Id Tokens Using a user(email) without multi-factor Authentication
"""


import logging
import msal
from azlog import AzLogger

logger = AzLogger(__name__)
logger.setLevel(logging.INFO)

# Constants


def acquire_token_confidential(
    tenant_id: str,
    client_id: str,
    user_name: str,
    password: str,
    client_credential: str,
):
    """
    Obtain an Entra ID token using a confidential client (service principal) and user credentials.

    This function uses MSAL (Microsoft Authentication Library) to authenticate using a service principal
    (confidential client) and the provided user credentials.

    Parameters
    ----------
    tenant_id : str
        The Azure AD tenant ID.
    client_id : str
        The client ID of the service principal.
    user_name : str
        The username (email) of the user.
    password : str
        The password of the user.
    client_credential : str
        The secret of the service principal.

    Returns
    -------
    str or None
        The Entra ID access token if authentication is successful, or None otherwise.
    """
    logger.command("Generating token for Fabric APIs")

    # Initialize the MSAL Confidential client
    authority = f"https://login.microsoftonline.com/{tenant_id}"

    app = msal.ConfidentialClientApplication(
        client_id, authority=authority, client_credential=client_credential
    )

    scopes = ["https://api.fabric.microsoft.com/.default"]

    result = app.acquire_token_by_username_password(user_name, password, scopes)

    if "access_token" in result:
        access_token = result["access_token"]
    else:
        access_token = None
    return access_token


def acquire_token_public(tenant_id: str, client_id: str, user_name: str, password: str):
    """
    Obtain an Entra ID token using a public client (user authentication) and user credentials.

    This function uses MSAL to authenticate using the provided user credentials in a public client scenario.

    Parameters
    ----------
    tenant_id : str
        The Azure AD tenant ID.
    client_id : str
        The client ID for the public client application.
    user_name : str
        The username (email) of the user.
    password : str
        The password of the user.

    Returns
    -------
    str or None
        The Entra ID access token if authentication is successful, or None otherwise.
    """
    logger.command("Generating token for Fabric APIs")

    # Initialize the MSAL Confidential client
    authority = f"https://login.microsoftonline.com/{tenant_id}"

    app = msal.PublicClientApplication(client_id, authority=authority)

    scopes = ["https://api.fabric.microsoft.com/.default"]

    result = app.acquire_token_by_username_password(user_name, password, scopes)

    if "access_token" in result:
        access_token = result["access_token"]
    else:
        access_token = None
    return access_token
