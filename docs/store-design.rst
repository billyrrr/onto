Design of Store
===================================

Store manages the dependency of an instance of a class. For example,
Store may be used to retrieve under one transaction all database documents
referenced with attrs.relation in a domain model.

Realtime Retrieval Logics
########

1. Push root document to stack
2. While stack is not empty:
    i) Pop a reference R_k from stack
    ii) Attach a listener to the document D_k referenced with target_id T_k
    iii) Wait for k to be consistent
    iv) Push to stack relations referenced by document; mark relations as visited
3. When stack is empty:
    i) Return a copy of all documents (Emit)

Coroutine:
- When Listener notifies target Tk has changed:
    - Reload tree with root Tk
    - Emit
