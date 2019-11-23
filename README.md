# flask-boiler

[![Build Status](https://travis-ci.com/billyrrr/flask-boiler.svg?branch=master)](https://travis-ci.com/billyrrr/flask-boiler)
[![Coverage Status](https://coveralls.io/repos/github/billyrrr/flask-boiler/badge.svg?branch=master)](https://coveralls.io/github/billyrrr/flask-boiler?branch=master)
[![Documentation Status](https://readthedocs.org/projects/flask-boiler/badge/?version=latest)](https://flask-boiler.readthedocs.io/en/latest/?badge=latest)

![IMG_2602](https://user-images.githubusercontent.com/24789156/67615967-90976f80-f787-11e9-9788-5b11e5ba4175.PNG)

"boiler": **B**ackend-**O**riginated **I**nstantly-**L**oaded **E**ntity **R**epository 

Flask-boiler helps you build fast-prototype of your backend. Other than providing an easy-to-use
ORM wrapper for firestore ORM, this framework support an entire set of features to build a backend
using "flask-boiler architecture". It works with flask so you may build new services using flask-boiler
to run with your current flask app.

This framework is at ***development stage***. 
API is not guaranteed and ***will*** change often. 

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

### Business Properties Binding
You can bind a view model to its business properties (underlying domain model).
See `examples/binding_example.py`.

```python

vm: Luggages = Luggages.new(vm_ref)

vm.bind_to(key=id_a, obj_type="LuggageItem", doc_id=id_a)
vm.bind_to(key=id_b, obj_type="LuggageItem", doc_id=id_b)
vm.register_listener()

```

### State Management

You can combine information gathered in domain models and serve them in Firestore, so 
that front end can read all data required from a single document or collection, 
without client-side queries and excessive server roundtrip time. 

There is a medium [article](https://medium.com/resolvejs/resolve-redux-backend-ebcfc79bbbea) 
 that explains a similar architecture called "reSolve" architecture. 

The example below explains how to use flask-boiler to expose a "view model" 
in firestore to save front end from querying 3 separate domain models. 
(See ```examples/meeting_room/view_models``` for details.)

```python

class MeetingSessionMixin:

    _schema_cls = MeetingSessionSchema

    def __init__(self, *args, meeting_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._meeting_id = meeting_id

    @property
    def _users(self):
        user_ids = [user_ref.id for user_ref in self._meeting.users]
        return {
            user_id: self.business_properties[user_id] for user_id in user_ids
        }

    @property
    def _tickets(self):
        return {
            self.business_properties[ticket_ref.id].user.id:
                self.business_properties[ticket_ref.id]
                for ticket_ref in self._meeting.tickets
        }

    @property
    def _meeting(self):
        """
        TODO: fix evaluation order in source code (add priority flag to some
        TODO:    view models to be instantiated first)
        :return:
        """
        return self.business_properties[self._meeting_id]

    @property
    def meeting_id(self):
        return self._meeting.doc_id

    @property
    def _location(self):
        return self.business_properties[self._meeting.location.id]

    @property
    def in_session(self):
        return self._meeting.status == "in-session"

    @in_session.setter
    def in_session(self, in_session):
        cur_status = self._meeting.status
        if cur_status == "in-session" and not in_session:
            self._meeting.status = "closed"
        elif cur_status == "closed" and in_session:
            self._meeting.status = "in-session"
        else:
            raise ValueError

    @property
    def latitude(self):
        return self._location.latitude

    @property
    def longitude(self):
        return self._location.longitude

    @property
    def address(self):
        return self._location.address

    @property
    def attending(self):
        user_ids = [uid for uid in self._users.keys()]

        if self._meeting.status == "not-started":
            return list()

        res = list()
        for user_id in sorted(user_ids):
            ticket = self._tickets[user_id]
            user = self._users[user_id]
            if ticket.attendance:
                d = {
                    "name": user.display_name,
                    "organization": user.organization,
                    "hearing_aid_requested": user.hearing_aid_requested
                }
                res.append(d)

        return res

    @property
    def num_hearing_aid_requested(self):
        count = 0
        for d in self.attending:
            if d["hearing_aid_requested"]:
                count += 1
        return count

    @classmethod
    def get_many_from_query(cls, query_d=None, once=False):
        """ Note that once kwarg apply to the snapshot but not the query.

        :param query_d:
        :param once: attaches a listener to individual snapshots
        :return:
        """
        return [
            cls.get_from_meeting_id(meeting_id=obj.doc_id, once=once)
            for obj in Meeting.where(**query_d)]

    @classmethod
    def new(cls, doc_id=None):
        return cls.get_from_meeting_id(meeting_id=doc_id)

    @classmethod
    def get_from_meeting_id(cls, meeting_id, once=False, **kwargs):
        struct = dict()

        m: Meeting = Meeting.get(doc_id=meeting_id)

        struct[m.doc_id] = (Meeting, m.doc_ref.id)

        for user_ref in m.users:
            obj_type = User
            doc_id = user_ref.id
            struct[doc_id] = (obj_type, user_ref.id)

        for ticket_ref in m.tickets:
            obj_type = Ticket
            doc_id = ticket_ref.id

            struct[doc_id] = (obj_type, ticket_ref.id)

        struct[m.location.id] = (Location, m.location.id)

        obj = cls.get(struct_d=struct, once=once,
                          meeting_id=m.doc_ref.id,
                          **kwargs)
        time.sleep(2)  # TODO: delete after implementing sync
        return obj

    def propagate_change(self):
        self._meeting.save()


class MeetingSession(MeetingSessionMixin, view.FlaskAsView):
    pass


class MeetingSessionMutation(Mutation):

    view_model_cls = MeetingSession

```



### Add data

```python
user = User.new(doc_id="alovelace")
user.first = 'Ada'
user.last = 'Lovelace'
user.born = "1815"
user.save()
```

(*Extra steps required to declare model. See quickstart for details.)


### Save data

```python

def CityBase(DomainModel):
    _collection_name = "cities"
    
class City(CityBase):
    _schema_cls = CitySchema 
    
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

### Relationship

Flask-boiler adds an option to retrieve a relation with 
minimal steps. Take an example given from SQLAlchemy, 

```python
category_id = utils.random_id()
py = Category.new(doc_id=category_id)
py.name = "Python"

post_id = utils.random_id()
p = Post.new(doc_id=post_id)
p.title = "snakes"
p.body = "Ssssssss"

# py.posts.append(p)
p.category = py

p.save()

```

See ```examples/relationship_example.py```


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



### Automatically Generated Swagger Docs
You can enable auto-generated swagger docs. See: `examples/view_example.py`



### Create Flask View
You can create a flask view to specify how a view model is read and changed.

```python


app = Flask(__name__)

meeting_session_mediator = view_mediator.ViewMediator(
    view_model_cls=MeetingSession,
    app=app,
    mutation_cls=MeetingSessionMutation
)
meeting_session_mediator.add_list_get(
    rule="/meeting_sessions",
    list_get_view=meeting_session_ops.ListGet
)

meeting_session_mediator.add_instance_get(
    rule="/meeting_sessions/<string:doc_id>")
meeting_session_mediator.add_instance_patch(
    rule="/meeting_sessions/<string:doc_id>")

user_mediator = view_mediator.ViewMediator(
    view_model_cls=UserView,
    app=app,
)
user_mediator.add_instance_get(
    rule="/users/<string:doc_id>"
)

swagger = Swagger(app)

app.run(debug=True)


```

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


## Comparisons 

### GraphQL

In GraphQL, the fields are evaluated with each query, but 
flask-boiler evaluates the fields if and only if the 
underlying data source changes. This leads to faster 
read for data that has not changed for a while. Also, 
the data source is expected to be consistent, as the 
field evaluation are triggered after all changes made in 
one transaction to firestore is read. 

GraphQL, however, lets front-end customize the return. You 
must define the exact structure you want to return in flask-boiler. 
This nevertheless has its advantage as most documentations 
of the request and response can be done the same way as REST API. 

### REST API / Flask

REST API does not cache or store the response. When 
a view model is evaluated by flask-boiler, the response 
is stored in firestore forever until update or manual removal. 

Flask-boiler controls role-based access with security rules 
integrated with Firestore. REST API usually controls these 
access with a JWT token. 

### Redux

Redux is implemented mostly in front end. Flask-boiler targets 
back end and is more scalable, since all data are communicated 
with Firestore, a infinitely scalable NoSQL datastore. 

Flask-boiler is declarative, and Redux is imperative. 
The design pattern of REDUX requires you to write functional programming 
in domain models, but flask-boiler favors a different approach: 
ViewModel reads and calculates data from domain models 
and exposes the attribute as a property getter. (When writing 
to DomainModel, the view model changes domain model and 
exposes the operation as a property setter). 
Nevertheless, you can still add function callbacks that are 
triggered after a domain model is updated, but this 
may introduce concurrency issues and is not perfectly supported 
due to the design tradeoff in flask-boiler. 

## Design Philosophies

### Scalability Valued Over Server Cost

At the starting stage of a project, you have a boutique 
user base, and it may be feasible to afford higher server 
cost to provide reliable and reactive services to 
these users. As your user base grow, you may take other 
actions to reduce cost while maintaining the quality 
of your product (such as moving to a different architecture 
to present view models). Overall, flask-boiler gives 
you a quality jump-start so that you can focus on 
transforming ideas. 

### ViewModel Made Eventually Consistent

When DomainModel changes, the relevant view models may 
not change immediately, but gradually changed overtime. 
The information on a view model will eventually be 
correct and up-to-date, and some view models may be 
update sooner than others. For example, some users 
may receive the update to their 
meeting session sooner than others. 

Rest assured, the write to DomainModel is still designed 
to be strongly consistent. When a user makes changes, 
it is designed to validate that they have the latest 
data before the domain model is updated. 

### Update One Document Per Field

For example, if user A wants to change their display name or
preferred pronoun, you should update only one document to
reflect this change. In alternative designs, you may update
several other documents, for example, the friend list of
user B and user E to reflect this change, but flask-boiler
does not favor this approach. It is recommended
that you build friend list as a ViewModel, and do not update
its values directly, so that you update only
***one*** document per field (in this case the User
domain model of user A).

## Contributing
Pull requests are welcome. 

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
