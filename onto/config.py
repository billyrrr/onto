"""
Author: Zixuan Rao
Reference:
    http://flask.pocoo.org/docs/1.0/config/
    https://medium.freecodecamp.org/structuring-a-flask-restplus-web-service-for-production-builds-c2ec676de563
"""

import os

"""
Reads config from "boiler.yaml" in root directory if unspecified. 
Reads config from FB_CONFIG_FILENAME env var if specified.  
"""
CONFIG_FILENAME_KEY = "FB_CONFIG_FILENAME"
DEFAULT_CONFIG_FILENAME = "boiler.yaml"

caller_module_path = os.path.curdir
config_jsons_path = os.path.join(caller_module_path, "config_jsons")


class ConfigBase:
    """
    TESTING: (authenticate decorator will return uid as the value of header["Authentication"])
        Enable testing mode. Exceptions are propagated rather than handled by the the app’s error handlers.
        Extensions may also change their behavior to facilitate easier testing.
        You should enable this in your own tests.
    DEBUG:
        Whether debug mode is enabled.
        When using flask run to start the development server, an interactive debugger will be shown for unhandled
        exceptions, and the server will be reloaded when code changes. The debug attribute maps to this config key.
        This is enabled when ENV is 'development' and is overridden by the FLASK_DEBUG environment variable.
        It may not behave as expected if set in code.

    Note that this Config currently does not affect (Flask) main.app CONFIG.
    TODO: extend from Flask Config and apply to main.app

    """
    DEBUG: bool = None
    TESTING: bool = None
    FIREBASE_CERTIFICATE_JSON_PATH: str = None
    APP_NAME: str = None
    STORAGE_BUCKET_NAME: str = None

    def __eq__(self, other):
        """
        Comparator for configs to avoid reloading the same config.

        Note: this does not compare all fields

        :param other:
        :return:
        """
        if other is None:
            return False
        else:
            return self.APP_NAME == other.APP_NAME \
                and self.DEBUG == other.DEBUG \
                and self.TESTING == other.TESTING

    def __new__(cls, certificate_filename=None, certificate_path=None,
                testing=False, debug=False,
                app_name=None, storage_bucket_name=None,
                database=None, default_database=None, services=None,
                *args, **kwargs):
        cls.TESTING = testing
        cls.DEBUG = debug
        cls.APP_NAME = app_name

        cls.database = database if database is not None else dict()
        cls.default_database = default_database
        if services is None:
            services = dict()
        cls.services = services
        return cls


class Config(ConfigBase):

    @classmethod
    def _load_from_file(cls, file):
        from yaml import load, dump
        try:
            from yaml import CLoader as Loader, CDumper as Dumper
        except ImportError:
            from yaml import Loader, Dumper
        y = load(file, Loader=Loader)
        return cls(**y)

    @classmethod
    def load(cls):

        import os
        filename = os.getenv(CONFIG_FILENAME_KEY, DEFAULT_CONFIG_FILENAME)

        with open(filename) as file:
            return cls._load_from_file(file)
