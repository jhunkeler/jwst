import os
import pytest
from astropy.io import fits
from jwst.helpers import get_bigdata, require_bigdata, cmp_fitshdr
from jwst.rscd.rscd_step import RSCD_Step

from ..helpers import add_suffix


@require_bigdata
def test_rscd_miri2():
    """

    Regression test of RSCD step performed on MIRI data.

    """
    output_file_base, output_file = add_suffix('rscd2_output.fits', 'rscd')

    try:
        os.remove(output_file)
    except:
        pass


    RSCD_Step.call(_bigdata+'/miri/test_rscd/jw80600012001_02101_00003_mirimage_linearity.fits',
                   output_file=output_file_base
                   )
    h = fits.open(output_file)
    href = fits.open(_bigdata+'/miri/test_rscd/jw80600012001_02101_00003_mirimage_rscd.fits')
    newh = fits.HDUList([h['primary'],h['sci'],h['err'],h['pixeldq'],h['groupdq']])
    newhref = fits.HDUList([href['primary'],href['sci'],href['err'],href['pixeldq'],href['groupdq']])
    result = fits.diff.FITSDiff(newh,
                              newhref,
                              ignore_keywords = ['DATE','CAL_VER','CAL_VCS','CRDS_VER','CRDS_CTX'],
                              rtol = 0.00001
    )
    assert result.identical, result.report()
