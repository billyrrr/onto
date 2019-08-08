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

#
# # Original Firebase set-up certs
#


config = None  # TODO: implement 


class Context:
    firebaseApp: firebase_admin.App = None
    db: firestore.Client = None
    debug = None
    testing = None
    _cred = None
    __instance = None

    def __init__(self, *args, **kwargs):
        raise NotImplementedError('Do not initialize this class, use the class methods and properties instead. ')

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Context, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    @classmethod
    def read(cls):
        """ Description
            Read config file andd reload firebase app and firestore client.

            # TODO read config from *.ini file (not provided yet)

        :type cls:
        :param cls:

        :raises:

        :rtype:
        """
        cls._reload_debug_flag(config.DEBUG)
        cls._reload_testing_flag(config.TESTING)
        cls._reload_firebase_app(config.FIREBASE_CERTIFICATE_JSON_PATH)
        cls._reload_firestore_client(config.FIREBASE_CERTIFICATE_JSON_PATH)
        return cls

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
    def _reload_firebase_app(cls, certificatePath):

        try:
            cls._cred = credentials.Certificate(certificatePath)
        except ValueError as e:
            logging.exception('Error initializing credentials.Certificate')
        # TODO delete certificate path in function call

        try:
            cls.firebaseApp = firebase_admin.initialize_app(credential=cls._cred, name=config.APP_NAME)
        except ValueError as e:
            logging.exception('Error initializing firebaseApp')

    @classmethod
    def _reload_firestore_client(cls, credPath):
        try:
            cls.db = firestore.Client.from_service_account_json(credPath)
        except ValueError as e:
            logging.exception('Error initializing firestore client from cls.firebaseApp')
