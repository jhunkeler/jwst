import os
import pytest
import requests

from jwst.helpers.io import (get_bigdata, _select_bigdata, BigdataError)
from jwst.helpers.mark import require_bigdata, remote_data
import jwst.helpers.utils as utils


@require_bigdata
class TestBigdata:
    """ Ensure BIGDATA resources and helper functions are working correctly.
    """
    def test_get_bigdata_arg_multi(self):
        """ Use split path elements
        """
        filename = get_bigdata('helpers', 'alive', 'alive-0.txt')
        assert os.path.exists(filename)
        assert os.stat(filename).st_size

    def test_get_bigdata_arg_single(self):
        """ Use single long path
        """
        filename = get_bigdata('helpers/alive/alive-0.txt')
        assert os.path.exists(filename)
        assert os.stat(filename).st_size

    def test_get_bigdata_raises_BigdataError(self):
        with pytest.raises(BigdataError):
            get_bigdata('THI5', 'PR0B4BLY', 'D03S', 'N0T', '3X15T')


class TestGenericUtils:
    @remote_data
    def test_download(self):
        output = os.path.join(os.path.abspath(os.curdir), 'index.html')
        filename = utils.download('http://www.stsci.edu/index.html', output)
        assert os.path.exists(filename)
        assert os.stat(filename).st_size

    def test_download_failure(self):
        output = os.path.join(os.path.abspath(os.curdir), 'index.html')
        with pytest.raises(requests.exceptions.ConnectionError):
            utils.download('http://localhostunlikely/null/index.html', output)


class TestJailFixture:
    _starting_path = os.path.abspath(os.curdir)

    # _jail fixture is set "autouse=True" in conftest.py
    def test_working_directory(self):
        """ Ensures the current working directory has been changed
        """
        assert os.path.abspath(os.curdir) != self._starting_path
