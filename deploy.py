"""
See: https://cloud.google.com/functions/docs/deploying/api

gcloud functions deploy to_trigger --runtime python37 --trigger-event providers/cloud.firestore/eventTypes/document.create --trigger-resource "projects/flask-boiler-testing/databases/(default)/documents/gcfTest/{gcfTestDocId}"
"""
from datetime import datetime

if __name__ == "__main__":
    """
    Ref: https://cloud.google.com/functions/docs/reference/rest/v1/projects.locations.functions/generateUploadUrl
    """

    import googleapiclient.discovery
    from google.oauth2 import service_account
    from flask_boiler.config import Config

    config = Config.load()

    SCOPES = ['https://www.googleapis.com/auth/cloud-platform']

    # client = Client.from_service_account_json(config.FIREBASE_CERTIFICATE_JSON_PATH)
    credentials = service_account.Credentials.from_service_account_file(
        config.FIREBASE_CERTIFICATE_JSON_PATH, scopes=SCOPES)

    # Update an existing project
    # project = client.fetch_project(config.APP_NAME)

    # Project name here projects/{project_id}/locations/{location_id}
    project_id = config.APP_NAME
    location_id = "us-central1"
    parent = f"projects/{project_id}/locations/{location_id}"

    functions_service: googleapiclient.discovery.Resource = googleapiclient.discovery.build(
        'cloudfunctions', 'v1', credentials=credentials)
    resp = functions_service.projects().locations().functions().generateUploadUrl(
        parent=parent).execute()

    upload_url = resp['uploadUrl']

    # http://googleapis.github.io/google-api-python-client/docs/dyn/cloudfunctions_v1.projects.locations.functions.html

    import requests

    from git import Repo

    repo = Repo()

    import os

    file_path = os.path.join(os.path.curdir, 'repo.zip')
    with open(file_path, 'wb') as fp:
        repo.archive(fp, format='zip')
    with open(file_path, 'rb') as fp:
        resp = requests.request(
            'PUT', url=upload_url, headers={
                'x-goog-content-length-range': "0,104857600",
                'content-type': 'application/zip',
            }, files={
                'only': fp
            }
        )

    print(resp)

    print(resp.content)

    import main
    mediator = main.to_trigger

    def configurations(*, env_vars: dict, resource: str, event_type: str,
                       description: str="", labels: dict,
                       available_memory_mb: int = 256, timeout: str = '540s',
                       entry_point: str = None, name: str, upload_url: str):
        """
        Docstrings adapted from Google documentations
        Ref:

        :param env_vars:
        :param resource: Required. The resource(s) from which to observe events, for example,
            `projects/_/buckets/myBucket`.

            Not all syntactically correct values are accepted by all services. For
            example:

            1. The authorization model must support it. Google Cloud Functions
               only allows EventTriggers to be deployed that observe resources in the
               same project as the `CloudFunction`.
            2. The resource type must match the pattern expected for an
               `event_type`. For example, an `EventTrigger` that has an
               `event_type` of "google.pubsub.topic.publish" should have a resource
               that matches Google Cloud Pub/Sub topics.

            Additionally, some services may support short names when creating an
            `EventTrigger`. These will always be returned in the normalized "long"
            format.

            See each *service's* documentation for supported formats.
            "service": "A String",
            The hostname of the service that should be observed.

            If no string is provided, the default service implementing the API will
            be used. For example, `storage.googleapis.com` is the default for all
            event types in the `google.storage` namespace.
        :param event_type:
         Required. The type of event to observe. For example:
            `providers/cloud.storage/eventTypes/object.change` and
            `providers/cloud.pubsub/eventTypes/topic.publish`.

            Event types match pattern `providers/*/eventTypes/*.*`.
            The pattern contains:

            1. namespace: For example, `cloud.storage` and
               `google.firebase.analytics`.
            2. resource type: The type of resource on which event occurs. For
               example, the Google Cloud Storage API includes the type `object`.
            3. action: The action that generates the event. For example, action for
               a Google Cloud Storage Object is 'change'.
            These parts are lower case.
        :param description: User-provided description of a function.
        :param labels: Labels associated with this Cloud Function.
        :param available_memory_mb: The amount of memory in MB available for a function.
         Defaults to 256MB.
        :param timeout: The function execution timeout. Execution is considered failed and
        can be terminated if the function is not completed at the end of the
        :param name: A user-defined name of the function. Function names must be unique
         globally and match pattern `projects/*/locations/*/functions/*`
        timeout period. Defaults to 60 seconds. duration must end with 's'.
        :param entry_point: The name of the function (as defined in source code) that will be
        executed. Defaults to the resource name suffix, if not specified. For
        backward compatibility, if function with given name is not found, then the
        system will try to use function named "function".
=        :param upload_url:
        :return:
        """

        if env_vars is None:
            env_vars = dict()

        return {
            "eventTrigger": {
                "resource": "projects/flask-boiler-testing/databases/(default)/documents/gcfTest/{gcfTestDocId}",
                "eventType": "providers/cloud.firestore/eventTypes/document.write"
            },
            "labels": labels,
            "availableMemoryMb": available_memory_mb,
            "description": "A String",  #
            "maxInstances": 42,
            "entryPoint": entry_point,
            "name": name,
            "environmentVariables": env_vars,
            "sourceUploadUrl": upload_url,
            "serviceAccountEmail": credentials.service_account_email,
            "timeout": timeout,
            "ingressSettings": "ALLOW_ALL",
            "runtime": "python37",
        }

    entry_point = 'to_trigger'
    name = f'projects/{project_id}/locations/{location_id}/functions/{entry_point}'

    body = configurations(
        env_vars=dict(),
        entry_point=entry_point,
        resource=mediator.resource,
        event_type=mediator.TRIGGER_EVENT_TYPE,
        upload_url=upload_url,
        labels=dict(),
        name=name
    )

    resp = functions_service.projects().locations().functions().get(
        name=name).execute()
    print(resp)

    if resp == dict():
        resp = functions_service.projects().locations().functions().create(
            location=parent, body=body
            ).execute()
    else:
        resp = functions_service.projects().locations().functions().patch(
            name=name, body=body
        ).execute()
    print(resp)
