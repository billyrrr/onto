from onto.context import Context as CTX


from functools import wraps


def run_transaction(func):
    """ Decorator to run a function in transaction. All instances
            of subclasses of FirestoreObject will default to this transaction
            for reading and writing to Firestore.

    :return:
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Set transaction context variable
        transaction = CTX.db.transaction()
        token = CTX.transaction_var.set(transaction)
        from google.cloud import firestore
        @firestore.transactional
        def new_func(transaction: firestore.Transaction):
            return func(*args, **kwargs, transaction=transaction)
        res = new_func(transaction)
        # Reverse transaction context variable
        CTX.transaction_var.reset(token)
        return res
    return wrapper

