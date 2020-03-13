"""
Author: Zixuan Rao
Reference: https://github.com/Amsterdam/subsidieservice/blob/master/subsidy_service/subsidy_service/context.py

Usage:
1. In testing or production, initialize Context singleton first by calling config.Context.read() in __init__.py of
    caller package
2. In package (test_data_access as an example) __init__.py, add "import config"
3. In files under the package: CTX = test_data_access.config.Context

"""

import logging

import firebase_admin
from firebase_admin import credentials
from google.cloud import firestore
from celery import Celery

from .config import Config


class Context:
    firebase_app: firebase_admin.App = None
    db: firestore.Client = None
    config: Config = None
    celery_app: Celery = None

    # debug = None
    # testing = None
    _cred = None
    __instance = None

    def __init__(self, *args, **kwargs):
        raise NotImplementedError('Do not initialize this class, use the class methods and properties instead. ')

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Context, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    @staticmethod
    def _enable_logging():
        import sys
        import logging

        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        root.addHandler(handler)

    @classmethod
    def read(cls, config):
        """ Description
            Read config file andd reload firebase app and firestore client.

            # TODO read config from *.ini file (not provided yet)

        :type cls:
        :param cls:

        :raises:

        :rtype:
        """
        cls.config = config
        cls._enable_logging()
        cls._reload_debug_flag(cls.config.DEBUG)
        cls._reload_testing_flag(cls.config.TESTING)
        cls._reload_firebase_app(cls.config.FIREBASE_CERTIFICATE_JSON_PATH)
        cls._reload_firestore_client(cls.config.FIREBASE_CERTIFICATE_JSON_PATH)
        cls._reload_celery_app()
        return cls

    @classmethod
    def _reload_celery_app(cls):
        cls.celery_app = Celery('tasks', broker='pyamqp://guest@localhost//')

    @classmethod
    def _reload_debug_flag(cls, debug):
        cls.debug = debug

    @classmethod
    def _reload_testing_flag(cls, testing):
        """
        When testing is set to True, all authenticate decorators in services returns uid as "testuid1"
        :param testing:
        :return:
        """
        cls.testing = testing

    @classmethod
    def _reload_firebase_app(cls, certificate_path):

        try:
            cls._cred = credentials.Certificate(certificate_path)
        except ValueError as e:
            logging.exception('Error initializing credentials.Certificate')
        # TODO delete certificate path in function call

        try:
            cls.firebase_app = firebase_admin.initialize_app(credential=cls._cred, name=cls.config.APP_NAME)
        except ValueError as e:
            logging.exception('Error initializing firebase_app')

    @classmethod
    def _reload_firestore_client(cls, cred_path):
        try:
            cls.db = firestore.Client.from_service_account_json(cred_path)
        except ValueError as e:
            logging.exception('Error initializing firestore client from cls.firebase_app')
