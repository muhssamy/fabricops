# fabricops

This package is built on top of this [repository](https://github.com/PowerBiDevCamp/FabConWorkshopSweden).
I have enhanced it to be more suitable for Azure Pipelines and Added New Fuctions for DevOps Pipeline Activies.

## Description

This package is designed to be used within an Azure DevOps Pipeline to update a Fabric Workspace from a Git repository using a user with an email and password. It supports both public client and confidential client applications. For more information about the differences, click [here](https://learn.microsoft.com/en-us/entra/msal/msal-client-applications)

**Note** This is currently the only available method because Microsoft does not support service principals for these operations. Once it becomes available, please use it. For more information, check Microsoft Entra supported identities [here](https://learn.microsoft.com/en-us/rest/api/fabric/core/git/update-from-git).

Another method is to schedule a notebook on Fabric running under the authority of a user who is a contributor or higher in an administration workspace using [this](https://semantic-link-labs.readthedocs.io/en/stable/sempy_labs.html#sempy_labs.update_from_git) libirary.

### Install

To install the package, use the following command:

```python
pip install fabricops
```

## Usage

### 1- Create Config File For Pipeline Contents

you can add the following tasks in your `azure-pipeline.yml` to create the files

```yml

- bash: 'python -m pip install fabricops --no-cache-dir --upgrade'
displayName: 'Install FabricOps'

- task: PythonScript@0
displayName: 'Create Config File'
inputs:
    scriptSource: 'filePath'
    scriptPath: '$(Build.SourcesDirectory)/create_configs.py' 
    arguments: '--WORKSPACE_ID $(WORKSPACE_ID) --WORKSPACE_WH_ID $(WORKSPACE_WH_ID) --CLIENT_ID $(CLIENTID) --TENANT_ID $(TENANTID) --USER_NAME $(email) --PASSWORD $(password) --CLIENT_SECRET $(CLIENTSECRET)'
    workingDirectory: '$(Build.SourcesDirectory)'

# Step 3: Publish the file as a pipeline artifact
- task: PublishPipelineArtifact@1
inputs:
    targetPath: 'linkedservice-config.json'
    artifact: 'config-file'
displayName: 'Publish created file as artifact'

- task: DownloadPipelineArtifact@2
inputs:
    artifact: 'config-file'
    path: '$(Pipeline.Workspace)'
displayName: 'Download created file'

```

and the content of `create_configs.py` exists in the Samples Folder.

### 2- To Update Fabric Pipelines

you can use the following task

```yml
- script: |
      python3 -c "from fabricops import update_linked_services; update_linked_services('$(Pipeline.Workspace)/linkedservice-config.json', '$(Build.SourcesDirectory)')"
    displayName: 'PY Modify JSON Files'

```

### 3- Update Workspace From Git Repo

Now you can update your Fabric Workspace From connected Repo. `update.py` in samples Folder

```yml

- task: PythonScript@0
displayName: 'Run a Python script'
inputs:
    scriptSource: 'filePath'
    scriptPath: '$(Build.SourcesDirectory)/update.py'
    arguments: '--WORKSPACE_ID $(WORKSPACE_ID) --CLIENT_ID $(CLIENTID) --TENANT_ID $(TENANTID) --USER_NAME $(email) --PASSWORD $(password) --CLIENT_SECRET $(CLIENTSECRET)'
    workingDirectory: '$(Build.SourcesDirectory)'

```
