"""Project default for pytest"""
import os
import pytest
import re
import requests

from astropy.tests.plugins.display import PYTEST_HEADER_MODULES
from astropy.tests.helper import enable_deprecations_as_exceptions

# Uncomment the following line to treat all DeprecationWarnings as exceptions
enable_deprecations_as_exceptions()

try:
    PYTEST_HEADER_MODULES['Astropy'] = 'astropy'
    PYTEST_HEADER_MODULES['asdf'] = 'asdf'
    del PYTEST_HEADER_MODULES['h5py']
except (NameError, KeyError):
    pass

pytest_plugins = [
    'asdf.tests.schema_tester'
]

RE_URL = re.compile('\w+://\S+')

BIGDATA_PATHS = [
    os.environ.get('TEST_BIGDATA', '/data4/jwst_test_data'),
    'https://bytesalad.stsci.edu/artifactory/jwst-pipeline'
]


# Add option to run slow tests
def pytest_addoption(parser):
    parser.addoption(
        "--runslow",
        action="store_true",
        help="run slow tests"
    )
    parser.addoption('--bigdata',
                     action='store_true',
                     help='Use big local datasets')


def check_url(url):
    """ Determine if `url` can be resolved without error
    """
    if RE_URL.match(url) is None:
        return False

    r = requests.head(url, allow_redirects=True)
    if r.status_code >= 400:
        return False
    return True


class BigdataError(Exception):
    pass


@pytest.fixture
def _bigdata():
    """ Return base path to large data sets
    """

    for root in BIGDATA_PATHS:
        if os.path.exists(root) or check_url(root):
            return root

    raise BigdataError('Data files are not available.')


@pytest.fixture(scope='function')
def _jail(tmpdir):
    """ Execute a test inside of new temporary directory

    Note: Passing `--basetemp=/some/path` to `pytest` will change the default
          temporary storage location. (default: /tmp)
    """
    os.chdir(tmpdir.strpath)
    yield
