# Features

Here are some reasons for choosing `flask-boiler` over the protocols 
and frameworks it is employing. 

### Native to Distributed Systems

#### Load Balancing 

`flask-boiler` is designed to run on clusters such as `kubernetes`. By 
limiting the source range, you may route an event to its dedicated pod  
which, for example, may already hold the states it requires. 

#### Consistency 

`flask-boiler` has timepoint check built into the system. You may avoid 
overwriting earlier changes made by other nodes by setting conditions on the sink. 

### Exchangable Components  

#### Ease of Change
As your requirements evolve, for example, you may have a new group of 
        users that uses your service less frequently. It would cause unnecessary 
        amount of space to render and store MeetingSession. You may make minimal 
        modifications to change the sink of the operation from NoSQL datastore to 
        websocket, for example, a MeetingSession ViewModel is only 
        refreshed when the user is active, and release space when the user logs out. 
        The client can communicate with the server via WebSocket. 

#### Abundance of Options
You may write different source/sink classes when you switch the database or services. 

#### Scalability 
As your requirements evolve, you may need a higher throughput, and flask-boiler's 
worker-queue based on multi-threading, and "pull every dependent for every push" 
may induce a higher cost. In this case, you can declare a mediator to be hosted 
as a Flink UDF (User Defined Function), and Flink will handle the invocation and logics 
for triggering. `flask-boiler` will compile/transform your code to be runnable as UDF. 

### Object-Oriented Code

#### Type hinting
- Write queries more easily and more accurately 
- Refactor more easily 

#### Easy to see the overall picture 
The code to write with `flask-boiler` reflects the use case better. You may 
obtain inspirations on your business, since classes are domain-driven. 

#### Better than Functional Reactive Programming (FRP)
If FRP is buttom-up, then `flask-boiler` is relatively top-down. 

Example: suppose that you want to make an object MeetingSession View which 
        requires an update to the number of people attending the meeting whenever 
        a user changes their Ticket. Functional reactive programming 
        would require you to modify an order when this happens. With `flask-boiler`, 
        you would write how MeetingSession is composed of individual Tickets, and 
        write logic on the side of MeetingSession. 

### N+1 Considerations
Consider the documents involved in a building a domain model or view model as a 
graph. We want to retrieve relevant documents when making an evaluation. This 
may lead to `N+1 problem` if not handled properly. We already know that most NoSQL 
usually does not support server-side join, or subqueries, so it is natural to 
fetch the dependent nodes (documents) to local storage. Even though this 
framework does all the fetching for you, you may still want to limit the reference 
between your data. For example, you want to avoid fetching every User document in 
your database when your User document has Friend's, and each User in Friend contains 
other User's. Beware that built-in verifications or warning systems have been 
implemented yet, but it is planned in the future. 

#### Shallow Reference
We want to limit the Tree Height of the said graph. Make sure that your models 
reference up to finitely many layers (and fewer layers when applicable). 


### Product Roadmap

#### Future

Support SQL (Maybe)

Support Flink Stateful Functions

Support Flink:
We want to offer a higher level of abstraction to Flink, 
rather than defining Schema's and operations with a pipelined API, 
we can define DomainModel's and ViewModel's that are object oriented. 
- Statically compile mediator functions to flink operators 
- Dynamically compile mediator functions to flink UDF  
- Statically compile "Store" attrs and adapt to flink (use ast) 
