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
import os

# from google.cloud import storage

# This import is intended to be accessed with google.cloud.logging.*


import logging

from contextvars import ContextVar
from onto.database import Database, Listener

_transaction_var: ContextVar['firestore.Transaction'] = \
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

    # from onto.config import Config

    debug = None
    firebase_app: 'firebase_admin.App' = None
    db: Database = None
    config = None
    # celery_app: Celery = None
    logger: logging.Logger = None
    listener: Listener = None

    transaction_var = _transaction_var

    # Deleted on purpose to ensure that .<flag> is not evaluated as False
    #   when .<flag> is neither set to True, nor set to False.
    # debug = None
    # testing = None
    # _cred = None
    __instance = None

    _ready = False
    """
    _ready is True when Context is loaded (and/or is read) 
    """

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
    def _enable_logging(cls, output_level=logging.DEBUG, output_choice=None,
                        certificate_path=None):
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
            import google.cloud.logging
            logging_client = google.cloud.logging.Client.from_service_account_json(
                json_credentials_path=certificate_path
            )
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
    def load(cls) -> None:
        from onto.config import Config
        config = Config.load()
        cls.read(config)

    @classmethod
    def read(cls, config) -> None:
        """ Description
            Read config file andd reload firebase app and firestore client.

        NOTE: ordering of cls._reload_* methods is important

        :type cls:
        :param cls:

        :raises:

        :rtype:
        """
        # if cls.config == config:
        #     """
        #     Skip reading config if the current config is the same as
        #         the config to read.
        #     """
        #     return cls
        if cls._ready:
            """ Only allow one read/load 
            """
            import warnings
            warnings.warn('Config is read more than once ')
        cls.config = config

        # """
        # TODO: NOTE that PROXY is used here
        # Best be replaced for Safety reasons
        # ATTENTION:
        # """
        # os.environ["HTTP_PROXY"] = "https://34.85.42.121:8899"
        # os.environ["HTTPS_PROXY"] = "https://34.85.42.121:8899"

        """
        Configure logger to output to sys-logger during test 
        and gcloud-logger during staging and etc 
        """
        cls._reload_logger()
        if cls.config.TESTING:
            cls._enable_logging(output_level=logging.DEBUG,
                                output_choice='sys-logger')
        else:
            cls._enable_logging(output_choice='gcloud-logger',
                                certificate_path=cls.config.FIREBASE_CERTIFICATE_JSON_PATH)

        cls._reload_debug_flag(cls.config.DEBUG)
        cls._reload_testing_flag(cls.config.TESTING)
        cls._reload_dbs(cls.config.database)
        default_db_name = cls.config.default_database
        cls._reload_default_db(db_name=default_db_name)
        cls._reload_services(cls.config.services)  # leancloud.engine depends on db

        cls.logger.info(f"onto.Context has finished "
                        f"loading config: {vars(config)}")
        cls._ready = True

    @classmethod
    def _reload_services(cls, services: dict):
        class Services:
            pass

        cls.services = Services()
        for svc_name, svc_config in services.items():
            svc = cls.create_service(svc_config)
            setattr(cls.services, svc_name, svc)

    @classmethod
    def _reload_dbs(cls, database: dict):
        class Dbs:
            pass

        cls.dbs = Dbs()
        for db_name, db_config in database.items():
            db = cls.create_db(db_config)
            setattr(cls.dbs, db_name, db)

    @classmethod
    def _reload_default_db(cls, db_name=None):
        if db_name is not None:
            db = getattr(cls.dbs, db_name)
            setattr(cls, 'db', db)

    @staticmethod
    def create_db(db_config):
        print(db_config)
        if db_config['type'] == "couch":
            server = db_config['server']
            try:
                import couchdb
            except ImportError as e:
                raise TypeError('couchdb server is configured, but '
                                'importing couchdb module has failed') from e
            return couchdb.Server(server)
        elif db_config['type'] == 'couchbase':
            try:
                from couchbase.cluster import Cluster, ClusterOptions
                from couchbase_core.cluster import PasswordAuthenticator
            except ImportError as e:
                raise TypeError('couchbase server is configured, but '
                                'importing couchbase module has failed') from e

            cluster = Cluster(db_config['cluster'], ClusterOptions(
                PasswordAuthenticator(
                    db_config['username'], db_config['password']
                )
            ))
            bucket = cluster.bucket(db_config['bucket'])
            return bucket
        elif db_config['type'] == 'firestore':
            caller_module_path = os.path.curdir
            cert_path = os.path.join(
                caller_module_path, db_config['certificate_path']
            )
            # import requests
            # px = {
            #     'http': "35.189.144.254:3128",
            #     'https': "35.189.144.254:3128"
            # }
            # session = requests.Session()
            # session.proxies = px
            def _ua():
                import pkg_resources
                version = pkg_resources.get_distribution("onto").version
                return f'onto/{version}'
            def _client_info():
                import google.api_core.gapic_v1.client_info
                import pkg_resources
                _GAPIC_LIBRARY_VERSION = pkg_resources.get_distribution(
                    "google-cloud-firestore"
                ).version
                return google.api_core.gapic_v1.client_info.ClientInfo(
                    gapic_version=_GAPIC_LIBRARY_VERSION,
                    user_agent=_ua()
                )

            from google.cloud import firestore
            client = firestore.Client.from_service_account_json(
                cert_path, client_info=_client_info())
            from onto.database.firestore import FirestoreDatabase
            FirestoreDatabase.firestore_client = client
            return FirestoreDatabase
        elif db_config['type'] == 'leancloud':
            try:
                import leancloud
            except ImportError as e:
                raise TypeError('leancloud server is configured, but '
                                'importing leancloud module has failed') from e
            if 'app_id' in db_config and 'master_key' in db_config:
                """
                Allow empty init for Leancloud engine uses 
                """
                leancloud.init(
                    app_id=db_config['app_id'],
                    master_key=db_config['master_key']
                )
            else:
                import leancloud

                APP_ID = os.environ['LEANCLOUD_APP_ID']
                APP_KEY = os.environ['LEANCLOUD_APP_KEY']
                MASTER_KEY = os.environ['LEANCLOUD_APP_MASTER_KEY']

                leancloud.init(APP_ID, app_key=APP_KEY, master_key=MASTER_KEY)
                # 如果需要使用 master key 权限访问 LeanCLoud 服务，请将这里设置为 True
                leancloud.use_master_key(False)

            from onto.database.leancloud import LeancloudDatabase
            return LeancloudDatabase
        elif db_config['type'] == 'kafka':
            try:
                bootstrap_servers = db_config['bootstrap_servers']
                from onto.database.kafka import KafkaDatabase
                KafkaDatabase.bootstrap_servers = bootstrap_servers
                return KafkaDatabase
            except ImportError as e:
                raise TypeError('kafka is configured, but '
                                'importing kafka module has failed') from e
        elif db_config['type'] == 'pony':
            try:
                from pony.orm import Database
                db = Database()
                from pony.orm.dbproviders.sqlite import SQLiteProvider
                db.bind(SQLiteProvider, filename=':memory:', create_db=True)
                return db
            except ImportError as e:
                raise TypeError('pony is configured, but '
                                'importing pony module has failed') from e
        elif db_config['type'] == 'mock':
            from onto.database.mock import MockDatabase
            return MockDatabase
        else:
            raise ValueError

    @classmethod
    def create_service(cls, svc_config):
        service_type = svc_config['type']
        if service_type == 'engine':
            try:
                import leancloud
            except ImportError as e:
                raise TypeError('leancloud server is configured, but '
                                'importing leancloud module has failed') from e
            engine = leancloud.Engine()
            return engine
        elif service_type == 'firebase':
            try:
                import firebase_admin
                app_name = svc_config['app_name']
                storage_bucket_name = svc_config.get('storage_bucket_name', None)
                if storage_bucket_name is None:
                    storage_bucket_name = f"{app_name}.appspot.com"

                cred = cls._get_credentials(svc_config['certificate_filename'])
                return firebase_admin.initialize_app(
                    credential=cred,
                    name=app_name,
                    options={
                        'storageBucket': storage_bucket_name
                    }
                )
            except Exception as e:
                logging.exception('Error initializing firebase_app')
                raise e
        elif service_type == 'celery':
            from celery import Celery
            celery_app = Celery('tasks',
                                    broker='pyamqp://guest@localhost//')
            return celery_app
        elif service_type == 'authing':
            user_pool_id = svc_config['user_pool_id']
            secret = svc_config['secret']  # TODO: isolate side effect of assignment
            from authing import Authing
            authing = Authing({
                "userPoolId": user_pool_id,
                "secret": secret,
            })
            return authing
        else:
            raise ValueError

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
    def _get_credentials(cls, certificate_path):
        try:
            from firebase_admin import credentials
            _cred = credentials.Certificate(certificate_path)
            return _cred
        except Exception as e:
            logging.exception('Error initializing credentials.Certificate')
            raise e
        # TODO delete certificate path in function call
