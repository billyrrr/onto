# Quickstart using a flask-boiler

This page is adapted from [Quickstart using a server client library](https://cloud.google.com/firestore/docs/quickstart-servers)
 released under [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/). 
 Some code samples are also adapted from the source, 
 which are released under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). 
 This page is part of a repository under MIT License, 
 but does not override some licensing conditions of
 the Google's quickstart guide. 
 Please refer to these license for more information.  
 
## Before you begin 

- Select or create a GCP project:
    [Project Selector Page](https://console.cloud.google.com/projectselector2/home/dashboard?_ga=2.78791382.-378732223.1566339304)
   
## Create a Cloud Firestore in Native mode database

If this is a new project, you need to create a Cloud Firestore database instance.

1. Go to [Cloud Firestore Viewer](https://console.cloud.google.com/firestore/data?_ga=2.250628420.-378732223.1566339304) .
2. From the Select a database service screen, choose Cloud Firestore in Native mode.

3. Select a [location](https://cloud.google.com/firestore/docs/locations#types) for your Cloud Firestore.

    This location setting is your project's [default Google Cloud Platform (GCP) resource location](https://cloud.google.com/firestore/docs/locations#default-cloud-location). 

    Note that this location will be used for GCP services in your project that require a location setting, 
specifically, your default [Cloud Storage](https://cloud.google.com/storage/docs) bucket 
and your [App Engine](https://cloud.google.com/appengine/docs/) app (which is required if you use Cloud Scheduler).
    
    > **Warning**: After you set your project's default GCP resource location, you cannot change it.

4. Click Create Database.
When you create a Cloud Firestore project, it also enables the API in the [Cloud API Manager](https://console.cloud.google.com/projectselector/apis/api/firestore.googleapis.com/overview?_ga=2.258762056.-378732223.1566339304).

## Set up authentication

To run the client library, you must first set up authentication by creating a service account and setting an environment variable.

GCP CONSOLE
1. In the GCP Console, go to the **Create service account** key page.

    Go to [Create Service Account Key Page](https://console.cloud.google.com/apis/credentials/serviceaccountkey?_ga=2.86663898.-378732223.1566339304)

2. From the **Service account** list, select **New service account**.

3. In the **Service account name** field, enter a name.

4. From the **Role** list, select **Project > Owner**.

    > Note: The **Role** field authorizes your service account to access resources. You can view and change this field later by using the [GCP Console](https://console.cloud.google.com/?_ga=2.81399125.-378732223.1566339304). If you are developing a production app, specify more granular permissions than **Project > Owner**. For more information, see [granting roles to service accounts](https://cloud.google.com/iam/docs/granting-roles-to-service-accounts).

5. Click Create. A JSON file that contains your key downloads to your computer.


 
### Add flask-boiler and the server client library to your app

Add the required dependencies and client libraries to your app.

In your project's requirements.txt, 

```

# Append to requirements, unless repeating existing requirements

google-cloud-firestore
flask-boiler  # Not released to pypi yet 

```

Configure virtual environment 
```
pip install virtualenv
virtualenv env
source env/bin/activate
```

In your project directory, 

```pip install -r requirements.txt```

### Initialize

Provide authentication credentials to flask-boiler by moving the json certificate file 
to your project directory and pass in the path as argument to ```flask_boiler.config.Config``` in your 
python code. 


In ```__init__``` of your project source root: 
```python
import os

from flask_boiler import context
from flask_boiler import config

Config = config.Config

testing_config = Config(app_name="[YOUR_APP_NAME]",
                        debug=True,
                        testing=True,
                        certificate_path="[PATH]")

CTX = context.Context
CTX.read(testing_config)
```

Replace ```[PATH]``` with the file path of the JSON file that contains your service account key, 
and ```[YOUR_APP_NAME]``` with the name of your firebase app.  

## Add data

First, declare a schema for your data. 

```python

# Creates a schema for serializing and deserializing to firestore database
class TestObjectSchema(schema.Schema):
    
    # Describes how obj.int_a is read from and stored to a document in firestore 
    int_a = fields.Raw()
    int_b = fields.Raw()
```

Next, declare the domain model and initialize all fields to the 
default value. 

```python

# Declares the object 
# Declares the object
TestObject = ClsFactory.create(
    name="TestObject",
    schema=TestObjectSchema,
    # Either MyDomainModelBase (specify cls._collection_id)
    #  or SubclassOfViewModel 
    # TODO: ADD MORE DOCS 
    base=PrimaryObject  
)

```

Now, you can create the object and assign values to it 

```python
# Creates an object with default values with reference: "TestObject/testObjId1" 
#   (but not saved to database)
obj = TestObject.create(doc_id="testObjId1")

# Assigns value to the newly created object 
obj.int_a = 1
obj.int_b = 2

# Saves to firestore "TestObject/testObjId1" 
obj.save()
```

### Read data

To quickly verify that you've added data to Cloud Firestore, 
use the data viewer in the [Firebase console](https://console.firebase.google.com/project/_/database/firestore/data).

To retrieve every object in the collection, 

```python

for obj in TestObject.all():
    print( "doc_id: {} int_a: {}".format(obj.doc_id, obj.int_a) )

```

