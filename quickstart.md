# Quickstart using a flask-boiler

This page is adapted from [Quickstart using a server client library](https://cloud.google.com/firestore/docs/quickstart-servers)
 released under [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/). 
 Some code samples are also adapted from the source, 
 which are released under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). 
 This page is part of a repository under MIT License, 
 but does not override some licensing conditions of
 the Google's quickstart guide. 
 Please refer to these license for more information.  

### Retrieve credentials 

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
to your project directory and specify the path in ```boiler.yaml``` 
in your current working directory. 

```yaml
app_name: "<Your Firebase App Name>"
debug: True
testing: True
certificate_filename: "<File Name of Certificate JSON>"
```


In ```__init__``` of your project source root: 
```python
from flask_boiler.context import Context as CTX

CTX.load()
```

## Declare a Domain Model

In ```models.py```, create a model, 

```python
from flask_boiler.domain_model import DomainModel
from flask_boiler import attrs

class City(DomainModel):

    city_name = attrs.bproperty()
    country = attrs.bproperty()
    capital = attrs.bproperty()

    class Meta:
        collection_name = "City"
```

Create Attribute objects for your domain model. 
These will be converted to a Marshmallow Schema 
for serialization and deserialization. 

Now, you can create the object and assign values to it 

```python
# Creates an object with reference: "City/SF" 
#   (but not saved to database)
sf = City.new(
    doc_id="SF", 
    city_name='San Francisco', 
    city_state ='CA', 
    country='USA', 
    regions=['west_coast', 'norcal']
)        

# Assigns value to the newly created object 
sf.capital = False

# Saves to firestore "City/SF" 
sf.save()
```

### Read data

To quickly verify that you've added data to Cloud Firestore, 
use the data viewer in the [Firebase console](https://console.firebase.google.com/project/_/database/firestore/data).

You can get all documents that is a subclass of City where country equals USA: 
```python
for city in City.where(country="USA"):
    ...
```

