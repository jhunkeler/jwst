import os
import pytest

from jwst.helpers.io import get_bigdata


@pytest.mark.usefixtures('_jail')
class TestBigdata:
    _starting_path = os.path.abspath(os.curdir)

    @pytest.mark.skipif(not pytest.config.getoption('bigdata'),
                       reason='requires --bigdata')
    def test_bigdata(self):
        """ Test ability to retrieve big data from a list of
        predefined resources (defined in jwst.helpers.io).
        """
        filename = get_bigdata('helpers', 'alive', 'alive-0.txt')
        assert os.path.exists(filename)
        assert os.stat(filename).st_size

    def test_jail(self):
        """ Ensures the current working directory has been changed
        """
        assert os.path.abspath(os.curdir) != self._starting_path


