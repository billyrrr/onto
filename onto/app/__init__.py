"""
We want a singleton instance that routes all requests and triggers including
    WebSocket, NoSQL change stream, cloud function triggers,
    HTTP request, and RPC.

App instance will keep a event loop, and places handlers on the event loop
    when triggered. We also want it to support job graph, as we may need
    to retract or cancel earlier invocations when new data has come in and
    we need to invoke with the new data in its place.

"""