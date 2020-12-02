#!/usr/bin/env python3
"""Pytest Kafka fixtures."""
import sys
import contextlib
import shutil
import urllib.request
import tarfile
from pathlib import Path



KAFKA_URL = 'https://archive.apache.org/dist/kafka/2.2.0/kafka_2.12-2.2.0.tgz'
KAFKA_TAR = 'kafka.tgz'
KAFKA_TAR_ROOTDIR = 'kafka_2.12-2.2.0'
KAFKA_DIR = 'kafka'


def set_up_kafka():
    """Clean, download Kafka from an official mirror and untar it."""
    clean_kafka()

    print('* Downloading Kafka', file=sys.stderr)
    urllib.request.urlretrieve(KAFKA_URL, KAFKA_TAR)

    print('* Unpacking Kafka', file=sys.stderr)
    with tarfile.open(KAFKA_TAR, 'r') as f:
        f.extractall()

    print('* Renaming:', KAFKA_TAR_ROOTDIR, '→', KAFKA_DIR, file=sys.stderr)
    Path(KAFKA_TAR_ROOTDIR).rename(KAFKA_DIR)
    Path(KAFKA_TAR).unlink()


def clean_kafka():
    """Clean whatever `set_up_kafka` may create."""
    shutil.rmtree(KAFKA_DIR, ignore_errors=True)
    shutil.rmtree(KAFKA_TAR_ROOTDIR, ignore_errors=True)
    with contextlib.suppress(FileNotFoundError):
        Path(KAFKA_TAR).unlink()

if __name__ == "__main__":

    set_up_kafka()
