.. _context-management:

Context Management
==================

In ```__init__``` of your project source root:

.. code-block:: python

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

Note that initializing ```Config``` with ```certificate_path``` is unstable and
may be changed later.

In your project code,

.. code-block:: python

    from flask_boiler import context

    CTX = context.Context

    # Retrieves firestore database instance
    CTX.db

    # Retrieves firebase app instance
    CTX.firebase_app
