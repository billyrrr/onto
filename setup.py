import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flask_boiler",
    # Beta release
    version="0.0.2dev18",
    author="Bill Rao",
    author_email="billrao@me.com",
    description="Build reactive back end with ease ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/billyrrr/flask-boiler",
    keywords=["firebase", "firestore", "ORM", "flasgger", "flask",
              "backend", "nosql", "reactive", "framework"],
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',

        'Programming Language :: Python :: 3.7',

        'Programming Language :: Python :: 3.8',

        "License :: OSI Approved :: MIT License",

        "Operating System :: OS Independent",
    ],
    install_requires=[
        'Flask>=0.10',
        # 'google-auth',
        ' google-cloud-firestore',
        'google-cloud-datastore',
        'grpcio==1.30.0',
        # 'google-api-core==1.18.0',
        'google-api-python-client',
        'firebase-admin',
        'flask_restful',
        # TODO: add version constraint
        'marshmallow',
        "inflection",
        "apispec>=2.0.2",
        "flasgger",
        "dictdiffer",
        "celery",
        "flask-socketio",
        "iso8601",
        "pyyaml",
        "google-cloud-logging",
        # "functions-framework",
        # "google-cloud-resource-manager",
        "gitpython",
        "ProxyTypes"
    ],
    # entry_points = {
    #     'console_scripts': ['flask-boiler=scripts.deploy:deploy_all'],
    # }
)
