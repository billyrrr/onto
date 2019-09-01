import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flask_boiler",
    # Alpha release
    version="0.0.1a3",
    author="Bill Rao",
    author_email="billrao@me.com",
    description="Build flask project with Firebase ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/billyrrr/flask-boiler",
    download_url="https://github.com/billyrrr/flask-boiler/archive/v0.0.1a3"
                 ".tar.gz",
    keywords=["firebase", "firestore", "ORM", "flasgger", "flask",
              "backend", "nosql"],
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',

        "Programming Language :: Python :: 3",

        "License :: OSI Approved :: MIT License",

        "Operating System :: OS Independent",
    ],
    install_requires=[
        'Flask>=0.10',
        'google-auth==1.5.1',
        'google-cloud-datastore>=1.4.0',
        'google-api-python-client',
        'firebase-admin',
        'flask_restful',
        # TODO: add version constraint
        'marshmallow',
        "inflection",
        "apispec>=2.0.2",
        "flasgger"
    ],
)
