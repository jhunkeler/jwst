import os
import pytest
from astropy.io import fits as pf
from jwst.emission.emission_step import EmissionStep

from ..helpers import add_suffix

pytestmark = [
    pytest.mark.usefixtures('_jail'),
    pytest.mark.skipif(not pytest.config.getoption('bigdata'),
                       reason='requires --bigdata')
]

def test_emission_miri():
    """

    Regression test of emission step performed on calibrated miri data.

    """
    output_file_base, output_file = add_suffix('emission1_output.fits', 'emission')

    try:
        os.remove(output_file)
    except:
        pass



    EmissionStep.call(_bigdata+'/miri/test_emission/jw00001001001_01101_00001_MIRIMAGE_flat_field.fits',
                         output_file=output_file_base
    )
    h = pf.open(output_file)
    href = pf.open(_bigdata+'/miri/test_emission/jw00001001001_01101_00001_MIRIMAGE_emission.fits')
    newh = pf.HDUList([h['primary'],h['sci'],h['err'],h['dq']])
    newhref = pf.HDUList([href['primary'],href['sci'],href['err'],href['dq']])
    result = pf.diff.FITSDiff(newh,
                              newhref,
                              ignore_keywords = ['DATE','CAL_VER','CAL_VCS','CRDS_VER','CRDS_CTX'],
                              rtol = 0.00001
    )
    assert result.identical, result.report()
