"""
   Call this functions to create Config file
   
   This config file will be used for linked-service values replacement
   
"""

import json
import logging
import os

import requests
from azlog import AzLogger

logger = AzLogger(__name__)
logger.setLevel(logging.INFO)

FABRIC_API_URL = "https://api.fabric.microsoft.com/v1"


def generate_lakehouse_config(workspace_id: str, token: str) -> dict:
    """
    Fetch only 'Lakehouse' items from the workspace and return a structured dictionary with relevant data.

    Parameters
    ----------
    workspace_id : str
        The ID of the workspace for which the items need to be fetched.
    token : str
        The authentication token to access the Microsoft Fabric API.

    Returns
    -------
    dict
        A dictionary containing Lakehouse items.
    """

    def fetch_workspace_items() -> list:
        url = f"{FABRIC_API_URL}/workspaces/{workspace_id}/items"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers, timeout=120)
        response.raise_for_status()

        items = response.json().get("value", [])
        return [item for item in items if item["type"] == "Lakehouse"]

    # Prepare data structure
    lakehouse_data = {}
    filtered_items = fetch_workspace_items()

    for item in filtered_items:
        lh_key = f"{item['displayName']}"
        lakehouse_data[lh_key] = {
            "typeProperties": {
                "artifactId": item["id"],
                "workspaceId": workspace_id,
                "rootFolder": "Tables",
            },
            "name": item["displayName"],
        }

    return lakehouse_data


def generate_warehouse_config(workspace_id: str, token: str) -> dict:
    """
    Fetch 'Warehouse' items from the workspace, retrieve their details, and return a structured dictionary.

    Parameters
    ----------
    workspace_id : str
        The ID of the workspace for which the items need to be fetched.
    token : str
        The authentication token to access the Microsoft Fabric API.

    Returns
    -------
    dict
        A dictionary containing Warehouse items.
    """

    def fetch_workspace_items() -> list:
        url = f"{FABRIC_API_URL}/workspaces/{workspace_id}/items"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers, timeout=120)
        response.raise_for_status()

        items = response.json().get("value", [])
        return [item for item in items if item["type"] == "Warehouse"]

    def fetch_warehouse_details(warehouse_id: str) -> dict:
        url = f"{FABRIC_API_URL}/workspaces/{workspace_id}/warehouses/{warehouse_id}"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers, timeout=120)
        response.raise_for_status()

        return response.json()

    # Prepare data structure
    warehouse_data = {}
    filtered_items = fetch_workspace_items()

    for item in filtered_items:
        warehouse = fetch_warehouse_details(item["id"])
        wh_key = f"{item['displayName']}"
        warehouse_data[wh_key] = {
            "typeProperties": {
                "artifactId": warehouse["id"],
                "endpoint": warehouse["properties"]["connectionString"],
                "workspaceId": workspace_id,
            },
            "objectId": warehouse["id"],
            "name": warehouse["displayName"],
        }

    return warehouse_data


def generate_config_file(
    lakehouse_workspace_id: str, warehouse_workspace_id: str, token: str
) -> None:
    """
    Run `generate_lakehouse_config` for the Lakehouse workspace and `generate_warehouse_config`
    for the Warehouse workspace, then merge the results into a single JSON object without
    any outer keys, such as 'warehouse' or 'lakehouse'.

    Parameters
    ----------
    lakehouse_workspace_id : str
        The workspace ID containing only 'Lakehouse' items.
    warehouse_workspace_id : str
        The workspace ID containing only 'Warehouse' items.
    token : str
        The authentication token.

    Returns
    -------
    None
        Saves the merged result to `linkedservice-config.json`.
    """

    # Run the function for Lakehouse items
    lakehouse_data = generate_lakehouse_config(lakehouse_workspace_id, token)

    # Run the function for Warehouse items
    warehouse_data = generate_warehouse_config(warehouse_workspace_id, token)

    # Merge the two dictionaries into one (no outer keys like 'warehouse' or 'lakehouse')
    merged_result = {**warehouse_data, **lakehouse_data}

    # Delete the file if it exists
    filename = "linkedservice-config.json"
    if os.path.exists(filename):
        os.remove(filename)

    # Save the merged result to the JSON file
    with open(filename, "w") as outfile:
        json.dump(merged_result, outfile, indent=4)

    logger.command(f"Linked service config file created: {filename}")
