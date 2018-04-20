import os
import pytest

from jwst.helpers.io import (get_bigdata, _select_bigdata, BigdataError)
from jwst.helpers.mark import require_bigdata
from jwst.helpers.utils import download


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



class TestJailFixture:
    _starting_path = os.path.abspath(os.curdir)

    # _jail fixture is set "autouse=True" in conftest.py
    def test_working_directory(self):
        """ Ensures the current working directory has been changed
        """
        assert os.path.abspath(os.curdir) != self._starting_path
