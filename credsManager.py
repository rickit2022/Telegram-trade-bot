import json 
from google.cloud import secretmanager

CREDS_JSON_PATH = "creds.json"
# Params for managing and accessing Secret Manager
PROJECT_ID = "" #your_project_id
SECRET_ID = "" #your_secret_name
VERSION = "latest" #your_secret_version

#example usage
    # list_secrets(PROJECT_ID)
    # delete_secret(PROJECT_ID, "APIs")
    # create_secret(PROJECT_ID, secret_id)
    # update_secret_with_alias(PROJECT_ID, secret_id)
    # print_secret(access_secret_version(PROJECT_ID, secret_id, version_id))
    # save_secret(access_secret_version(PROJECT_ID, secret_id, version_id))
    # print(get_key("alpaca","key_id"))
    # print(get_key("alpaca","secret_key"))

def create_secret() -> secretmanager.CreateSecretRequest:
    """
    Create a new secret with the given name. A secret is a logical wrapper
    around a collection of secret versions. Secret versions hold the actual
    secret material. Use this method to overwrite an existing secret by updating
    the creds.json file and create a new secret with the same secret id.
    """
    try:
        with open(CREDS_JSON_PATH, "r") as f:
            data = json.dumps(json.load(f)).encode("UTF-8")

        client = secretmanager.SecretManagerServiceClient()
            
        parent = f"projects/{PROJECT_ID}"
        response = client.create_secret(
            request={
                "parent": parent,
                "secret_id": SECRET_ID,
                "secret": {"replication": {"automatic": {}}},
            }
        )

        version = client.add_secret_version(
            request={"parent": response.name, "payload": {"data": data}}
        )

        print(f"Successfully created new secret at {version.name}")
    except:
        print("Couldn't create secret. Check logs for more info.")

def access_secret_version() -> secretmanager.AccessSecretVersionResponse:
    """
    Access the payload for the given secret version if one exists. The version
    can be a version number as a string (e.g. "5") or an alias (e.g. "latest").
    If returns None, please set project_id and secret_id.
    """
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{PROJECT_ID}/secrets/{SECRET_ID}/versions/{VERSION}"
        response = client.access_secret_version(request={"name": name})
    except:
        return None

    # Verify payload checksum.
    # crc32c = google_crc32c.Checksum()
    # crc32c.update(response.payload.data)
    # if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
    #     print("Data corruption detected.")
    return response

def update_secret_with_alias(alias) -> secretmanager.UpdateSecretRequest:
    """
    Update the metadata about an existing secret.
    """
    client = secretmanager.SecretManagerServiceClient()
    name = client.secret_path(PROJECT_ID, SECRET_ID)
    secret = {"name": name, "version_aliases": {alias: 1}}
    update_mask = {"paths": ["version_aliases"]}
    response = client.update_secret(
        request={"secret": secret, "update_mask": update_mask}
    )
    return response

def list_secrets() -> None:
    """
    List all secrets in the given project.
    """
    client = secretmanager.SecretManagerServiceClient()
    parent = f"projects/{PROJECT_ID}"
    for secret in client.list_secrets(request={"parent": parent}):
        print(secret.name)

def delete_secret() -> None:
    """
    Delete the secret with the given name and all of its versions.
    """
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = client.secret_path(PROJECT_ID, SECRET_ID)

        # Delete the secret.
        client.delete_secret(request={"name": name})
        print("Succesfully deleted secret.")
    except:
        print("Couldn't delete secret.")

def print_secret(response):
    # Print the secret payload.
    #
    # WARNING: Do not print the secret in a production environment - this
    # snippet is showing how to access the secret material.
    payload = response.payload.data.decode("UTF-8")
    print(f"Plaintext: {payload}")

def get_secret(abspath = None):
    """
    Save the secret payload to a file named creds.json by default, you can specified a path to where the file should be saved.
    """
    response = access_secret_version()
    if not response:
        print("Please make sure you configure your project and secret id in credsManager.py")
        return None
     
    path = CREDS_JSON_PATH
    if abspath:
        path = abspath

    with open(path, "w") as f:
        json.dump(json.loads(response.payload.data.decode("UTF-8")), f)
    return True

def get_key(api_name = None, key_name = None):
    with open(CREDS_JSON_PATH, "r") as f:
        data = json.load(f)
        if key_name:
            return data[api_name][key_name]
        return data[api_name]