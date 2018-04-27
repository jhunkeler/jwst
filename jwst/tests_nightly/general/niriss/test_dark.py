import os
from astropy.io import fits as pf
from jwst.dark_current.dark_current_step import DarkCurrentStep

from ..helpers import add_suffix

BIGDATA = os.environ['TEST_BIGDATA']

def test_dark_current_niriss():
    """

    Regression test of dark current step performed on NIRISS data.

    """
    output_file_base, output_file = add_suffix('darkcurrent1_output.fits', 'dark_current')

    try:
        os.remove(output_file)
    except:
        pass

    DarkCurrentStep.call(BIGDATA+'/niriss/test_dark_step/jw00034001001_01101_00001_NIRISS_saturation.fits',
                         config_file='dark_current.cfg',
                         output_file=output_file_base
                         )
    h = pf.open(output_file)
    href = pf.open(BIGDATA+'/niriss/test_dark_step/jw00034001001_01101_00001_NIRISS_dark_current.fits')
    newh = pf.HDUList([h['primary'],h['sci'],h['err'],h['pixeldq'],h['groupdq']])
    newhref = pf.HDUList([href['primary'],href['sci'],href['err'],href['pixeldq'],href['groupdq']])
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
