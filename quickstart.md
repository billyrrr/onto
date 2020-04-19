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

## Create a Document As View

In this example, we will build a mediator that forwards domain 
models (eg. ```City/TOK```) to view models (eg. ```cityView/TOK```). 
Both data models are stored in a NoSQL datastore, but only the 
view model is intended to be shown to the user. This example 
is similar to a stream converter, but you may build something 
more advanced by leveraging ViewModel.store to query multiple 
domain models across the datastore. The example is located in 
```examples/city```

### Configure Project

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

### Declare a Domain Model

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

```python
class Municipality(City):
    pass


class StandardCity(City):
    city_state = attrs.bproperty()
    regions = attrs.bproperty()
```

You can create subclasses of ```City```. By default, 
they will be stored in the same collection as ```City```. 
Running a query on ```City.where``` will 
query all objects that are of subclass of ```City```: 
```City, Municipality, StandardCity```. A query on 
```Municipality.where``` will query all objects of 
subclass of ```Municipality```: ```Municipality```. 

### Declare View Model

Declare a subclass of `Store` first. This object helps you reference 
domain models by calling `self.store.<domain_model_name>`. In this example, 
you should initialize the store with a snapshot you may receive from 
the View Mediator. 

```python
class CityStore(Store):
    city = reference(many=False)
```

Next, declare a View Model. A View Model has attributes that converts 
inner data models to presentable data models for front end. The 
`doc_ref` attribute chooses where the view model will save to. 

```python
class CityView(ViewModel):

    name = attrs.bproperty()
    country = attrs.bproperty()

    @classmethod
    def new(cls, snapshot):
        store = CityStore()
        store.add_snapshot("city", dm_cls=City, snapshot=snapshot)
        store.refresh()
        return cls(store=store)

    @name.getter
    def name(self):
        return self.store.city.city_name

    @country.getter
    def country(self):
        return self.store.city.country

    @property
    def doc_ref(self):
        return CTX.db.document(f"cityView/{self.store.city.doc_id}")
```

### Declare Mediator Class

```Protocol.on_create``` will be called every time a new document (domain
model) is created in the ```City/``` collection. When you start the server,
 ```on_create``` will be invoked once for all existing documents. 

```python
class CityViewMediator(ViewMediatorDeltaDAV):

    def notify(self, obj):
        obj.save()

    class Protocol(ProtocolBase):

        @staticmethod
        def on_create(snapshot: DocumentSnapshot, mediator: ViewMediatorBase):
            view = CityView.new(snapshot=snapshot)
            mediator.notify(obj=view)
```

### Add Entrypoint 

In ```main.py```, 

```python
city_view_mediator = CityViewMediator(
    query=City.get_query()
)

if __name__ == "__main__":
    city_view_mediator.start()
```

When you create a domain model in ```City/TOK```, 

```python
obj = Municipality.new(
        doc_id="TOK", city_name='Tokyo', country='Japan', capital=True)
obj.save()
```

The framework will generate a view document in ```cityView/TOK```, 

```python
{
    'doc_ref': 'cityView/TOK',
    'obj_type': 'CityView',
    'country': 'Japan',
    'name': 'Tokyo'
}
```

Now, you have the basic app set up. 

## Create a form service 

In this example, the user can post a form to 
```/users/<user_id>/cityForms/<city_id>``` and create a new city. 

### Create Form Class

Declare a ```CityForm``` used for user to create a new city. 

The function decorated with ```city.init``` will be called to 
initialize ```city``` attribute to a blank ```City``` Domain Model 
in the default location for property reads: ```obj._attrs```. 
The fields of the blank Domain Model are set through the property 
setters. ```propagate_change``` will be called by the mediator 
to save the newly created city Domain Model to datastore. 

```python
class CityForm(ViewModel):

    name = attrs.bproperty()
    country = attrs.bproperty()
    city_id = attrs.bproperty()

    city = attrs.bproperty(initialize=True)

    @city.init
    def city(self):
        self._attrs.city = City.new(doc_id=self.doc_ref.id)

    @name.setter
    def name(self, val):
        self.city.city_name = val

    @country.setter
    def country(self, val):
        self.city.country = val

    def propagate_change(self):
        self.city.save()
```

### Declare Form Mediator 

```python
class CityFormMediator(ViewMediatorDeltaDAV):

    def notify(self, obj):
        obj.propagate_change()

    class Protocol(ProtocolBase):

        @staticmethod
        def on_create(snapshot: DocumentSnapshot, mediator: ViewMediatorBase):
            obj = CityForm.new(doc_ref=snapshot.reference)
            obj.update_vals(with_raw=snapshot.to_dict())
            mediator.notify(obj=obj)
```

### Add Security Rule

In your Firestore console, add the following security rule:  

```
    match /users/{userId}/{documents=**} {
      allow read, write: if request.auth.uid == userId
    }
```

This restricts the ability to post a city to only registered users. 

### Add Service

Now, your ```main.py``` should be, 

```python
city_view_mediator = CityViewMediator(
    query=City.get_query()
)

city_form_mediator = CityFormMediator(
    query=CTX.db.collection_group("cityForms")
)

if __name__ == "__main__":
    city_view_mediator.start()
    city_form_mediator.start()
```

When the user creates a document in ```users/uid1/cityForms/LA```, 

```python
{
    'country': 'USA',
    'name': 'Los Angeles'
}
```

you should be able to receive the domain model in ```City/LA```, 

```python
{
    'cityName': 'Los Angeles',
    'country': 'USA',
    'doc_id': 'LA',
    'doc_ref': 'City/LA',
    'obj_type': 'City'
}
```

and the view model in ```cityView/LA```, 

```python

{
    'name': 'Los Angeles',
    'country': 'USA',
    'doc_ref': 'cityView/LA',
    'obj_type': 'CityView',
}
```

This completes the setup for a simple CQRS read model / form set up for 
flask-boiler. The user may create new cities by posting a collection 
they own, and view cities by reading ```cityView```. 
