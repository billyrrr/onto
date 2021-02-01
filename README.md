# onto

[![Build Status](https://travis-ci.com/billyrrr/flask-boiler.svg?branch=master)](https://travis-ci.com/billyrrr/flask-boiler)
[![Coverage Status](https://coveralls.io/repos/github/billyrrr/flask-boiler/badge.svg?branch=master)](https://coveralls.io/github/billyrrr/flask-boiler?branch=master)
[![Documentation Status](https://readthedocs.org/projects/flask-boiler/badge/?version=latest)](https://flask-boiler.readthedocs.io/en/latest/?badge=latest)


Demo: 

When you change the attendance status of one of the participants 
in the meeting, all other participants receive an updated version 
of the list of people attending the meeting. 

![Untitled_2](https://user-images.githubusercontent.com/24789156/71137341-be0e1000-2242-11ea-98cb-53ad237cac43.gif)

Some reasons that you may want to use this framework or architectual
practice:
- You want to build a reactive system and not just a reactive view. 
- You want to build a scalable app that is native to distributed 
    systems. 
- You want a framework with a higher level of abstraction, so you can 
    exchange components such as transportation protocols 
- You want your code to be readable and clear and written mostly 
    in python, while maintaining compatibility to different APIs. 
- You have constantly-shifting requirements, and want to have 
    the flexibility to migrate different layers, for example, 
    switch from REST API to WebSocket to serve a resource. 

This framework is at ***beta testing stage***. 
API is not guaranteed and ***may*** change. 

Documentations: [readthedocs](https://flask-boiler.readthedocs.io/)

Quickstart: [Quickstart](https://flask-boiler.readthedocs.io/en/latest/quickstart_link.html)

API Documentations: [API Docs](https://flask-boiler.readthedocs.io/en/latest/apidoc/flask_boiler.html)

Example of a Project using onto (now named onto): [gravitate-backend](https://github.com/billyrrr/gravitate-backend)

[Related Technologies](https://medium.baqend.com/real-time-databases-explained-why-meteor-rethinkdb-parse-and-firebase-dont-scale-822ff87d2f87)

## Connectors supported 

Implemented: 
- REST API (Flask and Flasgger)
- GraphQL (Starlette)
- Firestore
- Firebase Functions
- JsonRPC (flask-jsonrpc)
- Leancloud Engine
- WebSocket (flask socketio)

To be supported: 
- Flink Table API
- Kafka

## What I am currently trying to build

Front end creates mutations in graphql. 
"Onto" receives the view model, and triggers 
action on domain model. A method in domain model 
is called (which lives in Flink Stateful Functions
runtime). Different domain models communicate to 
persist a change, and save the output view into Kafka. 
Another set of system statically interprets "view 
model definition code" as SQL, 
and submit jobs with Flink SQL to assemble "view model". 
Eventually, the 1NF view of the data is sent to Kafka, 
and eventually delivered to front end in forms of 
GraphQL Subscription. 

(Write side has Serializable-level consistency, 
and read side has eventual consistency) 

## What it already does  
- Serialization and deserialization
- GraphQL/Flask server 
- Multiple table join
- ... 

## Installation
In your project directory, 

```
pip install onto
```

See more in [Quickstart](https://onto.readthedocs.io/en/latest/quickstart_link.html). 

<!--## Usage-->

<!--### Business Properties Binding-->
<!--You can bind a view model to its business properties (underlying domain model).-->
<!--See `examples/binding_example.py`. (Currently breaking)-->

<!--```python-->

<!--vm: Luggages = Luggages.new(vm_ref)-->

<!--vm.bind_to(key=id_a, obj_type="LuggageItem", doc_id=id_a)-->
<!--vm.bind_to(key=id_b, obj_type="LuggageItem", doc_id=id_b)-->
<!--vm.register_listener()-->

<!--```-->

### State Management

You can combine information gathered in domain models and serve them in Firestore, so 
that front end can read all data required from a single document or collection, 
without client-side queries and excessive server roundtrip time. 

There is a medium [article](https://medium.com/resolvejs/resolve-redux-backend-ebcfc79bbbea) 
 that explains a similar architecture called "reSolve" architecture. 

See ```examples/meeting_room/view_models``` on how to use onto 
to expose a "view model" in firestore that can be queried directly 
by front end without aggregation.  

### Processor Modes

`onto` is essentially a framework for source-sink operations: 

```
Source(s) -> Processor -> Sink(s)
```

Take query as an example,  

- Boiler
- NoSQL
- Flink
    - staticmethods: converts to UDF
    - classmethods: converts to operators and aggregator's 
    

### Declare View Model

```python
from onto.attrs import attrs

class CityView(ViewModel):

    name: str = attrs.nothing
    country: str = attrs.nothing

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

### Document View

``` python

class MeetingSessionGet(Mediator):

    from onto import source, sink

    source = source.domain_model(Meeting)
    sink = sink.firestore()  # TODO: check variable resolution order

    @source.triggers.on_update
    @source.triggers.on_create
    def materialize_meeting_session(self, obj):
        meeting = obj
        assert isinstance(meeting, Meeting)

        def notify(obj):
            for ref in obj._view_refs:
                self.sink.emit(reference=ref, snapshot=obj.to_snapshot())

        _ = MeetingSession.get(
            doc_id=meeting.doc_id,
            once=False,
            f_notify=notify
        )
        # mediator.notify(obj=obj)

    @classmethod
    def start(cls):
        cls.source.start()

```

### Create Flask View
You can use a RestMediator to create a REST API. OpenAPI3 docs will be 
automatically generated in ```<site_url>/apidocs``` when you run ```_ = Swagger(app)```. 

```python
app = Flask(__name__)

class MeetingSessionRest(Mediator):

    # from onto import source, sink

    view_model_cls = MeetingSessionC

    rest = RestViewModelSource()

    @rest.route('/<doc_id>', methods=('GET',))
    def materialize_meeting_session(self, doc_id):

        meeting = Meeting.get(doc_id=doc_id)

        def notify(obj):
            d = obj.to_snapshot().to_dict()
            content = jsonify(d)
            self.rest.emit(content)

        _ = MeetingSessionC.get(
            doc_id=meeting.doc_id,
            once=False,
            f_notify=notify
        )

    # @rest.route('/', methods=('GET',))
    # def list_meeting_ids(self):
    #     return [meeting.to_snapshot().to_dict() for meeting in Meeting.all()]

    @classmethod
    def start(cls, app):
        cls.rest.start(app)

swagger = Swagger(app)

app.run(debug=True)
```

(currently under implementation) 

## Object Lifecycle

### Once

Object created with ```cls.new``` -> 
Object exported with ```obj.to_view_dict```. 

### Multi

Object created when a new domain model is created in database -> 
Object changed when underlying datasource changes -> 
Object calls ```self.notify``` 

## Typical ViewMediator Use Cases 

Data flow direction is described as Source -> Sink. 
"Read" describes the flow of data where front end would find data in Sink useful. 
"Write" describes the flow of data where the Sink is the single source 
of truth. 

### Rest 

Read: Request -> Response \
Write: Request -> Document

1. Front end sends HTTP request to Server  
2. Server queries datastore
3. Server returns response

### Query

Read: Document -> Document \
Write: Document -> Document

1. Datastore triggers update function 
2. Server rebuilds ViewModel that may be changed as a result 
3. Server saves newly built ViewModel to datastore 

### Query+Task

Read: Document -> Document \
Write: Document -> Document

1. Datastore triggers update function for document `d` at time `t`
2. Server starts a transaction
3. Server sets write_option to only allow commit if documents are last updated at time `t` (still under design)
3. Server builds ViewModel with transaction 
5. Server saves ViewModel with transaction
7. Server marks document `d` as processed (remove document or update a field)
7. Server retries up to MAX_RETRIES from step 2 if precondition failed 

### WebSocket

Read: Document -> WebSocket Event \
Write: WebSocket Event -> Document

1. Front end subscribes to a ViewModel by sending a WebSocket event to server 
2. Server attaches listener to the result of the query
3. Every time the result of the query is changed and consistent:
    1. Server rebuilds ViewModel that may be changed as a result 
    2. Server publishes newly built ViewModel
4. Front end ends the session
5. Document listeners are released 

### Document

Read: Document -> Document \
Write: Document -> Document

### Comparisons 

|                 	| Rest 	            | Query 	     | Query+Task                   | WebSocket 	    | Document |
|-----------------	|------         	|-------	|------------	|-----------	|----------	|
| Guarantees      	|    ≤1   (At-Most-Once)         	| ≥ 1 (At-Least-Once)          |  =1[^1] (Exactly-Once)    |   ≤1   (At-Most-Once)  	|       ≥ 1 (At-Least-Once) 	|
| Idempotence      	| If Implemented    | No            | Yes, with transaction[^1]    	| If Implemented  	| No    |
| Designed For      | Stateless Lambda  |  Stateful Container   | Stateless Lambda      | Stateless Lambda  | Stateful Container |
| Latency         	| Higher            | Higher 	|   Higher     |  Lower           	|     Higher     	|
| Throughput      	| Higher when Scaled| Lower[^2]       	| Lower          	|   Higher when Scaled	|   Lower[^2]      	|
| Stateful        	| No   	            | If Implemented    | If Implemented   	| Yes        	| Yes         	|
| Reactive        	| No   	        | Yes    | Yes   	| Yes        	| Yes         	|

<!---
Gaurantees
| Back Pressure   	|      	|       	|            	|           	|          	|
Latency
Throughput
| Fault Tolerance 	|      	|       	|            	|           	|          	|
Stateful
-->

[^1]:  A message may be received and processed by multiple consumer, but only one 
consumer can successfully commit change and mark the event as processed. 
[^2]:  Scalability is limited by the number of listeners you can attach to the datastore.

## Comparisons 

### GraphQL

In GraphQL, the fields are evaluated with each query, but 
onto evaluates the fields if and only if the 
underlying data source changes. This leads to faster 
read for data that has not changed for a while. Also, 
the data source is expected to be consistent, as the 
field evaluation are triggered after all changes made in 
one transaction to firestore is read. 

GraphQL, however, lets front-end customize the return. You 
must define the exact structure you want to return in onto. 
This nevertheless has its advantage as most documentations 
of the request and response can be done the same way as REST API. 

### REST API / Flask

REST API does not cache or store the response. When 
a view model is evaluated by onto, the response 
is stored in firestore forever until update or manual removal. 

onto controls role-based access with security rules 
integrated with Firestore. REST API usually controls these 
access with a JWT token. 

### Redux

Redux is implemented mostly in front end. onto targets 
back end and is more scalable, since all data are communicated 
with Firestore, a infinitely scalable NoSQL datastore. 

onto is declarative, and Redux is imperative. 
The design pattern of REDUX requires you to write functional programming 
in domain models, but onto favors a different approach: 
ViewModel reads and calculates data from domain models 
and exposes the attribute as a property getter. (When writing 
to DomainModel, the view model changes domain model and 
exposes the operation as a property setter). 
Nevertheless, you can still add function callbacks that are 
triggered after a domain model is updated, but this 
may introduce concurrency issues and is not perfectly supported 
due to the design tradeoff in onto. 


### Architecture Diagram: 

![Architecture Diagram](https://user-images.githubusercontent.com/24789156/70380617-06e4d100-18f3-11ea-9111-4398ed0e865c.png)

## Contributing
Pull requests are welcome. 

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
