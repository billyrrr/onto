# flask-boiler

Flask-boiler helps you build fast-prototype of your backend. 

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
have to do is to enable relative services on Google Cloud 
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



