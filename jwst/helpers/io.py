import os
import re
import requests
import shutil


BIGDATA_PATHS = [
    os.environ.get('TEST_BIGDATA', '/data4/jwst_test_data'),
    'https://bytesalad.stsci.edu/artifactory/jwst-pipeline'
]

RE_URL = re.compile('\w+://\S+')


class BigdataError(Exception):
    pass


def abspath(filepath):
    """Get the absolute file path"""
    return os.path.abspath(os.path.expanduser(os.path.expandvars(filepath)))


def check_url(url):
    """ Determine if `url` can be resolved without error
    """
    if RE_URL.match(url) is None:
        return False

    r = requests.head(url, allow_redirects=True)
    if r.status_code >= 400:
        return False
    return True


def _download(url, dest):
    dest = os.path.abspath(dest)

    with requests.get(url, stream=True) as r:
        with open(dest, 'w+b') as data:
            for chunk in r.iter_content(chunk_size=0x4000):
                data.write(chunk)

    return dest


def _select_bigdata():
    """ Find and returns the path to the nearest big datasets
    """
    for path in BIGDATA_PATHS:
        if os.path.exists(path) or check_url(path):
            return path

    return None


def get_bigdata(*args):
    """ Acquire requested data from a managed resource

    Usage:
        filename = get_bigdata('abc', '123', 'sample.fits')
        with open(filename, 'rb') as data:
            example = data.read()

    Returns:
        Absolute path to local copy of data (i.e. /path/to/example.fits)
    """

    src = os.path.join(_select_bigdata(), *args)
    filename = os.path.basename(src)
    dest = os.path.abspath(os.path.join(os.curdir, filename))

    if os.path.exists(src):
        if src == dest:
            raise BigdataError('Source and destination paths are identical: '
                               '{}'.format(src))
        shutil.copy2(src, dest)

    elif check_url(src):
        _download(src, dest)

    else:
        raise BigdataError('Failed to retrieve data: {}'.format(src))

    return dest
