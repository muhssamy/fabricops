"""
update pipelines linkedservice

"""

import json
import os


def update_linked_services(config_file_path, root_directory):
    """
    Update linked service properties in pipeline-content.json files based on a configuration file.

    Parameters:
    config_file_path (str): Path to the linkedservice-config.json file.
    root_directory (str): Root directory to search for pipeline-content.json files.
    """

    # Load the configuration file
    with open(config_file_path, "r") as config_file:
        config = json.load(config_file)

    # Function to recursively search and update linkedService properties
    def update_linked_service(obj):
        if isinstance(obj, dict):
            # Check if the object has a 'linkedService' key
            if "linkedService" in obj:
                linked_service = obj["linkedService"]
                if isinstance(linked_service, dict):
                    # Access the name directly from the linked service
                    name = linked_service.get("name", None)
                    linked_service_properties = linked_service.get("properties", {})

                    # Check if the linked service name exists in the config
                    if name and name in config:
                        # Update the typeProperties
                        linked_service_properties["typeProperties"] = config[name][
                            "typeProperties"
                        ]

                        # Check if objectId exists in linked service properties
                        if "objectId" in linked_service:
                            # Update objectId if it exists in the config
                            if "objectId" in config[name]:
                                linked_service["objectId"] = config[name]["objectId"]
                            else:
                                # If objectId does not exist in the config, do nothing
                                pass
                        else:
                            # If the objectId key does not exist, skip any updates
                            pass

            # Recursively call this function for all values in the dictionary
            for key, value in obj.items():
                update_linked_service(value)

        elif isinstance(obj, list):
            # If the object is a list, iterate through each item
            for item in obj:
                update_linked_service(item)

    # Walk through the directory to find all pipeline-content.json files
    for subdir, _, files in os.walk(root_directory):
        for file in files:
            if file == "pipeline-content.json":
                json_file_path = os.path.join(subdir, file)

                # Load the pipeline-content.json file
                with open(json_file_path, "r") as json_file:
                    content = json.load(json_file)

                # Call the function to update linkedService
                update_linked_service(content)

                # Write the modified JSON back to the file
                with open(json_file_path, "w") as json_file:
                    json.dump(content, json_file, indent=2)

    print("All pipeline-content.json files have been processed.")
