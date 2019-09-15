.. _firestore-orm:

Migrate from google.cloud.firestore
===================================

This document compares google-cloud-python-client
firestore client library with flask-boiler ORM.

Add data
########

It allows you to replace,

.. code-block:: python

    doc_ref = db.collection(u'users').document(u'alovelace')
    doc_ref.set({
        u'first': u'Ada',
        u'last': u'Lovelace',
        u'born': 1815
    })

with this,

.. code-block:: python

    user = User.create(doc_id="alovelace")
    user.first = 'Ada'
    user.last = 'Lovelace'
    user.born = "1815"
    user.save()

(Extra steps required to declare model. See quickstart for details.)

Read data
#########

It allows you to replace,

.. code-block:: python

    users_ref = db.collection(u'users')
    docs = users_ref.stream()

    for doc in docs:
        print(u'{} => {}'.format(doc.id, doc.to_dict()))

with this,

.. code-block:: python

    for user in User.all():
        print(user.to_dict())


Save data
#########

It allows you to replace,

.. code-block:: python

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

with this,

.. code-block:: python

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

(fieldname kwarg in ClsFactory to be implemented soon)

Get data
########

It allows you to replace,

.. code-block:: python

    doc_ref = db.collection(u'cities').document(u'SF')

    try:
        doc = doc_ref.get()
        print(u'Document data: {}'.format(doc.to_dict()))
    except google.cloud.exceptions.NotFound:
        print(u'No such document!')

with this,

.. code-block:: python

    sf = City.get(doc_id='SF')
    if sf is not None:  # To be implemented soon
        print(u'Document data: {}'.format(doc.to_dict()))
    else:
        print("No such document")


Simple queries
##############

It allows you to replace,

.. code-block:: python

    docs = db.collection(u'cities').where(u'capital', u'==', True).stream()

    for doc in docs:
        print(u'{} => {}'.format(doc.id, doc.to_dict()))

with this,

.. code-block:: python

    for city in City.where(capital=True):
        print(city.to_dict())


Query operators
###############

It allows you to replace,

.. code-block:: python

    cities_ref = db.collection(u'cities')

    cities_ref.where(u'state', u'==', u'CA')
    cities_ref.where(u'population', u'<', 1000000)
    cities_ref.where(u'name', u'>=', u'San Francisco'

with this,

.. code-block:: python

    City.where(state="CA")
    City.where(population=('<', 1000000))
    City.where(name=('>=', "San Francisco"))

Field name conversion
#####################

Sometimes, you want to have object attributes in "snake_case" and
Firestore Document field name in "camelCase". This is by default for
flask-boiler. You may customize this conversion also.

Consider this example,

.. code-block:: python

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


object ``la`` saves to a document in firestore with "camelCase" field names,

.. code-block:: python

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


Similarly, you can query the objects with your local object attribute
or firestore field name.

.. code-block:: python

    for obj in City.where(city_state="CA"):
        print(obj.city_name)

Or equivalently

.. code-block:: python

    for obj in City.where("cityState", "==", "CA"):
        print(obj.city_name)
