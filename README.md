# flask-boiler

[![Build Status](https://travis-ci.com/billyrrr/flask-boiler.svg?branch=master)](https://travis-ci.com/billyrrr/flask-boiler)
[![Coverage Status](https://coveralls.io/repos/github/billyrrr/flask-boiler/badge.svg?branch=master)](https://coveralls.io/github/billyrrr/flask-boiler?branch=master)
[![Documentation Status](https://readthedocs.org/projects/flask-boiler/badge/?version=latest)](https://flask-boiler.readthedocs.io/en/latest/?badge=latest)

Flask-boiler helps you build fast-prototype of your backend. Other than providing an easy-to-use
ORM wrapper for firestore ORM, this framework support an entire set of features to build a backend
using "flask-boiler architecture". It works with flask so you may build new services using flask-boiler
to run with your current flask app.

This framework is at development stage. API is not guaranteed and may change often. 

Documentations: [readthedocs](https://flask-boiler.readthedocs.io/)

Quickstart: [Quickstart](https://flask-boiler.readthedocs.io/en/latest/quickstart_link.html)

API Documentations: [API Docs](https://flask-boiler.readthedocs.io/en/latest/apidoc/flask_boiler.html)

## Installation
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

```
pip install -r requirements.txt
```

See more in [Quickstart](https://flask-boiler.readthedocs.io/en/latest/quickstart_link.html). 

## Usage

### Context Management
In `__init__` of your project source root:
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

Note that initializing `Config` with `certificate_path` is unstable and
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


### Add data

```python
user = User.create(doc_id="alovelace")
user.first = 'Ada'
user.last = 'Lovelace'
user.born = "1815"
user.save()
```

(*Extra steps required to declare model. See quickstart for details.)

### Read data

```python
for user in User.all():
    print(user.to_dict())
```

### Save data

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

```python
sf = City.get(doc_id='SF')
if sf is not None:  # To be implemented soon  
    print(u'Document data: {}'.format(doc.to_dict()))
else:
    print("No such document")

```

### Business Properties Binding
You can bind a view model to its business properties (underlying domain model).
See `examples/binding_example.py`.

### Automatically Generated Swagger Docs
You can enable auto-generated swagger docs. See: `examples/view_example.py`

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
adding modules such as `flask-sqlalchemy`.

## Contributing
Pull requests are welcome. 

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
