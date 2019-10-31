# flask-boiler

[![Build Status](https://travis-ci.com/billyrrr/flask-boiler.svg?branch=master)](https://travis-ci.com/billyrrr/flask-boiler)
[![Coverage Status](https://coveralls.io/repos/github/billyrrr/flask-boiler/badge.svg?branch=master)](https://coveralls.io/github/billyrrr/flask-boiler?branch=master)
[![Documentation Status](https://readthedocs.org/projects/flask-boiler/badge/?version=latest)](https://flask-boiler.readthedocs.io/en/latest/?badge=latest)

![IMG_2602](https://user-images.githubusercontent.com/24789156/67615967-90976f80-f787-11e9-9788-5b11e5ba4175.PNG)

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

### Relationship

Flask-boiler adds an option to retrieve a relation with 
minimal steps. Take an example given from SQLAlchemy, 

```python
category_id = utils.random_id()
py = Category.create(doc_id=category_id)
py.name = "Python"

post_id = utils.random_id()
p = Post.create(doc_id=post_id)
p.title = "snakes"
p.body = "Ssssssss"

# py.posts.append(p)
p.category = py

py.save()

obj = Post.get(doc_id=post_id)

assert str(p.category) == "<Category 'Python'>"

assert p._export_as_view_dict() == {'body': 'Ssssssss',
                                    'id': post_id,
                                    'category': {
                                        'id': category_id,
                                        'name': 'Python'},
                                    'title': 'snakes',
                                    'pubDate': None
                                    }
                                    
```

See ```examples/relationship_example.py```

### Embedded

You can embed a serializable object in a ViewModel or ReferencedObject, 
so that the embedded object is retrieved with the master object 
(no separate calls). Thus offer an advantage over performance when 
1. nested document is meant to be retrieved with the master document
2. nested document is not referenced by any other document 
3. nested documents do not need to be queried 


```python
    class TargetSchema(schema.Schema):
        earliest = fields.Raw()
        latest = fields.Raw()

    class Target(serializable.Serializable):
        _schema_cls = TargetSchema

    t = Target()
    t.earliest = 10
    t.latest = 20

    class PlanSchema(schema.Schema):
        target = fields.Embedded()
        name = fields.Str()

    class Plan(serializable.Serializable):
        _schema_cls = PlanSchema

    k = Plan.from_dict({
        "target": t.to_dict(),
        "name": "my plan"
    })

    assert k.to_dict() == {
        "name": "my plan",
        "target": {
            "earliest": 10,
            "latest": 20,
            "obj_type": "Target",
            "doc_id": ""
        },
        "obj_type": "Plan",
        "doc_id": ""
    }

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
