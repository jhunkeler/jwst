import os
from astropy.io import fits as pf
from jwst.linearity.linearity_step import LinearityStep

from ..helpers import add_suffix

BIGDATA = os.environ['TEST_BIGDATA']

def test_linearity_nircam():
    """

    Regression test of linearity step performed on NIRCam data.

    """
    output_file_base, output_file = add_suffix('linearity1_output.fits', 'linearity')

    try:
        os.remove(output_file)
    except:
        pass



    LinearityStep.call(BIGDATA+'/nircam/test_linearity/jw00017001001_01101_00001_NRCA1_dark_current.fits',
                      config_file='linearity.cfg',
                      output_file=output_file_base
    )
    h = pf.open(output_file)
    href = pf.open(BIGDATA+'/nircam/test_linearity/jw00017001001_01101_00001_NRCA1_linearity.fits')
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
