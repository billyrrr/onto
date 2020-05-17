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
from google.cloud import storage
from celery import Celery

from .config import Config
import logging

from contextvars import ContextVar

_transaction_var: ContextVar[firestore.Transaction] = \
    ContextVar('_transaction_var', default=None)


class Context:
    """ Context Singleton for Firestore, Firebase and Celery app.

        Example:


    """

    firebase_app: firebase_admin.App = None
    db: firestore.Client = None
    config: Config = None
    celery_app: Celery = None
    logger: logging.Logger = None

    transaction_var = _transaction_var


    # Deleted on purpose to ensure that .<flag> is not evaluated as False
    #   when .<flag> is neither set to True, nor set to False.
    # debug = None
    # testing = None
    _cred = None
    __instance = None

    def __init__(self, *args, **kwargs):
        raise NotImplementedError('Do not initialize this class, use the class methods and properties instead. ')

    @classmethod
    def _reload_logger(cls):
        cls.logger = logging.getLogger()

    @staticmethod
    def _enable_logging(level=logging.DEBUG):
        import sys

        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        root.addHandler(handler)

    @classmethod
    def load(cls):
        config = Config.load()
        cls.read(config)

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
        if cls.config == config:
            """
            Skip reading config if the current config is the same as 
                the config to read. 
            """
            return cls
        cls.config = config
        cls._reload_logger()
        cls._reload_debug_flag(cls.config.DEBUG)
        cls._reload_testing_flag(cls.config.TESTING)
        cls._reload_firebase_app(cls.config.FIREBASE_CERTIFICATE_JSON_PATH)
        cls._reload_firestore_client(cls.config.FIREBASE_CERTIFICATE_JSON_PATH)
        cls._reload_celery_app()

        if cls.debug:
            cls._enable_logging(logging.DEBUG)
        else:
            cls._enable_logging(logging.ERROR)
        cls.logger.info(f"flask_boiler.Context has finished "
                        f"loading config: {vars(config)}")
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
        except Exception as e:
            logging.exception('Error initializing credentials.Certificate')
            raise e
        # TODO delete certificate path in function call

        try:
            cls.firebase_app = firebase_admin.initialize_app(credential=cls._cred, name=cls.config.APP_NAME, options={
                'storageBucket': cls.config.STORAGE_BUCKET_NAME
            })
        except Exception as e:
            logging.exception('Error initializing firebase_app')
            raise e

    @classmethod
    def _reload_firestore_client(cls, cred_path):
        try:
            cls.db = firestore.Client.from_service_account_json(cred_path)
        except Exception as e:
            logging.exception('Error initializing firestore client from cls.firebase_app')
            raise e
