import os
import pytest
from astropy.io import fits as pf
from jwst.imprint.imprint_step import ImprintStep

from ..helpers import add_suffix

pytestmark = [
    pytest.mark.usefixtures('_jail'),
    pytest.mark.skipif(not pytest.config.getoption('bigdata'),
                       reason='requires --bigdata')
]


def test_imprint_nirspec(_bigdata):
    """

    Regression test of imprint step performed on NIRSpec MSA data.

    """
    output_file_base, output_file = add_suffix('imprint1_output.fits', 'imprint')

    try:
        os.remove(output_file)
    except:
        pass


    ImprintStep.call(BIGDATA+'/nirspec/test_imprint/jw00038001001_01101_00001_NRS1_rate.fits',
                     _bigdata+'/nirspec/test_imprint/NRSMOS-MODEL-21_NRS1_rate.fits',
                     output_file=output_file_base)

    h = pf.open(output_file)
    href = pf.open(_bigdata+'/nirspec/test_imprint/jw00038001001_01101_00001_NRS1_imprint.fits')
    newh = pf.HDUList([h['primary'],h['sci'],h['err'],h['dq']])
    newhref = pf.HDUList([href['primary'],href['sci'],href['err'],href['dq']])

    result = pf.diff.FITSDiff(newh, newhref,
                              ignore_keywords = ['DATE','CAL_VER','CAL_VCS','CRDS_VER','CRDS_CTX'],
                              rtol = 0.00001)
    assert result.identical, result.report()
