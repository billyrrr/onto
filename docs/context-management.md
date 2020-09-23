# Context Management 


## Auto Configuration with boiler.yaml

Provide authentication credentials to flask-boiler by moving the json certificate file 
to your project directory and specify the path in ```boiler.yaml``` 
in your current working directory. 

```yaml
app_name: "<Your Firebase App Name>"
debug: True
testing: True
certificate_filename: "<File Name of Certificate JSON>"
```

In ```__init__``` of your project source root: 
```python
from onto.context import Context as CTX

CTX.load()
```

## Manual Configuration 
In `__init__` of your project source root:
```python
import os

from onto import context
from onto import config

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
from onto import context

CTX = context.Context

# Retrieves firestore database instance 
CTX.db

# Retrieves firebase app instance 
CTX.firebase_app

```

