"""

"""

import json
import logging
import os
import time

import requests
from azlog import AzLogger

logger = AzLogger(__name__)
logger.setLevel(logging.INFO)

# Constants
FABRIC_API_URL = "https://api.fabric.microsoft.com/v1"


def poll_lro_get_status(location_url: str, headers: dict, delay_second: int):
    """
    Poll the status of a Long Running Operation (LRO) in Microsoft Fabric.

    This function repeatedly checks the status of an ongoing operation until it is complete
    or encounters an error.

    Parameters
    ----------
    location_url : str
        The URL to poll for the operation status.
    headers : dict
        The headers containing authorization tokens and other required information.
    delay_second : int
        The delay in seconds between each polling request.

    Returns
    -------
    None

    """
    while True:
        status_response = requests.get(location_url, headers=headers, timeout=120)
        status_code = status_response.status_code
        if status_code == 200:
            logger.command("Git Sync completed")
            break
        status = status_response.json().get("Status", "Unknown")
        if status not in ("NotStarted", "Running"):
            break
        logger.command("GIT sync operation is still in progress...")
        time.sleep(delay_second)  # Wait for 10 seconds before polling again


def get_workspcehead(workspace_id: str, token):
    """
    Retrieve the latest Git status for a Fabric workspace.

    The status indicates changes to the item(s) since the last workspace and remote branch sync.
    If both locations were modified, the API flags a conflict.

    https://learn.microsoft.com/en-us/rest/api/fabric/core/git/get-status


    Parameters
    ----------
    workspace_id : str
        The ID of the Fabric workspace.
    token : str
        The Entra ID access token.

    Returns
    -------
    str or None
        The latest workspace commit ID if successful, or None if an error occurs.
    """
    try:
        logger.command("Retriving latest Workspace commit ID")
        url = f"{FABRIC_API_URL}/workspaces/{workspace_id}/git/status"
        headers = {"Authorization": f"Bearer {token}"}

        response = requests.get(url, headers=headers, timeout=120)
        # response.raise_for_status()
        workspaceheadid = response.json().get("workspaceHead")
        logger.command(f"Latest workspacehead: {workspaceheadid}")
        return workspaceheadid
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get Git status: {e}")
        os._exit(1)
        return None


def update_from_git(workspace_id: str, token):
    """
    Update a Fabric workspace from its connected remote Git repository.

    This function synchronizes changes from the remote Git repository to the workspace,
    resolving any conflicts using a specified policy.

    https://learn.microsoft.com/en-us/rest/api/fabric/core/git/update-from-git

    Parameters
    ----------
    workspace_id : str
        The ID of the Fabric workspace.
    token : str
        The Entra ID access token.

    Returns
    -------
    None
    """
    try:
        logger.command(
            f"Starting the UpateSync operation for the workspace {workspace_id}"
        )

        headers = {"Authorization": f"Bearer {token}"}
        # Get remoteCommitHash for the git
        gitstatusurl = f"{FABRIC_API_URL}/workspaces/{workspace_id}/git/status"
        response = requests.get(gitstatusurl, headers=headers, timeout=120)

        if response.status_code == 200:
            git_status = response.json()
            remote_commit_hash = git_status["remoteCommitHash"]
            workspace_head = git_status["workspaceHead"]
            logger.command(f"Remote Commit Hash: {remote_commit_hash}")
            logger.command(f"Workspace Head: {workspace_head}")

            # Define the update parameters with conflict resolution policy
            update_params = {
                "workspaceHead": workspace_head,
                "remoteCommitHash": remote_commit_hash,
                "conflictResolution": {
                    "conflictResolutionType": "Workspace",
                    "conflictResolutionPolicy": "PreferRemote",
                },
                "options": {"allowOverrideItems": True},
            }

            # Update the workspace
            updateworkspaceurl = (
                f"{FABRIC_API_URL}/workspaces/{workspace_id}/git/updateFromGit"
            )

            update_response = requests.post(
                updateworkspaceurl, headers=headers, json=update_params, timeout=120
            )

            if update_response.status_code == 200:
                git_status = update_response.json()
                logger.command(
                    f"Workspace {workspace_id} synced successfully with RemoteSync conflict resolution!"
                )
                # logger.command(git_status)
            elif update_response.status_code == 202:
                logger.command("Request accepted, update workspace is in progress.")
                # time.sleep(10)
                location_url = update_response.headers.get("Location")
                # operation = update_response.headers.get("x-ms-operation-id")
                logger.command(
                    f"Polling URL to track operation status is {location_url}"
                )
                # logger.command(f"Polling URL to track operation status is {operation}")
                time.sleep(20)
                poll_lro_get_status(location_url, headers, 10)

            else:
                logger.error(
                    f"Failed to update the workspace. Status Code: {update_response.status_code} - {update_response.text}"
                )
                os._exit(1)
        else:
            logger.error(
                f"Failed to retrieve Git status. Status Code: {response.status_code} This is the Error {response.json()}"
            )
            os._exit(1)

    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred: {e}")
        os._exit(1)


def commit_to_git(workspace_id: str, workspace_head: str, token):
    """
    Commits the changes made in the workspace to the connected remote branch.


    https://learn.microsoft.com/en-us/rest/api/fabric/core/git/commit-to-git

     Parameters
    ----------
    workspace_id : str
        The ID of the Fabric workspace.
    workspace_head : str
        The current head commit ID of the workspace.
    token : str
        The Entra ID access token.

    Returns
    -------
    None

    """
    try:
        logger.command(
            f"Initialize committ of all changed items for workspace {workspace_id}"
        )
        commit_url = f"{FABRIC_API_URL}/workspaces/{workspace_id}/git/commitToGit"
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "mode": "All",
            "workspaceHead": workspace_head,
            "commitMessage": "Committing all items from Fabric workspace to Git",
        }
        response = requests.post(commit_url, headers=headers, json=payload, timeout=120)

        if response.status_code == 200:
            logger.command("Successfully committed all items to Git.")
        elif response.status_code == 400:
            logger.warning("No Changed Items to commmit")
        else:
            logger.error(f"Failed to commit items. Status code: {response.status_code}")
            os._exit(1)
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to commit items: {e}")
        os._exit(1)
