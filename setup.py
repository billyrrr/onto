import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flask_boiler",
    version="0.0.1",
    author="Bill Rao",
    author_email="billrao@me.com",
    description="Build flask project with Firebase ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'Flask>=0.10',
        'google-auth==1.5.1',
        'google-cloud-datastore',
        'google-api-python-client',
        'firebase-admin',
        'flask_restful'
    ],
)