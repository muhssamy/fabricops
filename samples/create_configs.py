"""
  Create Config Files
  
"""

import argparse
import logging

from azlog import AzLogger

from fabricops import acquire_token_confidential, generate_config_file

logger = AzLogger(__name__)
logger.setLevel(logging.INFO)

parser = argparse.ArgumentParser(description="Create Config File")
parser.add_argument(
    "--WORKSPACE_ID",
    type=str,
    required=True,
    help="Workspace ID Where Lakehouse exists",
)
parser.add_argument(
    "--WORKSPACE_WH_ID",
    type=str,
    required=True,
    help="Workspace ID Where Warehouse exists",
)
parser.add_argument("--CLIENT_ID", type=str, required=True, help="Client ID")
parser.add_argument("--CLIENT_SECRET", type=str, required=True, help="Client Secret")
parser.add_argument("--TENANT_ID", type=str, required=True, help="Tenant ID")
parser.add_argument("--USER_NAME", type=str, required=True, help="Username")
parser.add_argument("--PASSWORD", type=str, required=True, help="Password")
args = parser.parse_args()


WORKSPACE_ID = args.WORKSPACE_ID
CLIENT_ID = args.CLIENT_ID
TENANT_ID = args.TENANT_ID
USERNAME = args.USER_NAME
PASSWORD = args.PASSWORD
CLIENT_SECRET = args.CLIENT_SECRET
WORKSPACE_WH_ID = args.WORKSPACE_WH_ID

logger.command(f"Workspace ID {WORKSPACE_ID}")
logger.command(f"UserName {USERNAME}")


if __name__ == "__main__":
    access_token = acquire_token_confidential(
        TENANT_ID, CLIENT_ID, USERNAME, PASSWORD, CLIENT_SECRET
    )
    generate_config_file(WORKSPACE_ID, WORKSPACE_WH_ID, access_token)

    logger.command("Program Completed")
