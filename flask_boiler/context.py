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
# from google.cloud import storage

# This import is intended to be accessed with google.cloud.logging.*
import google.cloud.logging

from celery import Celery

from .config import Config
import logging

from contextvars import ContextVar

_transaction_var: ContextVar[firestore.Transaction] = \
    ContextVar('_transaction_var', default=None)


class Context:
    """ Context Singleton for Firestore, Firebase and Celery app.
    TODO: consider development behavior inconsistency for different
            values of debug and testing. (Behaviors of context
            may be different in production as compared to that in
            testing)

        Example:

    NOTE: reload should not be called for more than once
    TODO: enforce call reload only once and rename methods starting with reload

    """

    debug = None
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
        """ Loads logger.
        TODO: call Logger.setLevel(...)  with level specified by user
        """
        cls.logger = logging.getLogger()
        cls.logger.setLevel(level=logging.DEBUG)

    # @staticmethod
    # def _logger_type(logger):
    #     if isinstance(logger, google.cloud.logging.logger.Logger):
    #         return 'gcloud-logger'
    #     elif isinstance(logger, logging.Logger):
    #         return 'sys-logger'
    #     else:
    #         raise TypeError

    @classmethod
    def _enable_logging(cls, output_level=logging.DEBUG, output_choice=None):
        """ Set cls.logger to output to standard out.
        NOTE: cls._reload_logger should be called first.
        level applies when output_choice is sys-logger, and does not
            apply to cls.logger

        :param level:
        :return:
        """
        if output_choice == 'sys-logger':
            import sys
            root = cls.logger

            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(output_level)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            root.addHandler(handler)
        elif output_choice == 'gcloud-logger':
            logging_client = google.cloud.logging.Client()
            # "Retrieves a Cloud Logging handler based on the environment
            # you're running in and integrates the handler with the
            # Python logging module. By default this captures all logs
            # at INFO level and higher"
            # ref: gcloud logging docs
            logging_client.get_default_handler()
            logging_client.setup_logging()
        else:
            raise TypeError

    @classmethod
    def load(cls):
        config = Config.load()
        cls.read(config)

    @classmethod
    def read(cls, config):
        """ Description
            Read config file andd reload firebase app and firestore client.

        NOTE: ordering of cls._reload_* methods is important

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

        cls._reload_credentials(cls.config.FIREBASE_CERTIFICATE_JSON_PATH)

        """
        Configure logger to output to sys-logger during test 
        and gcloud-logger during staging and etc 
        """
        cls._reload_logger()
        if cls.config.TESTING:
            cls._enable_logging(output_level=logging.DEBUG,
                                output_choice='sys-logger')
        else:
            cls._enable_logging(output_choice='gcloud-logger')

        cls._reload_debug_flag(cls.config.DEBUG)
        cls._reload_testing_flag(cls.config.TESTING)
        cls._reload_firebase_app()
        cls._reload_firestore_client(
            certificate_path=cls.config.FIREBASE_CERTIFICATE_JSON_PATH)
        cls._reload_celery_app()

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
    def _reload_credentials(cls, certificate_path):
        try:
            cls._cred = credentials.Certificate(certificate_path)
        except Exception as e:
            logging.exception('Error initializing credentials.Certificate')
            raise e
        # TODO delete certificate path in function call

    @classmethod
    def _reload_firebase_app(cls):
        try:
            cls.firebase_app = firebase_admin.initialize_app(
                credential=cls._cred,
                name=cls.config.APP_NAME,
                options={
                'storageBucket': cls.config.STORAGE_BUCKET_NAME
            })
        except Exception as e:
            logging.exception('Error initializing firebase_app')
            raise e

    @classmethod
    def _reload_firestore_client(cls, certificate_path):
        try:
            cls.db = firestore.Client.from_service_account_json(certificate_path)
        except Exception as e:
            logging.exception('Error initializing firestore client from cls.firebase_app')
            raise e
