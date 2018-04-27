import os
from astropy.io import fits as pf
from jwst.straylight.straylight_step import StraylightStep

from ..helpers import add_suffix

BIGDATA = os.environ['TEST_BIGDATA']

def test_straylight1_miri():
    """

    Regression test of straylight performed on MIRI IFUSHORT data.

    """
    output_file_base, output_file = add_suffix('straylight1_output.fits', 'straylight')

    try:
        os.remove(output_file)
    except:
        pass

    StraylightStep.call(BIGDATA+'/miri/test_straylight/jw80500018001_02101_00002_MIRIFUSHORT_flatfield.fits',
                      config_file='straylight.cfg',
                      output_file=output_file_base
    )
    h = pf.open(output_file)
    href = pf.open(BIGDATA+'/miri/test_straylight/jw80500018001_02101_00002_MIRIFUSHORT_straylight.fits')
    newh = pf.HDUList([h['primary'],h['sci'],h['err'],h['dq']])
    newhref = pf.HDUList([href['primary'],href['sci'],href['err'],href['dq']])
    result = pf.diff.FITSDiff(newh,
                              newhref,
                              ignore_keywords = ['DATE','CAL_VER','CAL_VCS','CRDS_VER','CRDS_CTX'],
                              rtol = 0.00001
    )
    result.report()
    try:
        assert result.identical == True
    except AssertionError as e:
        print(result.report())
        raise AssertionError(e)
