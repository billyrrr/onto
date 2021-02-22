# Architecture with Flink

## Overview 
Flink Stateful Functions manage the lifecycle of an instantiated object (a domain model), 
and keep tracks of its internal states. A domain model has public attribute getters, 
and these values are committed to Flink Table API once the instance has been modified. 
A domain model has dynamic public attribute getters, which are evaluated with Flink 
Table API. A domain model has public methods, which are invoked in Flink Stateful 
Functions. 

Single Source of Truth: internal state of an object 


## Domain Model
### Internal State 
Internal state should be contained in the Attribute Store, and are serialized 
and deserialized when an object is instantiated or saved. Objects are 
bijective to (doc_id, internal state). 

### Public Property
    public property := f(*<internal state>, *<public property>)

```python
@riders.getter
def riders(self):
    return self._store.riders
```

Public property should only access 

### Dynamic Property
    dynamic property := f(
        *<public property of self>, 
        *<public property of other objects>, 
        *<dynamic property>
    )

```python
@num_riders.getter
def num_riders(self):
    return len(self.riders)
```

### Method
Method accesses internal state. Dynamic property can be "conjured" but may 
produced a different value as when evaluated with Flink. 

Side effect is allowed. 

```python

def add_rider(self, rider: Rider):
  self._store.riders.add(rider)

```

TODO: define when preconditions should be checked. 

Either when Form is built or when a method is executed. 

TODO: Shared mutable state? How to keep track of 
pointers and back references. 
Go with encapsulation principle. Each function 
maintains its own state. 
Eg. assign twice for a bi-directed edge 


### Antipattern (until there is a better way) 
- public read methods



