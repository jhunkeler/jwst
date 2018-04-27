import os
from astropy.io import fits as pf
from jwst.refpix.refpix_step import RefPixStep

from ..helpers import add_suffix

BIGDATA = os.environ['TEST_BIGDATA']

def test_refpixt_nircam():
    """

    Regression test of refpix step performed on NIRCam data.

    """
    output_file_base, output_file = add_suffix('refpix1_output.fits', 'refpix')

    try:
        os.remove(output_file)
    except:
        pass



    RefPixStep.call(BIGDATA+'/nircam/test_bias_drift/jw00017001001_01101_00001_NRCA1_dq_init.fits',
                    odd_even_columns=True, use_side_ref_pixels=False, side_smoothing_length=10,
                    side_gain=1.0, output_file=output_file_base
                    )
    h = pf.open(output_file)
    href = pf.open(BIGDATA+'/nircam/test_bias_drift/jw00017001001_01101_00001_NRCA1_bias_drift.fits')
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
