# flask-boiler

[![Build Status](https://travis-ci.com/billyrrr/flask-boiler.svg?branch=master)](https://travis-ci.com/billyrrr/flask-boiler)
[![Coverage Status](https://coveralls.io/repos/github/billyrrr/flask-boiler/badge.svg?branch=master)](https://coveralls.io/github/billyrrr/flask-boiler?branch=master)

Flask-boiler helps you build fast-prototype of your backend. Other than providing an easy-to-use 
ORM wrapper for firestore ORM, this framework support an entire set of features to build a backend 
using "flask-boiler architecture". It works with flask so you may build new services using flask-boiler 
to run with your current flask app. 

# Features

## Firestore ORM 

### Add data

It allows you to replace, 

```python
doc_ref = db.collection(u'users').document(u'alovelace')
doc_ref.set({
    u'first': u'Ada',
    u'last': u'Lovelace',
    u'born': 1815
})
```
with this, 

```python
user = User.create(doc_id="alovelace")
user.first = 'Ada'
user.last = 'Lovelace'
user.born = "1815"
user.save()
```

(*Extra steps required to declare model. See quickstart for details.)

### Read data

It allows you to replace, 

```python
users_ref = db.collection(u'users')
docs = users_ref.stream()

for doc in docs:
    print(u'{} => {}'.format(doc.id, doc.to_dict()))
```

with this, 

```python
for user in User.all():
    print(user.to_dict())
```

### Save data 

It allows you to replace, 

```python
class City(object):
    def __init__(self, name, state, country, capital=False, population=0,
                 regions=[]):
        self.name = name
        self.state = state
        self.country = country
        self.capital = capital
        self.population = population
        self.regions = regions

    @staticmethod
    def from_dict(source):
        # ...

    def to_dict(self):
        # ...

    def __repr__(self):
        return(
            u'City(name={}, country={}, population={}, capital={}, regions={})'
            .format(self.name, self.country, self.population, self.capital,
                    self.regions))

cities_ref = db.collection(u'cities')
cities_ref.document(u'SF').set(
    City(u'San Francisco', u'CA', u'USA', False, 860000,
         [u'west_coast', u'norcal']).to_dict())
cities_ref.document(u'LA').set(
    City(u'Los Angeles', u'CA', u'USA', False, 3900000,
         [u'west_coast', u'socal']).to_dict())
cities_ref.document(u'DC').set(
    City(u'Washington D.C.', None, u'USA', True, 680000,
         [u'east_coast']).to_dict())
cities_ref.document(u'TOK').set(
    City(u'Tokyo', None, u'Japan', True, 9000000,
         [u'kanto', u'honshu']).to_dict())
cities_ref.document(u'BJ').set(
    City(u'Beijing', None, u'China', True, 21500000, [u'hebei']).to_dict())
```

with this, 

```python

def CityBase(DomainModel):
    _collection_name = "cities"
    
City = ClsFactory.create_customized(
        name="City",
        fieldnames=["name", "state", "country", "capital", "population", "regions"], 
        auto_initialized=False,
        importable=False,
        exportable=True,
        additional_base=(CityBase,)
    )
    
City.new(
        doc_id='SF',
        name='San Francisco',
        state='CA', 
        country='USA', 
        capital=False, 
        populations=860000,
        regions=['west_coast', 'norcal']).save()

# ...
```

(*fieldname kwarg in ClsFactory to be implemented soon)

### Get data 

It allows you to replace, 

```python
doc_ref = db.collection(u'cities').document(u'SF')

try:
    doc = doc_ref.get()
    print(u'Document data: {}'.format(doc.to_dict()))
except google.cloud.exceptions.NotFound:
    print(u'No such document!')
```

with this, 

```python
sf = City.get(doc_id='SF')
if sf is not None:  # To be implemented soon  
    print(u'Document data: {}'.format(doc.to_dict()))
else:
    print("No such document")

```

### Simple queries

It allows you to replace, 

```python
docs = db.collection(u'cities').where(u'capital', u'==', True).stream()

for doc in docs:
    print(u'{} => {}'.format(doc.id, doc.to_dict()))
```

with this, 

```python
for city in City.where(capital=True):
    print(city.to_dict())
```

### Query operators

It allows you to replace, 

```python
cities_ref = db.collection(u'cities')

cities_ref.where(u'state', u'==', u'CA')
cities_ref.where(u'population', u'<', 1000000)
cities_ref.where(u'name', u'>=', u'San Francisco'
```

with this, 

```python
City.where(state="CA")
City.where(population=('<', 1000000))
City.where(name=('>=', "San Francisco"))
```

### Field name conversion 

Sometimes, you want to have object attributes in "snake_case" and 
Firestore Document field name in "camelCase". This is by default for 
flask-boiler. You may customize this conversion also. 

Consider this example, 

```python

class CitySchema(Schema):
    city_name = fields.Raw()

    country = fields.Raw()
    capital = fields.Raw()
    

class MunicipalitySchema(CitySchema):
    pass


class StandardCitySchema(CitySchema):
    city_state = fields.Raw()
    regions = fields.Raw(many=True)


class City(DomainModel):
    _collection_name = "City"
    

Municipality = ClsFactory.create(
    name="Municipality",
    schema=MunicipalitySchema,
    base=City,
)


StandardCity = ClsFactory.create(
    name="StandardCity",
    schema=StandardCitySchema,
    base=City
)

sf = StandardCity.create(doc_id="SF")
sf.city_name, sf.city_state, sf.country, sf.capital, sf.regions = \
    'San Francisco', 'CA', 'USA', False, ['west_coast', 'norcal']
sf.save()

la = StandardCity.create(doc_id="LA")
la.city_name, la.city_state, la.country, la.capital, la.regions = \
    'Los Angeles', 'CA', 'USA', False, ['west_coast', 'socal']
la.save()

dc = Municipality.create(doc_id="DC")
dc.city_name, dc.country, dc.capital = 'Washington D.C.', 'USA', True
dc.save()

tok = Municipality.create(doc_id="TOK")
tok.city_name, tok.country, tok.capital = 'Tokyo', 'Japan', True
tok.save()

beijing = Municipality.create(doc_id="BJ")
beijing.city_name, beijing.country, beijing.capital = \
    'Beijing', 'China', True
beijing.save()

```

object ```la``` saves to a document in firestore with "camelCase" field names, 

```python
{
    'cityName': 'Los Angeles',
    'cityState': 'CA',
    'country': 'USA',
    'capital': False,
    'regions': ['west_coast', 'socal'],
    'obj_type': "StandardCity",
    'doc_id': 'LA',
    'doc_ref': 'City/LA'
}
```

Similarly, you can query the objects with your local object attribute 
or firestore field name. 

```python
for obj in City.where(city_state="CA"):
    print(obj.city_name)
```

Or equivalently 
```python
for obj in City.where("cityState", "==", "CA"):
    print(obj.city_name)
```


### Context Management

In ```__init__``` of your project source root: 
```python
import os

from flask_boiler import context
from flask_boiler import config

Config = config.Config

testing_config = Config(app_name="your_app_name",
                        debug=True,
                        testing=True,
                        certificate_path=os.path.curdir + "/../your_project/config_jsons/your_certificate.json")

CTX = context.Context
CTX.read(testing_config)
```

Note that initializing ```Config``` with ```certificate_path``` is unstable and 
may be changed later. 

In your project code, 

```python
from flask_boiler import context

CTX = context.Context

# Retrieves firestore database instance 
CTX.db

# Retrieves firebase app instance 
CTX.firebase_app

```

## Architecture Diagram

You may structure your project in this way:

![architecture diagrama](https://www.lucidchart.com/publicSegments/view/76e8c8d4-a356-46ed-af95-e079d38a7bd7/image.png)

### Business Properties Binding

You can bind a view model to its business properties (underlying domain model). 
See ```examples/binding_example.py```. 

### Automatically Generated Swagger Docs

You can enable auto-generated swagger docs. See: ```examples/view_example.py```

### Create Flask View

You can create a flask view to specify how a view model is read and changed. 

## Advantages

### Decoupled Domain Model and View Model

Using Firebase Firestore sometimes require duplicated fields 
across several documents in order to both query the data and 
display them properly in front end. Flask-boiler solves this 
problem by decoupling domain model and view model. View model 
are generated and refreshed automatically as domain model 
changes. This means that you will only have to write business 
logics on the domain model without worrying about how the data 
will be displayed. This also means that the View Models can 
be displayed directly in front end, while supporting 
real-time features of Firebase Firestore. 

### One-step Configuration

Rather than configuring the network and different certificate 
settings for your database and other cloud services. All you 
have to do is to enable related services on Google Cloud 
Console, and add your certificate. Flask-boiler configures 
all the services you need, and expose them as a singleton 
Context object across the project. 

### Redundancy

Since all View Models are persisted in Firebase Firestore. 
Even if your App Instance is offline, the users can still 
access a view of the data from Firebase Firestore. Every 
View is also a Flask View, so you can also access the data 
with auto-generated REST API, in case Firebase Firestore is 
not viable. 

### Added Safety

By separating business data from documents that are accessible
to the front end, you have more control over which data is 
displayed depending on the user's role. 

### One-step Documentation

All ViewModels have automatically generated documentations 
(provided by Flasgger). This helps AGILE teams keep their 
documentations and actual code in sync. 

### Fully-extendable

When you need better performance or relational database 
support, you can always refactor a specific layer by 
adding modules such as ```flask-sqlalchemy```.  


